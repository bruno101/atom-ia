# -*- coding: utf-8 -*-
"""
Elasticsearch search algorithm implementation
"""
import logging
from elasticsearch import Elasticsearch
import spacy
import google.generativeai as genai
import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

nlp = spacy.load("pt_core_news_lg")
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API'))

def _connect_elasticsearch(url):
    """Connect to Elasticsearch and return client"""
    try:
        es = Elasticsearch(url)
        if not es.ping():
            logger.error("Elasticsearch not available")
            return None
        return es
    except Exception as e:
        logger.error(f"Cannot connect to Elasticsearch: {e}")
        return None

def _expand_query_with_gemini(query, max_expansions):
    """Expand query using Gemini-2.0-flash for entity extraction"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        prompt = f"""Extract entities and their name variations from this query for lexical search, ordered by importance:

Query: "{query}"

Return only a comma-separated list of terms (max {max_expansions}), starting with the entities and variations from most to least important. No explanations."""
        
        response = model.generate_content(prompt)
        entities = [query] + [term.strip() for term in response.text.split(',') if term.strip()]
        return entities[:max_expansions + 1] if entities else [query]
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise

def _expand_query_with_nlp(query, max_expansions):
    """Fallback: Expand query using NLP noun phrases"""
    doc = nlp(query)
    seen = set()
    expanded = [query]
    
    for ent in doc.ents:
        key = ent.text.strip().lower()
        if key not in seen and len(expanded) <= max_expansions:
            seen.add(key)
            expanded.append(key)
    
    return expanded

def _expand_query(query, max_expansions):
    """Expand query using Gemini with NLP fallback"""
    start_time = time.time()
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(_expand_query_with_gemini, query, max_expansions)
            expanded = future.result(timeout=10)
            gemini_time = time.time() - start_time
            print(f"Consulta expandida (Gemini) - {gemini_time:.2f}s")
            print(expanded)
            return expanded
    except (TimeoutError, Exception) as e:
        gemini_time = time.time() - start_time
        logger.warning(f"Gemini timeout/error after {gemini_time:.2f}s, using NLP fallback: {e}")
        expanded = _expand_query_with_nlp(query, max_expansions)
        print("Consulta expandida (NLP)")
        print(expanded)
        return expanded

def _build_search_body(query, size, is_main_query=True):
    """Build Elasticsearch search body"""
    if is_main_query:
        query_body = {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query.lower(),
                            "fields": ["text^2", "title^3"],
                            "type": "best_fields",
                            "fuzziness": "AUTO"
                        }
                    },
                    {
                        "multi_match": {
                            "query": query.lower(),
                            "type": "phrase",
                            "slop": 1,
                            "fields": ["text^2", "title^3"],
                            "boost": 5
                        }
                    }
                ]
            }
        }
    else:
        query_body = {
        "match_phrase": {
            "text": query.lower()
        }}
    
    return {
        "query": query_body,
        "size": size,
        "highlight": {
            "fields": {
                "text": {
                    "fragment_size": 300,
                    "number_of_fragments": 3,
                    "pre_tags": ["<em>"],
                    "post_tags": ["</em>"]
                }
            }
        }
    }

def _process_search_hit(hit, is_main_query=True):
    """Process a single search hit into document format"""
    source = hit['_source']
    highlights = hit.get("highlight", {}).get("text", [])
    score = hit['_score'] if is_main_query else hit['_score'] * 0.8
    
    return {
        'text': " ... ".join(highlights) if highlights else source['text'][:300],
        'url': source['url'],
        'title': source['title'],
        'relevance_score': score
    }

def _search_with_fallback(es, query, size, is_main_query=True):
    """Execute search with fallback to simple match"""
    try:
        response = es.search(index="documents_folded", body=_build_search_body(query, size, is_main_query))
        print("Consulta")
        print(query)
        print("Resultado")
        print([_process_search_hit(hit, is_main_query) for hit in response['hits']['hits']][0:2])
        return [_process_search_hit(hit, is_main_query) for hit in response['hits']['hits']]
    except Exception as e:
        logger.error(f"Elasticsearch search error: {e}")
        try:
            simple_search = {"query": {"match": {"text": query.lower()}}, "size": size}
            response = es.search(index="documents_folded", body=simple_search)
            return [_process_search_hit(hit, is_main_query) for hit in response['hits']['hits']]
        except Exception as e2:
            logger.error(f"Fallback search failed: {e2}")
            return []

def _remove_duplicates(documents):
    """Remove duplicate documents based on URL and boost scores for multi-query matches"""
    url_docs = {}
    
    for doc in documents:
        url = doc['url']
        if url not in url_docs:
            url_docs[url] = doc.copy()
            url_docs[url]['match_count'] = 1
        else:
            url_docs[url]['match_count'] += 1
            url_docs[url]['relevance_score'] = max(url_docs[url]['relevance_score'], doc['relevance_score'])
    
    for doc in url_docs.values():
        if doc['match_count'] > 1:
            doc['relevance_score'] *= (1 + 0.3 * (doc['match_count'] - 1))
        del doc['match_count']
    
    return list(url_docs.values())

def search_documents_by_text(queries, n_results_per_query=5, url_elastic_search="localhost:9200", expand=False):
    """Elasticsearch search implementation"""
    if not queries or not isinstance(queries, list):
        return []
    
    es = _connect_elasticsearch(url_elastic_search)
    if not es:
        return []
    
    all_documents = []
    
    for query in queries:
        if not query or not query.strip():
            continue
        
        expanded_queries = _expand_query(query, 2) if expand else [query]
        print("Expandindo consultas")
        print(expand)
        print(expanded_queries)
        results_per_query = n_results_per_query // len(expanded_queries)
        
        for i, expanded in enumerate(expanded_queries):
            size = n_results_per_query - results_per_query * (len(expanded_queries) - 1) if i == 0 else results_per_query
            is_main = i == 0
            documents = _search_with_fallback(es, expanded, size, is_main)
            all_documents.extend(documents)
        
        # Complement with more results from main query if needed
        unique_docs = _remove_duplicates(all_documents)
        if len(unique_docs) < n_results_per_query:
            existing_urls = {doc['url'] for doc in unique_docs}
            additional_size = n_results_per_query * 2  # Get more to account for duplicates
            additional_docs = _search_with_fallback(es, query, additional_size, True)
            for doc in additional_docs:
                if doc['url'] not in existing_urls and len(unique_docs) < n_results_per_query:
                    unique_docs.append(doc)
        
        all_documents = unique_docs
    
    return sorted(all_documents, key=lambda x: x['relevance_score'], reverse=True)
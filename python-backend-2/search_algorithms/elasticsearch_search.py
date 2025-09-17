# -*- coding: utf-8 -*-
"""
Elasticsearch search algorithm implementation
"""
import logging
from elasticsearch import Elasticsearch
import spacy

nlp = spacy.load("pt_core_news_lg")
logger = logging.getLogger(__name__)

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

def _expand_query(query, max_expansions):
    """Expand query using NLP noun phrases"""
    doc = nlp(query)
    seen = set()
    expanded = [query]
    
    for chunk in doc.noun_chunks:
        key = chunk.text.strip().lower()
        if key not in seen and len(expanded) <= max_expansions:
            seen.add(key)
            expanded.append(key)
    
    return expanded

def _build_search_body(query, size):
    """Build Elasticsearch search body"""
    return {
        "query": {
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
        },
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
        response = es.search(index="documents", body=_build_search_body(query, size))
        return [_process_search_hit(hit, is_main_query) for hit in response['hits']['hits']]
    except Exception as e:
        logger.error(f"Elasticsearch search error: {e}")
        try:
            simple_search = {"query": {"match": {"text": query.lower()}}, "size": size}
            response = es.search(index="documents", body=simple_search)
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
        
        expanded_queries = _expand_query(query, n_results_per_query // 2) if expand else [query]
        results_per_query = n_results_per_query // len(expanded_queries)
        
        for i, expanded in enumerate(expanded_queries):
            size = n_results_per_query - results_per_query * (len(expanded_queries) - 1) if i == 0 else results_per_query
            is_main = i == 0
            documents = _search_with_fallback(es, expanded, size, is_main)
            all_documents.extend(documents)
    
    unique_docs = _remove_duplicates(all_documents)
    return sorted(unique_docs, key=lambda x: x['relevance_score'], reverse=True)
# -*- coding: utf-8 -*-
"""
Elasticsearch search algorithm implementation
"""
import logging
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


def search_documents_by_text(queries, n_results_per_query=5,  url_elastic_search="localhost:9200"):
    """Elasticsearch search implementation"""
    if not queries or not isinstance(queries, list):
        return []
    
    try:
        print(url_elastic_search)
        es = Elasticsearch(url_elastic_search)
        if not es.ping():
            logger.error("Elasticsearch not available")
            return []
    except Exception as e:
        logger.error(f"Cannot connect to Elasticsearch: {e}")
        return []
    
    all_documents = []
    
    for query in queries:
        if not query or not query.strip():
            continue
        
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {   # fuzzy / partial matches
                            "multi_match": {
                                "query": query.lower(),
                                "fields": ["text^2", "title^3"],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        },
                        {   # phrase / proximity boost
                            "multi_match": {
                                "query": query.lower(),
                                "type": "phrase",
                                "slop": 3,
                                "fields": ["text^2", "title^3"],
                                "boost": 2
                            }
                        }
                    ]
                }
            },
            "size": n_results_per_query
        }

        
        try:
            response = es.search(index="documents", body=search_body)
            
            for hit in response['hits']['hits'][:n_results_per_query]:
                source = hit['_source']
                all_documents.append({
                    'text': source['text'],
                    'url': source['url'],
                    'title': source['title'],
                    'relevance_score': hit['_score']
                })
                
        except Exception as e:
            logger.error(f"Elasticsearch search error: {e}")
            # Fallback to simple search if multi_match fails
            try:
                simple_search = {
                    "query": {
                        "match": {
                            "text": query.lower()
                        }
                    },
                    "size": n_results_per_query
                }
                response = es.search(index="documents", body=simple_search)
                for hit in response['hits']['hits'][:n_results_per_query]:
                    source = hit['_source']
                    all_documents.append({
                        'text': source['text'],
                        'url': source['url'],
                        'title': source['title'],
                        'relevance_score': hit['_score']
                    })
            except Exception as e2:
                logger.error(f"Fallback search also failed: {e2}")
    
    return all_documents
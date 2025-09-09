# -*- coding: utf-8 -*-
"""
Main text search module with pluggable search algorithms
"""
import os
import logging
from datetime import datetime
from search_algorithms import bm25_search

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default search algorithm
DEFAULT_SEARCH_ALGORITHM = bm25_search

def search_documents_by_text(queries, n_results_per_query=5):
    """Main search function using default BM25 algorithm"""
    # Convert queries to lowercase for case insensitive search
    if isinstance(queries, list):
        queries = [q.lower() if q else q for q in queries]
    return DEFAULT_SEARCH_ALGORITHM.search_documents_by_text(queries, n_results_per_query)


def test_all_algorithms():
    """Test all search algorithms and save results to log files"""
    from search_algorithms import bm25_search, tfidf_search, simple_like_search
    
    test_queries = ["questão de limites piauí ceará demarcação serras"]
    algorithms = {
        'bm25': bm25_search,
        'tfidf': tfidf_search,
        'simple_like': simple_like_search
    }
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for algo_name, algo_module in algorithms.items():
        logger.info(f"Testing {algo_name} algorithm...")
        
        try:
            results = algo_module.search_documents_by_text(test_queries, n_results_per_query=10)
            
            # Save results to log file in search_algorithms folder
            log_filename = f"search_algorithms/{algo_name}_results.txt"
            with open(log_filename, 'a', encoding='utf-8') as f:
                f.write(f"\n=== Test Run: {timestamp} ===\n")
                f.write(f"Queries: {test_queries}\n")
                f.write(f"Total results: {len(results)}\n\n")
                
                for i, doc in enumerate(results, 1):
                    f.write(f"--- Result {i} ---\n")
                    f.write(f"Score: {doc['relevance_score']:.4f}\n")
                    f.write(f"URL: {doc['url']}\n")
                    f.write(f"Text snippet: {doc['text']}...\n\n")
            
            logger.info(f"{algo_name}: {len(results)} results appended to {log_filename}")
            
        except Exception as e:
            logger.error(f"Error testing {algo_name}: {e}")

def test_text_search():
    """Test default BM25 algorithm"""
    test_queries = ["questão de limites piauí ceará demarcação serras"]
    logger.info(f"Testing default algorithm with queries: {test_queries}")

    results = search_documents_by_text(test_queries, n_results_per_query=5)
    logger.info(f"Total results: {len(results)}")

    for i, doc in enumerate(results, 1):
        logger.info(f"\n--- Result {i} ---")
        logger.info(f"Score: {doc['relevance_score']:.2f}")
        logger.info(f"URL: {doc['url']}")
        logger.info(f"Text snippet: {doc['text']}...")

    return results


if __name__ == "__main__":
    test_all_algorithms()
    #test_text_search()

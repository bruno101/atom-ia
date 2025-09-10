# -*- coding: utf-8 -*-
"""
BM25P search algorithm implementation - BM25 with proximity scoring
"""
import os
import logging
import oracledb
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
import math

logger = logging.getLogger(__name__)

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_9")

def fetch_candidate_documents(query):
    """Fetch documents containing at least one word from the query using simple LIKE"""
    words = [w.strip() for w in query.split() if w.strip()]
    if not words:
        return []

    like_conditions = " OR ".join([f"UPPER(text) LIKE UPPER('%{word}%')" for word in words])
    sql = f"""
        SELECT text, url, title
        FROM documents
        WHERE {like_conditions}
    """

    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                results = []
                for text, url, title in cursor.fetchall():
                    text_content = text.read() if hasattr(text, "read") else str(text)
                    results.append({
                        "text": text_content,
                        "url": url,
                        "title": title
                    })
                return results
    except oracledb.Error as e:
        logger.error(f"Error fetching documents: {e}")
        return []

def calculate_proximity_score(query_tokens, doc_tokens, window_size=10):
    """Calculate proximity score based on term distances"""
    if len(query_tokens) < 2:
        return 1.0
    
    proximity_score = 0.0
    total_pairs = 0
    
    for i, token1 in enumerate(query_tokens):
        for j, token2 in enumerate(query_tokens):
            if i >= j:
                continue
            
            positions1 = [k for k, t in enumerate(doc_tokens) if t == token1]
            positions2 = [k for k, t in enumerate(doc_tokens) if t == token2]
            
            if positions1 and positions2:
                min_distance = min(abs(p1 - p2) for p1 in positions1 for p2 in positions2)
                if min_distance <= window_size:
                    proximity_score += 1.0 / (1.0 + min_distance)
                total_pairs += 1
    
    return proximity_score / max(total_pairs, 1)

def rank_documents(query, documents, top_n=5):
    """Re-rank documents using BM25P (BM25 + proximity)"""
    if not documents:
        return []

    corpus = [doc["text"].lower() for doc in documents]
    tokenized_corpus = [doc.split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)

    query_tokens = query.lower().split()
    bm25_scores = bm25.get_scores(query_tokens)
    
    # Calculate proximity scores
    proximity_scores = []
    for doc_tokens in tokenized_corpus:
        prox_score = calculate_proximity_score(query_tokens, doc_tokens)
        proximity_scores.append(prox_score)
    
    # Combine BM25 and proximity scores
    combined_scores = []
    for bm25_score, prox_score in zip(bm25_scores, proximity_scores):
        # Weight: 70% BM25, 30% proximity
        combined_score = 0.7 * bm25_score + 0.3 * prox_score * max(bm25_scores)
        combined_scores.append(combined_score)

    ranked_docs = sorted(
        zip(documents, combined_scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [{"text": d["text"], "url": d["url"], "title": d["title"], "relevance_score": s} 
            for d, s in ranked_docs[:top_n]]

def search_documents_by_text(queries, n_results_per_query=5):
    """BM25P search implementation"""
    if not queries or not isinstance(queries, list):
        return []
    
    all_documents = []
    for query in queries:
        if not query or not query.strip():
            continue
        candidates = fetch_candidate_documents(query)
        if not candidates:
            continue
        results = rank_documents(query, candidates, n_results_per_query)
        all_documents.extend(results)
    
    return all_documents
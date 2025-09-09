# -*- coding: utf-8 -*-
"""
TF-IDF search algorithm implementation
"""
import os
import logging
import oracledb
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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

def rank_documents(query, documents, top_n=5):
    """Re-rank documents using TF-IDF cosine similarity"""
    if not documents:
        return []

    corpus = [doc["text"].lower() for doc in documents]
    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus + [query.lower()])
        query_vector = tfidf_matrix[-1]
        doc_vectors = tfidf_matrix[:-1]
        
        similarities = cosine_similarity(query_vector, doc_vectors).flatten()
        
        ranked_docs = sorted(
            zip(documents, similarities),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [{"text": d["text"], "url": d["url"], "title": d["title"], "relevance_score": float(s)} 
                for d, s in ranked_docs[:top_n]]
    except:
        # Fallback to simple scoring
        return [{"text": d["text"], "url": d["url"], "title": d["title"], "relevance_score": 1.0} 
                for d in documents[:top_n]]

def search_documents_by_text(queries, n_results_per_query=5):
    """TF-IDF search implementation"""
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
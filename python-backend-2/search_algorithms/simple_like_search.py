# -*- coding: utf-8 -*-
"""
Simple LIKE search algorithm implementation
"""
import os
import logging
import oracledb
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_9")

def search_documents_by_text(queries, n_results_per_query=5):
    """Simple LIKE search implementation"""
    if not queries or not isinstance(queries, list):
        return []
    
    all_documents = []
    
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as conn:
            with conn.cursor() as cursor:
                for query in queries:
                    if not query or not query.strip():
                        continue
                    
                    terms = [term.strip() for term in query.split() if term.strip()]
                    like_conditions = [f"UPPER(text) LIKE UPPER('%{term}%')" for term in terms]
                    where_clause = " AND ".join(like_conditions)
                    
                    sql = f"""
                    SELECT text, url, title, 1 as relevance_score
                    FROM documents 
                    WHERE {where_clause}
                    FETCH FIRST {n_results_per_query} ROWS ONLY
                    """
                    
                    cursor.execute(sql)
                    
                    for text, url, title, score in cursor.fetchall():
                        text_content = text.read() if hasattr(text, 'read') else str(text)
                        all_documents.append({
                            'text': text_content,
                            'url': url,
                            'title': title,
                            'relevance_score': score
                        })
        
        return all_documents
        
    except oracledb.Error as e:
        logger.error(f"Error in LIKE search: {e}")
        return []
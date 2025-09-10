# -*- coding: utf-8 -*-
"""
Implementação do algoritmo LambdaMART para re-ranking de documentos

LambdaMART é um algoritmo de aprendizado de máquina para ranking que utiliza
gradient boosting para otimizar métricas de ranking como NDCG. Esta implementação
utiliza Random Forest como aproximação, combinando múltiplas features de relevância
para melhorar a ordenação dos resultados de busca.
"""
import os
import logging
import oracledb
import numpy as np
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor

# Logger para este módulo
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

# Inicializa cliente Oracle
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

def extract_features(query, documents):
    """Extrai features para re-ranking LambdaMART
    
    Combina múltiplas features de relevância para treinar o modelo de ranking:
    1. BM25 scores - relevância probabilística
    2. TF-IDF similarity - similaridade vetorial
    3. Document length - normalização por tamanho
    4. Query term frequency - frequência de termos da consulta
    
    Args:
        query (str): Consulta de busca
        documents (list[dict]): Lista de documentos candidatos
        
    Returns:
        np.ndarray: Matrix de features (n_docs x n_features)
    """
    if not documents:
        return np.array([])
    
    # Prepara consulta e corpus
    query_tokens = query.lower().split()
    corpus = [doc["text"].lower() for doc in documents]
    
    # Feature 1: Scores BM25 - algoritmo probabilístico padrão
    tokenized_corpus = [doc.split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(query_tokens)
    
    # Feature 2: Similaridade cosseno TF-IDF - representação vetorial
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus + [query.lower()])
        query_vector = tfidf_matrix[-1]
        doc_vectors = tfidf_matrix[:-1]
        from sklearn.metrics.pairwise import cosine_similarity
        tfidf_scores = cosine_similarity(query_vector, doc_vectors).flatten()
    except:
        # Fallback em caso de erro
        tfidf_scores = np.ones(len(documents))
    
    # Feature 3: Tamanho do documento (normalizado) - penaliza documentos muito longos
    doc_lengths = np.array([len(doc.split()) for doc in corpus])
    normalized_lengths = doc_lengths / np.max(doc_lengths) if np.max(doc_lengths) > 0 else doc_lengths
    
    # Feature 4: Frequência de termos da consulta no documento
    query_term_freq = []
    for doc in corpus:
        doc_tokens = doc.split()
        freq = sum(doc_tokens.count(token) for token in query_tokens)
        query_term_freq.append(freq / len(doc_tokens) if doc_tokens else 0)
    
    # Combina todas as features em uma matriz
    features = np.column_stack([
        bm25_scores,           # Feature 1: BM25
        tfidf_scores,          # Feature 2: TF-IDF
        normalized_lengths,    # Feature 3: Tamanho normalizado
        query_term_freq        # Feature 4: Frequência de termos
    ])
    
    return features

def rank_documents(query, documents, top_n=5):
    """Re-classifica documentos usando abordagem inspirada no LambdaMART
    
    Utiliza Random Forest como aproximação do LambdaMART para combinar múltiplas
    features de relevância. Em um sistema real, o modelo seria treinado com dados
    rotulados de relevância, mas aqui usamos combinação ponderada das features.
    
    Args:
        query (str): Consulta de busca original
        documents (list[dict]): Documentos candidatos
        top_n (int): Número de documentos a retornar
        
    Returns:
        list[dict]: Documentos re-classificados com scores LambdaMART
    """
    if not documents:
        return []
    
    # Extrai features dos documentos
    features = extract_features(query, documents)
    if features.size == 0:
        return documents[:top_n]
    
    # Aproximação simples do LambdaMART usando Random Forest
    # Em produção, seria treinado com dados rotulados de relevância
    rf = RandomForestRegressor(n_estimators=10, random_state=42)
    
    # Cria labels sintéticos baseados em combinação ponderada das features
    # Pesos: BM25 (40%), TF-IDF (30%), Tamanho (10%), Freq. Termos (20%)
    synthetic_labels = (features[:, 0] * 0.4 +  # BM25
                       features[:, 1] * 0.3 +   # TF-IDF
                       features[:, 2] * 0.1 +   # Tamanho normalizado
                       features[:, 3] * 0.2)    # Frequência de termos
    
    # Treina modelo com features e labels sintéticos
    rf.fit(features, synthetic_labels)
    predicted_scores = rf.predict(features)
    
    # Ordena documentos por scores preditos (maior para menor)
    ranked_indices = np.argsort(predicted_scores)[::-1]
    
    # Constrói lista de documentos re-classificados
    ranked_docs = []
    for idx in ranked_indices[:top_n]:
        doc = documents[idx]
        ranked_docs.append({
            "text": doc["text"],
            "url": doc["url"],
            "title": doc["title"],
            "relevance_score": float(predicted_scores[idx])
        })
    
    return ranked_docs

def search_documents_by_text(queries, n_results_per_query=5):
    """Implementação principal da busca LambdaMART
    
    Pipeline completo de busca com re-ranking por machine learning:
    1. Busca documentos candidatos no banco de dados
    2. Extrai múltiplas features de relevância
    3. Aplica modelo Random Forest para re-ranking
    4. Retorna documentos ordenados por relevância predita
    
    Args:
        queries (list[str]): Lista de consultas de busca
        n_results_per_query (int): Número de resultados por consulta
        
    Returns:
        list[dict]: Documentos re-classificados com scores LambdaMART
    """
    # Validação de entrada
    if not queries or not isinstance(queries, list):
        return []
    
    all_documents = []
    
    # Processa cada consulta individualmente
    for query in queries:
        # Pula consultas vazias
        if not query or not query.strip():
            continue
            
        # Etapa 1: Busca documentos candidatos
        candidates = fetch_candidate_documents(query)
        if not candidates:
            continue
            
        # Etapa 2: Re-classifica usando LambdaMART
        results = rank_documents(query, candidates, n_results_per_query)
        all_documents.extend(results)
    
    return all_documents
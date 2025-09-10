# -*- coding: utf-8 -*-
"""
Implementação do algoritmo de busca BM25

BM25 (Best Matching 25) é um algoritmo de ranking probabilístico usado para
estimar a relevância de documentos para uma consulta de busca. É baseado no
modelo probabilístico de recuperação de informação desenvolvido por Robertson e Jones.
"""
import os
import logging
import oracledb
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi

# Logger para este módulo
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

# Inicializa cliente Oracle com biblioteca instant client
oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_9")

def fetch_candidate_documents(query):
    """Busca documentos candidatos que contenham pelo menos uma palavra da consulta
    
    Utiliza consultas LIKE simples no Oracle para encontrar documentos que contenham
    qualquer uma das palavras da consulta. Esta é a primeira etapa do processo de
    busca, criando um conjunto de candidatos para posterior re-ranking com BM25.
    
    Args:
        query (str): Consulta de busca do usuário
        
    Returns:
        list[dict]: Lista de documentos candidatos com texto, URL e título
    """
    # Divide a consulta em palavras individuais
    words = [w.strip() for w in query.split() if w.strip()]
    if not words:
        return []

    # Cria condições LIKE para cada palavra (busca case-insensitive)
    like_conditions = " OR ".join([f"UPPER(text) LIKE UPPER('%{word}%')" for word in words])
    sql = f"""
        SELECT text, url, title
        FROM documents
        WHERE {like_conditions}
    """

    try:
        # Conecta ao banco Oracle e executa consulta
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                results = []
                
                # Processa cada documento encontrado
                for text, url, title in cursor.fetchall():
                    # Trata objetos CLOB do Oracle
                    text_content = text.read() if hasattr(text, "read") else str(text)
                    results.append({
                        "text": text_content,
                        "url": url,
                        "title": title
                    })
                return results
    except oracledb.Error as e:
        logger.error(f"Erro ao buscar documentos: {e}")
        return []

def rank_documents(query, documents, top_n=5):
    """Re-classifica documentos usando algoritmo BM25
    
    Aplica o algoritmo BM25 para calcular scores de relevância entre a consulta
    e cada documento candidato. O BM25 considera frequência de termos, frequência
    inversa de documentos e normalização por tamanho do documento.
    
    Args:
        query (str): Consulta de busca original
        documents (list[dict]): Lista de documentos candidatos
        top_n (int): Número máximo de resultados a retornar
        
    Returns:
        list[dict]: Documentos ordenados por relevância com scores BM25
    """
    if not documents:
        return []

    # Prepara corpus convertendo textos para minúsculas
    corpus = [doc["text"].lower() for doc in documents]
    # Tokeniza cada documento (divide em palavras)
    tokenized_corpus = [doc.split() for doc in corpus]
    
    # Inicializa modelo BM25 com o corpus tokenizado
    bm25 = BM25Okapi(tokenized_corpus)

    # Tokeniza consulta e calcula scores BM25 para cada documento
    query_tokens = query.lower().split()
    scores = bm25.get_scores(query_tokens)

    # Ordena documentos por score de relevância (maior para menor)
    ranked_docs = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    # Retorna top_n documentos com seus scores de relevância
    return [{"text": d["text"], "url": d["url"], "title": d["title"], "relevance_score": s} 
            for d, s in ranked_docs[:top_n]]

def search_documents_by_text(queries, n_results_per_query=5):
    """Implementação principal da busca BM25
    
    Função principal que coordena o processo de busca BM25:
    1. Busca documentos candidatos no banco de dados
    2. Aplica algoritmo BM25 para re-ranking
    3. Retorna documentos mais relevantes
    
    Args:
        queries (list[str]): Lista de consultas de busca
        n_results_per_query (int): Número de resultados por consulta
        
    Returns:
        list[dict]: Lista de documentos encontrados com scores de relevância
    """
    # Validação de entrada
    if not queries or not isinstance(queries, list):
        return []
    
    all_documents = []
    
    # Processa cada consulta individualmente
    for query in queries:
        # Pula consultas vazias ou inválidas
        if not query or not query.strip():
            continue
            
        # Etapa 1: Busca documentos candidatos no banco
        candidates = fetch_candidate_documents(query)
        if not candidates:
            continue
            
        # Etapa 2: Re-classifica candidatos usando BM25
        results = rank_documents(query, candidates, n_results_per_query)
        all_documents.extend(results)
    
    return all_documents
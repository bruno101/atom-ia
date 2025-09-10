# -*- coding: utf-8 -*-
"""
Implementação do algoritmo de busca vetorial semântica

Utiliza embeddings vetoriais para busca semântica baseada no significado do conteúdo,
não apenas correspondência de palavras-chave. Implementa interface compatível com
outros algoritmos de busca para integração no sistema modular.
"""
import os
import logging
import oracledb
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import ssl

# Logger para este módulo
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

# Modelo para gerar embeddings
MODEL_NAME = 'intfloat/multilingual-e5-large-instruct'

# Cache global do modelo
_model_cache = None


def get_model():
    """Carrega o modelo de embedding uma única vez e mantém em cache
    
    Returns:
        SentenceTransformer: Modelo carregado para gerar embeddings
    """
    global _model_cache
    
    if _model_cache is None:
        logger.info(f"Carregando modelo {MODEL_NAME}...")
        try:
            # Configura proxy para redes corporativas (se necessário)
            os.environ['http_proxy'] = 'http://10.0.220.11:3128'
            os.environ['https_proxy'] = 'http://10.0.220.11:3128'
            
            # Contorna verificação SSL para redes corporativas
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # Carrega modelo do Hugging Face
            _model_cache = SentenceTransformer(MODEL_NAME)
            logger.info("Modelo carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise
    
    return _model_cache

def vectorize_query(query_text):
    """Converte texto da consulta em vetor de embedding
    
    Args:
        query_text (str): Texto da consulta do usuário
        
    Returns:
        np.ndarray: Vetor de embedding da consulta
    """
    try:
        # Obtém modelo do cache
        model = get_model()
        
        # Adiciona prefixo "query:" recomendado para consultas nos modelos e5
        query_with_prefix = f"query: {query_text}"
        
        # Gera embedding da consulta
        embedding = model.encode([query_with_prefix], convert_to_numpy=True)
        
        return embedding[0]  # Retorna o primeiro (e único) embedding
        
    except Exception as e:
        logger.error(f"Erro ao vetorizar consulta: {e}")
        raise

def search_documents_by_text(queries, n_results_per_query=5):
    """Implementação da busca vetorial semântica
    
    Interface compatível com outros algoritmos de busca. Converte consultas em
    embeddings vetoriais e utiliza VECTOR_DISTANCE do Oracle 23ai para encontrar
    documentos semanticamente similares.
    
    Args:
        queries (list[str]): Lista de consultas de busca
        n_results_per_query (int): Número de resultados por consulta
        
    Returns:
        list[dict]: Lista de documentos com campos 'text', 'url', 'title', 'relevance_score'
    """
    # Validação de entrada
    if not queries or not isinstance(queries, list):
        return []
    
    all_documents = []
    
    try:
        # Conecta ao banco Oracle
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            with connection.cursor() as cursor:
                
                # Processa cada consulta individualmente
                for query in queries:
                    if not query or not query.strip():
                        continue
                    
                    logger.info(f"Processando consulta vetorial: '{query[:50]}...'")
                    
                    # Etapa 1: Gerar embedding vetorial da consulta
                    query_vector = vectorize_query(query)
                    
                    # Etapa 2: Converter para formato Oracle VECTOR
                    vector_str = '[' + ','.join(map(str, query_vector.astype(np.float32))) + ']'
                    
                    # Etapa 3: Executar busca vetorial no Oracle
                    sql = """
                    SELECT text, url, title, VECTOR_DISTANCE(vector, VECTOR(:1)) as distance
                    FROM documents 
                    ORDER BY VECTOR_DISTANCE(vector, VECTOR(:2))
                    FETCH FIRST :3 ROWS ONLY
                    """
                    
                    cursor.execute(sql, (vector_str, vector_str, n_results_per_query))
                    results = cursor.fetchall()
                    
                    # Etapa 4: Formatar resultados
                    for text, url, title, distance in results:
                        # Trata objetos CLOB do Oracle
                        text_content = text.read() if hasattr(text, 'read') else str(text)
                        
                        # Converte distância em score de relevância (menor distância = maior relevância)
                        relevance_score = 1.0 / (1.0 + distance) if distance > 0 else 1.0
                        
                        all_documents.append({
                            'text': text_content,
                            'url': url,
                            'title': title,
                            'relevance_score': relevance_score
                        })
                    
                    logger.info(f"Encontrados {len(results)} resultados para consulta vetorial")
        
        return all_documents
        
    except oracledb.Error as e:
        logger.error(f"Erro de banco de dados Oracle: {e}")
        return []
    except Exception as e:
        logger.error(f"Erro inesperado na busca vetorial: {e}")
        return []
# -*- coding: utf-8 -*-
"""
Módulo para busca semântica usando embeddings vetoriais no Oracle 23ai
Permite buscar documentos similares usando consultas em linguagem natural
"""
import os
import logging
import oracledb
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import ssl

# Configurar logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD") 
DB_DSN = os.getenv("DB_DSN")

# Modelo para gerar embeddings (mesmo usado no populate_database.py)
MODEL_NAME = 'intfloat/multilingual-e5-large-instruct'

# Cache global do modelo para evitar recarregamento
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
            # Configure proxy for corporate network
            os.environ['http_proxy'] = 'http://10.0.220.11:3128'
            os.environ['https_proxy'] = 'http://10.0.220.11:3128'
            
            # Bypass SSL verification for corporate networks
            ssl._create_default_https_context = ssl._create_unverified_context
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
    logger.info(f"Vetorizando consulta: '{query_text[:50]}...'")
    
    try:
        model = get_model()
        # Prefixo "query:" recomendado para consultas nos modelos e5
        query_with_prefix = f"query: {query_text}"
        embedding = model.encode([query_with_prefix], convert_to_numpy=True)
        
        logger.info(f"Embedding gerado com shape: {embedding.shape}")
        return embedding[0]  # Retorna o primeiro (e único) embedding
        
    except Exception as e:
        logger.error(f"Erro ao vetorizar consulta: {e}")
        raise

def search_similar_documents(query_text, n_results=5):
    """Busca documentos similares usando busca vetorial semântica
    
    Args:
        query_text (str): Consulta em linguagem natural
        n_results (int): Número de resultados a retornar (padrão: 5)
        
    Returns:
        list[dict]: Lista de documentos com campos 'text' e 'url'
    """
    logger.info(f"Iniciando busca por '{query_text}' (top {n_results} resultados)")
    
    # Validar parâmetros
    if not query_text or not query_text.strip():
        logger.warning("Consulta vazia fornecida")
        return []
    
    if n_results <= 0:
        logger.warning("Número de resultados deve ser positivo")
        return []
    
    try:
        # Gerar embedding da consulta
        query_vector = vectorize_query(query_text)
        
        # Converter para formato Oracle VECTOR
        vector_str = '[' + ','.join(map(str, query_vector.astype(np.float32))) + ']'
        logger.info("Vetor da consulta formatado para Oracle")
        
        # Conectar ao banco e executar busca
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            logger.info("Conexão com Oracle estabelecida")
            
            with connection.cursor() as cursor:
                # Query usando VECTOR_DISTANCE para busca por similaridade
                # Ordena por menor distância (mais similar)
                sql = """
                SELECT text, url, title, VECTOR_DISTANCE(vector, VECTOR(:1)) as distance
                FROM documents 
                ORDER BY VECTOR_DISTANCE(vector, VECTOR(:2))
                FETCH FIRST :3 ROWS ONLY
                """
                
                logger.info(f"Executando consulta SQL para {n_results} resultados")
                cursor.execute(sql, (vector_str, vector_str, n_results))
                
                results = cursor.fetchall()
                logger.info(f"Encontrados {len(results)} resultados")
                
                # Formatar resultados
                documents = []
                for i, (text, url, title, distance) in enumerate(results):
                    # Handle CLOB objects by reading their content
                    text_content = text.read() if hasattr(text, 'read') else str(text)
                    
                    documents.append({
                        'text': text_content,
                        'url': url,
                        'title': title
                    })
                    logger.debug(f"Resultado {i+1}: distância={distance:.4f}, url={url}")
                
                return documents
                
    except oracledb.Error as e:
        logger.error(f"Erro de banco de dados Oracle: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na busca: {e}")
        raise

def test_vector_search():
    """Função de teste para verificar se a busca vetorial está funcionando"""
    logger.info("=== TESTE DA BUSCA VETORIAL ===")
    
    try:
        # Teste com consulta simples
        test_query = "escravidão"
        results = search_similar_documents(test_query, n_results=3)
        
        logger.info(f"Teste executado com sucesso!")
        logger.info(f"Consulta: '{test_query}'")
        logger.info(f"Resultados encontrados: {len(results)}")
        
        for i, doc in enumerate(results, 1):
            logger.info(f"\n--- Resultado {i} ---")
            logger.info(f"URL: {doc['url']}")
            text_preview = doc['text'][:100] if doc['text'] else 'Sem texto'
            logger.info(f"Texto (primeiros 100 chars): {text_preview}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Teste falhou: {e}")
        return False

if __name__ == "__main__":
    # Executar teste quando script é rodado diretamente
    test_vector_search()
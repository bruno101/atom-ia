# -*- coding: utf-8 -*-
"""
Generate chunks from documents and store them with vectors in Oracle database
"""
import os
import logging
import oracledb
import numpy as np
import time
import argparse
import ssl
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Configuration variables
CHUNK_SIZE = 500  # Size of each chunk in characters
OVERLAP_SIZE = 200  # Size of overlap between chunks in characters
BATCH_SIZE = 50  # Number of chunks to process in each batch
MODEL_NAME = 'intfloat/multilingual-e5-large-instruct'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")


def split_text_into_chunks(text, chunk_size, overlap_size):
    """Split text into overlapping chunks of specified size with word boundaries"""
    if not text or chunk_size <= 0:
        return []
    
    words = text.split()
    chunks = []
    start_idx = 0
    
    while start_idx < len(words):
        current_chunk = []
        current_length = 0
        word_idx = start_idx
        
        # Build chunk from start_idx
        while word_idx < len(words) and current_length + len(words[word_idx]) + 1 <= chunk_size:
            current_chunk.append(words[word_idx])
            current_length += len(words[word_idx]) + 1
            word_idx += 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Calculate next start position with overlap
        if word_idx >= len(words):
            break
            
        # Find overlap start position
        overlap_length = 0
        overlap_words = 0
        for i in range(len(current_chunk) - 1, -1, -1):
            word_len = len(current_chunk[i]) + 1
            if overlap_length + word_len <= overlap_size:
                overlap_length += word_len
                overlap_words += 1
            else:
                break
        
        start_idx = max(start_idx + len(current_chunk) - overlap_words, start_idx + 1)
    
    return chunks

def create_chunks_table(cursor):
    """Create chunks table if it doesn't exist"""
    try:
        cursor.execute("SELECT COUNT(*) FROM chunks WHERE ROWNUM = 1")
        logger.info("Tabela 'chunks' já existe.")
    except oracledb.Error:
        logger.info("Criando tabela 'chunks'...")
        create_table_sql = """
        CREATE TABLE chunks (
            id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            document_id NUMBER,
            chunk_text CLOB,
            chunk_index NUMBER,
            vector VECTOR(1024, FLOAT32)
        ) TABLESPACE USERS
        """
        cursor.execute(create_table_sql)
        logger.info("Tabela 'chunks' criada com sucesso.")

def generate_chunks():
    """Generate chunks from documents and store them with vectors"""
    logger.info(f"Carregando modelo {MODEL_NAME}...")
    
    # Configura proxy para redes corporativas
    os.environ['http_proxy'] = 'http://10.0.220.11:3128'
    os.environ['https_proxy'] = 'http://10.0.220.11:3128'
    
    # Contorna verificação SSL para redes corporativas
    ssl._create_default_https_context = ssl._create_unverified_context
    
    model = SentenceTransformer(MODEL_NAME)
    logger.info("Modelo carregado com sucesso.")
    
    try:
        logger.info("Conectando ao banco de dados Oracle...")
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            logger.info("Conexão com o banco de dados Oracle bem-sucedida.")
            with connection.cursor() as cursor:
                # Create chunks table if needed
                create_chunks_table(cursor)
                
                # Clear existing chunks
                cursor.execute("DELETE FROM chunks")
                connection.commit()
                logger.info("Chunks existentes removidos.")
                
                # Fetch documents
                logger.info("Buscando documentos...")
                cursor.execute("SELECT id, text FROM documents")
                documents = cursor.fetchall()
                logger.info(f"Encontrados {len(documents)} documentos.")
                
                all_chunks = []
                for doc_id, text_clob in documents:
                    # Read CLOB content
                    text = text_clob.read() if hasattr(text_clob, 'read') else str(text_clob)
                    
                    # Generate chunks
                    chunks = split_text_into_chunks(text, CHUNK_SIZE, OVERLAP_SIZE)
                    
                    for chunk_index, chunk_text in enumerate(chunks):
                        all_chunks.append({
                            'document_id': doc_id,
                            'chunk_text': chunk_text,
                            'chunk_index': chunk_index
                        })
                
                logger.info(f"Gerados {len(all_chunks)} chunks de {len(documents)} documentos.")
                
                # Process chunks in batches
                total_chunks = len(all_chunks)
                num_batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE
                
                logger.info(f"Processando {total_chunks} chunks em {num_batches} lotes de até {BATCH_SIZE} chunks cada.")
                
                for i in range(0, total_chunks, BATCH_SIZE):
                    batch_start_time = time.time()
                    batch = all_chunks[i:i + BATCH_SIZE]
                    
                    logger.info(f"--- Processando lote {i // BATCH_SIZE + 1}/{num_batches} ---")
                    
                    # Prepare texts for embedding with E5 prefix
                    texts_to_embed = ["passage: " + chunk['chunk_text'] for chunk in batch]
                    
                    logger.info(f"Gerando embeddings para {len(batch)} chunks...")
                    embeddings = model.encode(texts_to_embed, convert_to_numpy=True, show_progress_bar=True)
                    logger.info(f"Embeddings gerados. Shape: {embeddings.shape}")
                    
                    # Insert chunks
                    logger.info("Inserindo chunks no banco de dados...")
                    for chunk, vector in zip(batch, embeddings):
                        # Format vector as string for Oracle VECTOR constructor
                        vector_str = '[' + ','.join(map(str, vector.astype(np.float32))) + ']'
                        
                        # Insert chunk
                        sql = "INSERT INTO chunks (document_id, chunk_index, vector) VALUES (:1, :2, VECTOR(:3))"
                        cursor.execute(sql, (chunk['document_id'], chunk['chunk_index'], vector_str))
                        
                        # Update CLOB separately
                        cursor.execute("UPDATE chunks SET chunk_text = :1 WHERE id = (SELECT MAX(id) FROM chunks)", (chunk['chunk_text'],))
                    
                    connection.commit()
                    
                    batch_end_time = time.time()
                    logger.info(f"Lote {i // BATCH_SIZE + 1} inserido com sucesso em {batch_end_time - batch_start_time:.2f} segundos.")
                
                # Show sample record
                logger.info("--- Amostra de chunk inserido ---")
                cursor.execute("SELECT id, document_id, chunk_index, SUBSTR(chunk_text, 1, 100) as chunk_sample FROM chunks WHERE ROWNUM = 1 ORDER BY id DESC")
                sample = cursor.fetchone()
                if sample:
                    logger.info(f"ID: {sample[0]}")
                    logger.info(f"Document ID: {sample[1]}")
                    logger.info(f"Chunk Index: {sample[2]}")
                    logger.info(f"Chunk Text (primeiros 100 chars): {sample[3]}...")
                else:
                    logger.info("Nenhum chunk encontrado.")
                
                logger.info(f"Processamento concluído. Total de chunks inseridos: {total_chunks}")
                
    except oracledb.Error as e:
        error, = e.args
        logger.error(f"ERRO de banco de dados Oracle: {error.message}")
        logger.error("Verifique se o container Docker está em execução e se as credenciais estão corretas.")
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado: {e}")

def main():
    logger.info(f"Iniciando geração de chunks com tamanho: {CHUNK_SIZE} e overlap: {OVERLAP_SIZE}")
    generate_chunks()

if __name__ == "__main__":
    main()
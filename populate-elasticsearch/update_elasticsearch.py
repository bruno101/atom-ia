# -*- coding: utf-8 -*-
"""
Atualização incremental do Elasticsearch
Detecta mudanças no Oracle e sincroniza com Elasticsearch
"""
import os
import sys
import logging
import oracledb
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["NO_PROXY"] = "localhost,127.0.0.1"

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_9")

def get_document_hash(text, url, title):
    """Gera hash único para detectar mudanças no documento"""
    content = f"{text}{url}{title}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def fetch_oracle_documents():
    """Busca todos os documentos do Oracle"""
    
    try:
        # Force fresh connection
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as conn:
            # Set read committed isolation and autocommit
            conn.autocommit = True
            
            with conn.cursor() as cursor:
                # Force fresh read with hints
                cursor.execute("ALTER SESSION SET ISOLATION_LEVEL = READ COMMITTED")
                cursor.execute("COMMIT")
                
                # Test query
                cursor.execute("select title from documents where title like '%10 jul. 1853.'")
                for title in cursor.fetchall():
                    print({"title": title})
                
                # Main query with NO_CACHE hint to force fresh read
                cursor.execute("SELECT /*+ NO_CACHE */ text, url, title FROM documents")
                documents = {}
                
                for text, url, title in cursor.fetchall():
                    text_content = text.read() if hasattr(text, "read") else str(text)
                    doc_hash = get_document_hash(text_content, url, title)
                    documents[url] = {
                        "text": text_content,
                        "url": url,
                        "title": title,
                        "hash": doc_hash
                    }
                
                logger.info(f"Oracle: {len(documents)} documentos encontrados")
                return documents
                
    except oracledb.Error as e:
        logger.error(f"Erro Oracle: {e}")
        return {}

def fetch_elasticsearch_documents():
    """Busca documentos existentes no Elasticsearch"""
    es = Elasticsearch("http://localhost:9200")
    
    try:
        if not es.ping():
            logger.error("Elasticsearch não disponível")
            return {}, None
            
        response = es.search(
            index="documents",
            body={"query": {"match_all": {}}, "size": 10000}
        )
        
        documents = {}
        for hit in response['hits']['hits']:
            source = hit['_source']
            url = source['url']
            # Use stored hash if available, otherwise calculate it
            doc_hash = source.get('hash', get_document_hash(source['text'], source['url'], source['title']))
            documents[url] = {
                "id": hit['_id'],
                "hash": doc_hash
            }
        
        logger.info(f"Elasticsearch: {len(documents)} documentos encontrados")
        return documents, es
        
    except Exception as e:
        logger.error(f"Erro Elasticsearch: {e}")
        return {}, None

def update_elasticsearch(force_reupload=False):
    """Atualiza Elasticsearch com mudanças do Oracle"""
    logger.info("=== ATUALIZANDO ELASTICSEARCH ===")
    
    oracle_docs = fetch_oracle_documents()
    es_docs, es = fetch_elasticsearch_documents()
    
    if not es:
        return
    
    if force_reupload:
        logger.info("🔄 MODO FORCE: Recarregando todos os documentos")
        # Delete all existing documents
        try:
            es.delete_by_query(index="documents", body={"query": {"match_all": {}}})
            logger.info("✅ Todos os documentos removidos")
        except:
            pass
        
        # Add all Oracle documents
        to_add = list(oracle_docs.values())
        to_update = []
        to_delete = []
    else:
        to_add = []
        to_update = []
        to_delete = []
        
        # Detecta novos e modificados
        for url, oracle_doc in oracle_docs.items():
            if url not in es_docs:
                to_add.append(oracle_doc)
            elif es_docs[url]['hash'] != oracle_doc['hash']:
                oracle_doc['es_id'] = es_docs[url]['id']
                to_update.append(oracle_doc)
        
        # Detecta removidos
        for url, es_doc in es_docs.items():
            if url not in oracle_docs:
                to_delete.append(es_doc)
    
    logger.info(f"Mudanças: +{len(to_add)} ~{len(to_update)} -{len(to_delete)}")
    
    # Executa atualizações
    if to_add:
        actions = [{
            "_index": "documents",
            "_source": {"text": doc["text"], "url": doc["url"], "title": doc["title"], "hash": doc["hash"]}
        } for doc in to_add]
        
        bulk(es, actions)
        logger.info(f"✅ {len(to_add)} documentos adicionados")
    
    if to_update:
        for doc in to_update:
            es.update(
                index="documents",
                id=doc["es_id"],
                body={"doc": {"text": doc["text"], "url": doc["url"], "title": doc["title"], "hash": doc["hash"]}}
            )
        logger.info(f"✅ {len(to_update)} documentos atualizados")
    
    if to_delete:
        for doc in to_delete:
            es.delete(index="documents", id=doc["id"])
        logger.info(f"✅ {len(to_delete)} documentos removidos")
    
    if not (to_add or to_update or to_delete):
        logger.info("✅ Elasticsearch já está sincronizado")
    
    logger.info("=== ATUALIZAÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    force_reupload = len(sys.argv) > 1 and sys.argv[1] == "--force"
    update_elasticsearch(force_reupload)
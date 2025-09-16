# -*- coding: utf-8 -*-
"""
Migrate documents from Oracle to Elasticsearch
"""
import os
import logging
import oracledb
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import time
import elasticsearch
print(elasticsearch.__version__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["NO_PROXY"] = "localhost,127.0.0.1"

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")


def wait_for_elasticsearch():
    """Wait for Elasticsearch to be ready"""
    es = Elasticsearch("http://localhost:9200")
    print(es.ping())
    for i in range(30):
        try:
            if es.ping():
                logger.info("Elasticsearch is ready")
                return True
            time.sleep(2)
        except Exception as e:
            logger.info(f"Waiting for Elasticsearch... attempt {i+1}")
            time.sleep(2)
    return False

def create_elasticsearch_index():
    """Create Elasticsearch index with proper mapping"""
    es = Elasticsearch("http://localhost:9200")

    
    mapping = {
        "mappings": {
            "properties": {
                "text": {"type": "text", "analyzer": "standard"},
                "url": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "standard"}
            }
        }
    }
    
    try:
        if es.indices.exists(index="documents"):
            es.indices.delete(index="documents")
            logger.info("Deleted existing index")
    except Exception as e:
        logger.info(f"Index doesn't exist or error checking: {e}")
    
    try:
        es.indices.create(index="documents", body=mapping)
        logger.info("Created Elasticsearch index 'documents'")
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        raise
    
    return es

def fetch_documents_from_oracle():
    """Fetch all documents from Oracle database"""
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT text, url, title FROM documents")
                documents = []
                
                for text, url, title in cursor.fetchall():
                    text_content = text.read() if hasattr(text, "read") else str(text)
                    documents.append({
                        "text": text_content,
                        "url": url,
                        "title": title
                    })
                
                logger.info(f"Fetched {len(documents)} documents from Oracle")
                return documents
                
    except oracledb.Error as e:
        logger.error(f"Error fetching from Oracle: {e}")
        return []

def migrate_documents():
    """Migrate documents from Oracle to Elasticsearch"""
    if not wait_for_elasticsearch():
        logger.error("Elasticsearch not ready")
        return
    
    es = create_elasticsearch_index()
    documents = fetch_documents_from_oracle()
    
    if not documents:
        logger.error("No documents to migrate")
        return
    
    # Prepare documents for bulk indexing
    actions = []
    for i, doc in enumerate(documents):
        action = {
            "_index": "documents",
            "_id": i,
            "_source": doc
        }
        actions.append(action)
    
    # Bulk index documents
    try:
        result = bulk(es, actions)
        logger.info(f"Bulk indexing result: {result}")
        logger.info(f"Successfully indexed documents")
    except Exception as e:
        logger.error(f"Error during bulk indexing: {e}")
        # Try individual indexing as fallback
        for action in actions[:5]:  # Try first 5 documents
            try:
                es.index(index="documents", id=action["_id"], body=action["_source"])
                logger.info(f"Indexed document {action['_id']}")
            except Exception as idx_error:
                logger.error(f"Error indexing document {action['_id']}: {idx_error}")

if __name__ == "__main__":
    migrate_documents()
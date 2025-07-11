import os
import glob
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore
from .config import CHROMA_PATH, STORAGE_PATH, COLLECTION_NAME
from .embeddings import get_chroma_embedding_model
from fetch_documents import fetch_documents_from_db

def initialize_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_vector_store(chroma_collection):
    return ChromaVectorStore(chroma_collection=chroma_collection)

def create_or_load_index(debug=False):
    chroma_client = initialize_chroma_client()
    embed_model_chroma = get_chroma_embedding_model()
    
    chroma_collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, 
        embedding_function=embed_model_chroma
    )
    vector_store = get_vector_store(chroma_collection)

    has_index = os.path.exists(STORAGE_PATH) and bool(glob.glob(f"{STORAGE_PATH}/*.json"))
    
    if (not has_index) or debug:
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        documents = fetch_documents_from_db()
        index = VectorStoreIndex.from_documents(documents, storage_context)
        storage_context.persist(persist_dir=STORAGE_PATH)
    else:
        storage_context = StorageContext.from_defaults(
            persist_dir=STORAGE_PATH, 
            vector_store=vector_store
        )
        index = load_index_from_storage(storage_context)
    
    return index, chroma_collection
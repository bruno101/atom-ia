# Módulo para gerenciamento de índices vetoriais
# Responsável por criar, carregar e gerenciar o índice do LlamaIndex com ChromaDB
import os
import glob
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore
from .config import CHROMA_PATH, STORAGE_PATH, COLLECTION_NAME
from .embeddings import get_chroma_embedding_model
from fetch_documents import fetch_documents_from_db

def initialize_chroma_client():
    """Inicializa o cliente persistente do ChromaDB
    
    Returns:
        chromadb.PersistentClient: Cliente configurado para persistência local
    """
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_vector_store(chroma_collection):
    """Cria um vector store do LlamaIndex usando uma coleção do Chroma
    
    Args:
        chroma_collection: Coleção do ChromaDB
        
    Returns:
        ChromaVectorStore: Vector store configurado
    """
    return ChromaVectorStore(chroma_collection=chroma_collection)

def create_or_load_index(debug=False):
    """Cria um novo índice ou carrega um existente
    
    Args:
        debug (bool): Se True, força a recriação do índice
        
    Returns:
        tuple: (índice do LlamaIndex, coleção do Chroma)
    """
    # Inicializa o cliente e modelo de embedding
    chroma_client = initialize_chroma_client()
    embed_model_chroma = get_chroma_embedding_model()
    
    # Obtém ou cria a coleção no ChromaDB
    chroma_collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, 
        embedding_function=embed_model_chroma
    )
    vector_store = get_vector_store(chroma_collection)

    # Verifica se já existe um índice salvo
    has_index = os.path.exists(STORAGE_PATH) and bool(glob.glob(f"{STORAGE_PATH}/*.json"))
    
    if (not has_index) or debug:
        # Cria novo índice a partir dos documentos do banco
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        documents = fetch_documents_from_db()
        index = VectorStoreIndex.from_documents(documents, storage_context)
        # Persiste o índice no disco
        storage_context.persist(persist_dir=STORAGE_PATH)
    else:
        # Carrega índice existente do disco
        storage_context = StorageContext.from_defaults(
            persist_dir=STORAGE_PATH, 
            vector_store=vector_store
        )
        index = load_index_from_storage(storage_context)
    
    return index, chroma_collection
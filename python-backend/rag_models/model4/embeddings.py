# Módulo para gerenciamento de modelos de embedding
# Fornece wrappers e funções para criar modelos de embedding compatíveis
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from .config import EMBEDDING_MODEL

class ChromaEmbeddingsWrapper:
    """Wrapper para compatibilidade do modelo de embedding com ChromaDB
    
    Adapta o modelo HuggingFace para funcionar com a interface esperada pelo Chroma
    """
    def __init__(self, model_name):
        """Inicializa o wrapper com o modelo especificado"""
        self.model = HuggingFaceEmbedding(model_name=model_name)
    
    def __call__(self, input): 
        """Gera embeddings para o input fornecido"""
        return self.model.embed(input)
    
    def name(self): 
        """Retorna o nome identificador do modelo"""
        return "custom-chroma-embedding"

def get_embedding_model():
    """Cria e retorna uma instância do modelo de embedding padrão
    
    Returns:
        HuggingFaceEmbedding: Modelo configurado com EMBEDDING_MODEL
    """
    return HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)

def get_chroma_embedding_model():
    """Cria e retorna o modelo de embedding compatível com ChromaDB
    
    Returns:
        ChromaEmbeddingsWrapper: Wrapper configurado para uso com Chroma
    """
    return ChromaEmbeddingsWrapper(EMBEDDING_MODEL)
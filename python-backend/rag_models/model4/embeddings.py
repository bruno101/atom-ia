from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from .config import EMBEDDING_MODEL

class ChromaEmbeddingsWrapper:
    def __init__(self, model_name):
        self.model = HuggingFaceEmbedding(model_name=model_name)
    def __call__(self, input): return self.model.embed(input)
    def name(self): return "custom-chroma-embedding"

def get_embedding_model():
    return HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)

def get_chroma_embedding_model():
    return ChromaEmbeddingsWrapper(EMBEDDING_MODEL)
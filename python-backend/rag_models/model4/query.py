from .config import GEMINI_API, LLM_MODEL
from llama_index.llms.google_genai import GoogleGenAI
from .index_management import create_or_load_index
from .query_engine import create_query_engine
from .pipeline import pipeline_stream
from .embeddings import get_embedding_model
from llama_index.core import Settings
from db_connection import fetch_slugs

llm = GoogleGenAI(model=LLM_MODEL, api_key=GEMINI_API)
Settings.llm = llm
Settings.embed_model = get_embedding_model()

print("Modelo LLM carregado:", llm.model)

index, _ = create_or_load_index()
query_engine = create_query_engine(index, llm)

print("Query engine criado com sucesso")

slugs_validos = None
try:
    slugs_validos = fetch_slugs()
except Exception as e:
    raise Exception(f"Slugs não encontradas")

def handle_query(consulta, historico):
    print("Before pipeline_stream")
    return pipeline_stream(consulta, historico, query_engine, llm, slugs_validos)
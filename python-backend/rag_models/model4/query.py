# Módulo principal de consulta - inicializa e configura todos os componentes
# Ponto de entrada para processamento de consultas do usuário
from .config import GEMINI_API, LLM_MODEL
from llama_index.llms.google_genai import GoogleGenAI
from .index_management import create_or_load_index
from .query_engine import create_query_engine
from .pipeline import pipeline_stream
from .embeddings import get_embedding_model
from llama_index.core import Settings
from db_connection import fetch_slugs
from sentence_transformers import CrossEncoder

# Inicializa o modelo de linguagem Google Gemini
llm = GoogleGenAI(model=LLM_MODEL, api_key=GEMINI_API)
# Configura as definições globais do LlamaIndex
Settings.llm = llm
Settings.embed_model = get_embedding_model()

print("Modelo LLM carregado:", llm.model)

# Cria ou carrega o índice vetorial existente
index, _ = create_or_load_index()
# Inicializa o motor de consulta com o índice e modelo
query_engine = create_query_engine(index, llm)

print("Query engine criado com sucesso")

# Carrega lista de slugs válidos do banco de dados para validação
slugs_validos = None
try:
    slugs_validos = fetch_slugs()
except Exception as e:
    raise Exception(f"Slugs não encontradas")

def handle_query(consulta, historico):
    """Função principal para processar consultas do usuário
    
    Args:
        consulta (str): Consulta do usuário
        historico (str): Histórico da conversa
        
    Returns:
        Generator: Stream de mensagens de progresso e resultado final
    """
    print("Before pipeline_stream")
    return pipeline_stream(consulta, historico, query_engine, llm, slugs_validos)
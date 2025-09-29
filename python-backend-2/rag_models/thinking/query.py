# Módulo principal de consulta - inicializa e configura todos os componentes
# Ponto de entrada para processamento de consultas do usuário
from .config import GEMINI_API, LLM_MODEL
from llama_index.llms.google_genai import GoogleGenAI
from .query_engine import create_query_engine
from .pipeline import pipeline_stream
from llama_index.core import Settings

# Inicializa o modelo de linguagem Google Gemini
llm = GoogleGenAI(model=LLM_MODEL, api_key=GEMINI_API)
# Configura as definições globais do LlamaIndex
Settings.llm = llm

print("Modelo LLM carregado:", llm.model)

# Inicializa o motor de consulta com o modelo
query_engine = create_query_engine(llm)

print("Query engine criado com sucesso")

def handle_query(consulta, historico):
    """Função principal para processar consultas do usuário
    
    Args:
        consulta (str): Consulta do usuário
        historico (str): Histórico da conversa
        
    Returns:
        Generator: Stream de mensagens de progresso e resultado final
    """
    print("Before pipeline_stream")
    return pipeline_stream(consulta, historico, query_engine, llm)
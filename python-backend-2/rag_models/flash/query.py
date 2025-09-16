# Módulo principal de consulta - inicializa e configura todos os componentes
# Ponto de entrada para processamento de consultas do usuário
from .config import GEMINI_API, LLM_MODEL
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
from .pipeline import pipeline_stream
# Inicializa o modelo de linguagem Google Gemini
llm = GoogleGenAI(model=LLM_MODEL, api_key=GEMINI_API)
# Configura as definições globais do LlamaIndex
Settings.llm = llm

print("Modelo LLM carregado:", llm.model)

def handle_query_flash(consulta, historico):
    """Função principal para processar consultas do usuário
    
    Args:
        consulta (str): Consulta do usuário
        historico (str): Histórico da conversa
        
    Returns:
        Generator: Stream de mensagens de progresso e resultado final
    """
    return pipeline_stream(consulta, historico, llm)
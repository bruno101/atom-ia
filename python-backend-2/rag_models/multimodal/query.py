# Módulo principal de consulta - inicializa e configura todos os componentes
# Ponto de entrada para processamento de consultas do usuário
from .config import GEMINI_API, LLM_MODEL, GEMINI_API_PROVIDER, PROJECT_ID, LOCATION
from .pipeline import pipeline_stream
import vertexai
from vertexai.generative_models import GenerativeModel
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

# Inicializa o modelo baseado no provider configurado
if GEMINI_API_PROVIDER == "vertex":
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    llm = GenerativeModel(LLM_MODEL)
    print(f"Modelo Vertex AI carregado: {LLM_MODEL}")
else:
    genai.configure(api_key=GEMINI_API)
    llm = genai.GenerativeModel(LLM_MODEL)
    print(f"Modelo Google AI Studio carregado: {LLM_MODEL}")

def handle_query_multimodal(consulta, historico, file_metadata):
    """Função principal para processar consultas multimodais do usuário
    
    Args:
        consulta (str): Consulta do usuário
        historico (str): Histórico da conversa
        tipo_de_arquivo (str): Tipo do arquivo
        texto_arquivo (str): Transcrição do arquivo
        
    Returns:
        Generator: Stream de mensagens de progresso e resultado final
    """
    logger.info(f"Starting multimodal query processing: '{consulta[:100]}...'")
    return pipeline_stream(consulta, historico, llm, file_metadata)
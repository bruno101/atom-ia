# Arquivo de configuração centralizada para o sistema RAG
# Define parâmetros, caminhos e modelos utilizados
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Chave da API do Google Gemini - Google AI Studio
GEMINI_API = os.getenv("GEMINI_API")

# Chave da API do Google Gemini - Vertex
PROJECT_ID = "chatbot-atom"
LOCATION = "us-central1"
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

GEMINI_API_PROVIDER = "google-ai-studio"

# Modelos utilizados no sistema
LLM_MODEL = "gemini-2.5-flash"  # Modelo de linguagem do Google
LLM_EXPANSIONS_MODEL = "gemini-2.0-flash-lite"

NUMBER_OF_MULTIMODAL_QUERY_EXPANSIONS = 5

MAX_NODES_VECTOR_QUERY = 2       # Máximo de nós vetoriais totais
MAX_NODES_TRADITIONAL_QUERY = 4    # Máximo de nós tradicionais totais

# Limitações de tamanho para otimização
MAX_CHARS_PER_NODE = 2500  # Caracteres máximos por nó (controle de tokens)
MAX_QUERY_CHARS = 2000     # Caracteres máximos da consulta do usuário
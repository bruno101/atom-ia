# Arquivo de configuração centralizada para o sistema RAG
# Define parâmetros, caminhos e modelos utilizados
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Chave da API do Google Gemini
GEMINI_API = os.getenv("GEMINI_API")

# Modelos utilizados no sistema
LLM_MODEL = "gemini-2.5-flash"  # Modelo de linguagem do Google


MAX_NODES_VECTOR_QUERY = 15       # Máximo de nós vetoriais totais
MAX_NODES_TRADITIONAL_QUERY = 15    # Máximo de nós tradicionais totais

# Limitações de tamanho para otimização
MAX_CHARS_PER_NODE = 2500  # Caracteres máximos por nó (controle de tokens)
MAX_QUERY_CHARS = 2000     # Caracteres máximos da consulta do usuário
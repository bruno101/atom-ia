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

# Parâmetros para consultas vetoriais
NUMBER_OF_VECTOR_QUERIES = 5     # Número de consultas vetoriais por busca
NODES_PER_VECTOR_QUERY = 3       # Nós retornados por consulta vetorial
MAX_NODES_VECTOR_QUERY = 15       # Máximo de nós vetoriais totais

# Parâmetros para consultas tradicionais (Elasticsearch)
NUMBER_OF_TRADITIONAL_QUERIES = 20  # Número de consultas tradicionais
NODES_PER_TRADITIONAL_QUERY = 3     # Nós retornados por consulta tradicional
MAX_NODES_TRADITIONAL_QUERY = 30    # Máximo de nós tradicionais totais

# Limitações de tamanho para otimização
MAX_CHARS_PER_NODE = 2500  # Caracteres máximos por nó (controle de tokens)
MAX_QUERY_CHARS = 1000     # Caracteres máximos da consulta do usuário
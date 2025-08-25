import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API = os.getenv("GEMINI_API")

EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
LLM_MODEL = "gemini-2.5-flash"

CHROMA_PATH = "./chroma_db_atom"
STORAGE_PATH = "./storage_atom"
COLLECTION_NAME = "documentos_atom"

NUMBER_OF_VECTOR_QUERIES = 10
NODES_PER_VECTOR_QUERY = 10
MAX_NODES_VECTOR_QUERY = 50
NUMBER_OF_TRADITIONAL_QUERIES = 20
NODES_PER_TRADITIONAL_QUERY = 3
MAX_NODES_TRADITIONAL_QUERY = 50

MAX_CHARS_PER_NODE = 2500
MAX_QUERY_CHARS = 1000
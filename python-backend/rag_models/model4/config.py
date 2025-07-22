import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API = os.getenv("GEMINI_API")

EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
LLM_MODEL = "gemini-2.5-flash"

CHROMA_PATH = "./chroma_db_atom"
STORAGE_PATH = "./storage_atom"
COLLECTION_NAME = "documentos_atom"

URL_ATOM = "http://localhost:63001"

NUMBER_OF_VECTOR_QUERIES = 6
NODES_PER_VECTOR_QUERY = 12
NUMBER_OF_TRADITIONAL_QUERIES = 2
NODES_PER_TRADITIONAL_QUERY = 6

MAX_CHARS_PER_NODE = 2500
MAX_QUERY_CHARS = 1000
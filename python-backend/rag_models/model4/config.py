import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API = os.getenv("GEMINI_API")
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
CHROMA_PATH = "./chroma_db_atom"
STORAGE_PATH = "./storage_atom"
COLLECTION_NAME = "documentos_atom"
MAX_NODES = 15
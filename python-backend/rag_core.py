import os, json, glob
import pandas as pd
import chromadb
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import (
    VectorStoreIndex, SimpleDirectoryReader, StorageContext,
    PromptTemplate, load_index_from_storage,
)
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.response_synthesizers import BaseSynthesizer, get_response_synthesizer

# Load environment variables
load_dotenv()
GROQ_API = os.getenv("GROQ_API")
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
CHROMA_PATH = "./chroma_db"
STORAGE_PATH = "./storage"
COLLECTION_NAME = "meus_documentos"

# Init LLM and embedding
llm = Groq(model="llama3-70b-8192", api_key=GROQ_API)
embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)

# Embedding wrapper for Chroma
class ChromaEmbeddingsWrapper:
    def __init__(self, model_name):
        self.model = HuggingFaceEmbedding(model_name=model_name)
    def __call__(self, input): return self.model.embed(input)
    def name(self): return "custom-chroma-embedding"

embed_model_chroma = ChromaEmbeddingsWrapper(EMBEDDING_MODEL)

# Setup Chroma
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME, embedding_function=embed_model_chroma
)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# Load or build index
has_index = os.path.exists(STORAGE_PATH) and bool(glob.glob(f"{STORAGE_PATH}/*.json"))
if not has_index:
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    csv_docs = SimpleDirectoryReader("csv").load_data()
    artigos_docs = SimpleDirectoryReader("artigos").load_data()
    documents = csv_docs + artigos_docs
    index = VectorStoreIndex.from_documents(documents, storage_context, embed_model)
    storage_context.persist(persist_dir=STORAGE_PATH)
else:
    storage_context = StorageContext.from_defaults(
        persist_dir=STORAGE_PATH, vector_store=vector_store
    )
    index = load_index_from_storage(storage_context, embed_model=embed_model)

# Prompt
qa_prompt = PromptTemplate(
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, answer the query.\n"
    "Responda em português.\n"
    """Somente responda em json
    Formato resposta em json
    {"data": {
      "livros": [
        {
          "titulo": "Titulo do livro",
          "categoria": "Categoria do livro",
          "Justificativa": "Porque recomenda"
        }
      ]
    }}
    Só recomende livros dessa base de dados"""
    "\nQuery: {query_str}\n"
    "Answer: "
)

# Query engine
class RAGStringQueryEngine(CustomQueryEngine):
    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: Groq
    qa_prompt: PromptTemplate

    def custom_query(self, query_str: str):
        nodes = self.retriever.retrieve(query_str)
        context_str = "\n\n".join([n.node.get_content() for n in nodes])
        response = self.llm.complete(
            self.qa_prompt.format(context_str=context_str, query_str=query_str)
        )
        return str(response)

retriever = index.as_retriever()
synthesizer = get_response_synthesizer(response_mode="compact", llm=llm)
query_engine_customize = RAGStringQueryEngine(
    retriever=retriever,
    response_synthesizer=synthesizer,
    llm=llm,
    qa_prompt=qa_prompt
)

# Validation + Formatting
try:
    df = pd.read_csv("csv/livros_mais_vendidos.csv")
except:
    df = pd.DataFrame(columns=["nome"])

def validando(resposta_json):
    for livro in resposta_json['data']['livros']:
        titulo = livro['titulo'].upper()
        if df.query("nome == @titulo").empty:
            raise Exception(f"Livro {titulo} não encontrado")

def formatando_respostas(response, consulta):
    prompt = f'''
    Formate a resposta para o usuário
    Você é um atendente da empresa buscante que vai recomendar livros com base na consulta.
    Use apenas os livros retornados.
    Consulta: {consulta}
    JSON: {response}
    '''
    return llm.complete(prompt=prompt).text

def pipeline_completo(consulta):
    response = query_engine_customize.custom_query(consulta)
    resposta_json = json.loads(response)
    validando(resposta_json)
    return formatando_respostas(response, consulta)

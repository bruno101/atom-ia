# MODELO LEGADO 1 - Sistema RAG com Groq/Llama3 (DESCONTINUADO)
# Este modelo foi substituído pelo model4 que usa Google Gemini
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
from llama_index.core import Settings
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.response_synthesizers import BaseSynthesizer, get_response_synthesizer
from llama_index.core import Document
from llama_index.core import Settings
from rapidfuzz import process
from fetch_documents import fetch_documents_from_db
from db_connection import fetch_slugs

# Carrega variáveis de ambiente
load_dotenv()
GROQ_API = os.getenv("GROQ_API")
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
CHROMA_PATH = "./chroma_db_atom"
STORAGE_PATH = "./storage_atom"
COLLECTION_NAME = "documentos_atom"

# Inicializando LLM e embedding
llm = Groq(model="llama3-8b-8192", api_key=GROQ_API)
Settings.llm = llm
embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
print(f"Modelo LLM carregado: {llm.model}")

class ChromaEmbeddingsWrapper:
    def __init__(self, model_name):
        self.model = HuggingFaceEmbedding(model_name=model_name)
    def __call__(self, input): return self.model.embed(input)
    def name(self): return "custom-chroma-embedding"

embed_model_chroma = ChromaEmbeddingsWrapper(EMBEDDING_MODEL)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME, embedding_function=embed_model_chroma
)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

debug = False

has_index = os.path.exists(STORAGE_PATH) and bool(glob.glob(f"{STORAGE_PATH}/*.json"))
if (not has_index) or debug == True:
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    documents = fetch_documents_from_db()
    #print(documents)
    print("Número de documentos", len(documents))
    Settings.embed_model = embed_model
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
    "{historico_str}"
    "Given the context information and not prior knowledge, answer the query.\n"
    "Responda em português.\n"
    """Somente responda em json
    Formato resposta em json
    {"data": {
      "paginas": [
        {
        "slug": "Slug da página recomendada",
        "title": "Titulo da página recomendada",
        "descricao": "Descrição resumida do conteúdo da página",
        "justificativa": "Motivo da recomendação e como essa página pode ajudar na pesquisa"
      }
      ]
    }}
    Só recomende se houver informações claras e diretas nos documentos; não use conhecimento prévio, mesmo que a resposta pareça óbvia. Se os documentos recuperados não contiverem evidências claras de relevância, não os recomende.
    Só recomende slugs dessa base de dados. Os slugs são identificadores técnicos. Eles **devem ser copiados exatamente como estão na base**, sem nenhuma alteração. NÃO insira, remova ou modifique hífens, acentos ou letras. Apenas use os slugs retornados pela base.
"""
    "\nQuery: {query_str}\n"
    "Answer: "
)

# Query engine

class RAGStringQueryEngine(CustomQueryEngine):
    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: Groq
    qa_prompt: PromptTemplate

    def custom_query(self, query_str: str, historico_str: str):
        
        MAX_CHARS_PER_NODE = 2500
        MAX_QUERY_CHARS = 900
    
        nodes = self.retriever.retrieve(query_str)
        print("nodes:\n\n", nodes, "\n\n")
        clipped_nodes = []
        for n in nodes:
            content = n.node.get_content()
            slug = n.node.metadata.get("slug", "[sem slug]")
            content = "Atenção! O seguinte é o slug da página, que, se necessário, deve ser copiado exatamente como está: ***" + slug + "***" + content
            clipped_content = content[:MAX_CHARS_PER_NODE]
            clipped_nodes.append(clipped_content)
        
        context_str = "\n\n".join(clipped_nodes)
        historico_limit = 900 - min(900, len(query_str))
        historico_instrucoes = "Histórico da conversa:\n" + historico_str[-historico_limit:] if historico_str and historico_limit>= 50 else ""
        print("Query size is: ", len(self.qa_prompt.format(context_str=context_str, query_str=query_str[:MAX_QUERY_CHARS], historico_str=historico_instrucoes)))
        #print("############\n\n"+self.qa_prompt.format(context_str=context_str, query_str=query_str[:MAX_QUERY_CHARS], historico_str=historico_instrucoes)+"\n\n############")
        response = self.llm.complete(
            self.qa_prompt.format(context_str=context_str, query_str=query_str[:MAX_QUERY_CHARS], historico_str=historico_instrucoes)
        )
        return str(response)

MAX_NODES = 10

retriever = index.as_retriever(similarity_top_k=MAX_NODES, with_similarity=True)
synthesizer = get_response_synthesizer(response_mode="compact", llm=llm)
query_engine_customize = RAGStringQueryEngine(
    retriever=retriever,
    response_synthesizer=synthesizer,
    llm=llm,
    qa_prompt=qa_prompt
)

# Validação + Formatação
try:
    slugs_validos = fetch_slugs()
    print("Número de slugs", len(slugs_validos))
except:
    raise Exception(f"Slugs não encontradas")

def corrigir_slug(slug_modelo, slugs_validos):
    print("Corrigindo: ", slug_modelo)
    melhor, score, _ = process.extractOne(slug_modelo, slugs_validos, score_cutoff=90)
    print("Corrigindo: ", melhor, score)
    return melhor if melhor else None

def validando(resposta_json, slugs_validos):
    for pagina in resposta_json['data']['paginas']:
        slug = pagina['slug']
        if slug not in slugs_validos:
            slug_corrigido = corrigir_slug(slug, slugs_validos)
            if slug_corrigido:
                pagina['slug'] = slug_corrigido
            else:
                raise ValueError(f"Slug '{slug}' não encontrado nem pôde ser corrigido.")
    return resposta_json

def formatando_respostas(resposta_json, consulta):
    prompt = f'''
Você é um assistente que recomenda páginas do AtoM para ajudar na pesquisa.

Consulta: "{consulta}"

Com base neste JSON:
{json.dumps(resposta_json)}

Recomende as páginas mais relevantes, explique por que são úteis e forneça o link completo no formato:
http://localhost:63001/index.php/{{slug}}

Responda em português, de forma clara e objetiva. Se não houver informações relevantes ou evidências claras no contexto acima, diga explicitamente: "Não há páginas relevantes encontradas com base nos dados disponíveis."
 Lembre-se de que você está respondendo a uma consulta do usuário.
'''
    #print("Prompt:", prompt)
    return llm.complete(prompt=prompt).text


def pipeline_completo(consulta, historico=None):
    print("LLM em uso no pipeline:", query_engine_customize.llm.model)
    response = query_engine_customize.custom_query(consulta, historico)
    resposta_json = json.loads(response)
    resposta_json_validada = validando(resposta_json, slugs_validos)
    resposta_textual = formatando_respostas(resposta_json_validada, consulta)
    #print("Paginas", [pagina for pagina in resposta_json_validada['data']['paginas']] )
    return {"resposta":resposta_textual, "links":[{"url": f"http://localhost:63001/index.php/{pagina['slug']}", "slug":pagina['slug'], "title":pagina['title'], "justificativa":pagina['justificativa'], "descricao":pagina['descricao']} for pagina in resposta_json_validada['data']['paginas']]}

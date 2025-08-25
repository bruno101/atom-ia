from dotenv import load_dotenv
import oracledb
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from sentence_transformers import SentenceTransformer
import os

load_dotenv()

# Oracle config
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_WALLET_DIR = os.getenv("ORACLE_WALLET_DIR")
ORACLE_DSN = os.getenv("ORACLE_DSN")
ORACLE_WALLET_PASSWORD = os.getenv("ORACLE_WALLET_PASSWORD")

model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")

Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-large-instruct")

def embed(query):
    return model.encode("query: " + query)

def connect_to_oracle():
    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN,
        config_dir=ORACLE_WALLET_DIR,
        wallet_location=ORACLE_WALLET_DIR,
        wallet_password=ORACLE_WALLET_PASSWORD,
    )
    
def search_closest_documents(conn, query_embedding, top_k=5):
    cursor = conn.cursor()
        
    vector_str = '[' + ','.join(f'{x:.6f}' for x in query_embedding) + ']'
        
    sql = f"""
        SELECT id, texto_original, VECTOR_DISTANCE(vetor, :query_vec, COSINE) AS dist
         FROM documentos
         ORDER BY dist ASC
         FETCH APPROXIMATE FIRST {top_k} ROWS ONLY
        """
    print("🧪 SQL gerado:", sql)

    cursor.execute(sql, query_vec=vector_str)
    results = cursor.fetchall()
    cursor.close()

    return results


def vector_query(consultas_vetoriais: list[str]):
        conn = connect_to_oracle()
        for idx, consulta_vetorial in enumerate(consultas_vetoriais):
            retrieved = search_closest_documents(conn, embed("query: " + consulta_vetorial), 10)
            
            sorted_retrieved = sorted(retrieved, key=lambda x: x[2], reverse=True)

            print(f"\n🔎 Top resultados para a consulta #{idx + 1}:\n\"{consulta_vetorial}\"\n")
            for rank, no in enumerate(sorted_retrieved[:10], start=1):
                score = 1 - no[2]
                slug = no[0]
                if rank == 1:
                    print(f"Melhor resultado para a consulta #{idx + 1}:\n\"{no[1]}\"\n")
                print(f"{rank:>2}. {slug} - Retriever Score: {no[2]:.4f}" if score is not None else f"{rank:>2}. {no[0]} - Score: N/A")
            
consultas_vetoriais = """História judeus Brasil colonização imigração, 
    educação no Império do Brasil, 
    Comunidade judaica Brasil cultura tradições sinagogas, 
    alforria, 
    Sítio Picapau Amarelo literatura infantil brasileira,
    Personagens Sítio Picapau Amarelo Emília Visconde,
    Adaptações Sítio Picapau Amarelo televisão cinema,
    Folclore brasileiro fantasia Sítio Picapau Amarelo,
    Sítio Picapau Amarelo Rede Globo elenco,
    Impacto cultural Sítio Picapau Amarelo educação"""

vector_query(consultas_vetoriais.split(","))

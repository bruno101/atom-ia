# Arquivo de teste para integração com Oracle Database (DESCONTINUADO)
# Este código foi usado para testes com Oracle Vector DB mas não é mais utilizado
from dotenv import load_dotenv
import oracledb
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from sentence_transformers import SentenceTransformer
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Oracle Database (não utilizadas no sistema atual)
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_WALLET_DIR = os.getenv("ORACLE_WALLET_DIR")
ORACLE_DSN = os.getenv("ORACLE_DSN")
ORACLE_WALLET_PASSWORD = os.getenv("ORACLE_WALLET_PASSWORD")

# Inicializa modelo de embedding para testes
model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")

# Configura modelo de embedding global do LlamaIndex
Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-large-instruct")

def embed(query):
    """Gera embedding para uma consulta usando o modelo SentenceTransformer"""
    return model.encode("query: " + query)

def connect_to_oracle():
    """Estabelece conexão com Oracle Database usando wallet
    
    Returns:
        oracledb.Connection: Conexão ativa com o Oracle
    """
    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN,
        config_dir=ORACLE_WALLET_DIR,
        wallet_location=ORACLE_WALLET_DIR,
        wallet_password=ORACLE_WALLET_PASSWORD,
    )
    
def search_closest_documents(conn, query_embedding, top_k=5):
    """Busca documentos mais similares usando busca vetorial no Oracle
    
    Args:
        conn: Conexão com Oracle Database
        query_embedding: Vetor de embedding da consulta
        top_k (int): Número de documentos mais similares a retornar
        
    Returns:
        list: Lista de tuplas (id, texto, distância)
    """
    cursor = conn.cursor()
    
    # Converte o embedding para formato string aceito pelo Oracle
    vector_str = '[' + ','.join(f'{x:.6f}' for x in query_embedding) + ']'
        
    # SQL para busca vetorial usando VECTOR_DISTANCE com similaridade cosseno
    sql = f"""
        SELECT id, texto_original, VECTOR_DISTANCE(vetor, :query_vec, COSINE) AS dist
         FROM documentos
         ORDER BY dist ASC
         FETCH APPROXIMATE FIRST {top_k} ROWS ONLY
        """
    print("🧪 SQL gerado:", sql)

    # Executa a query com o vetor como parâmetro
    cursor.execute(sql, query_vec=vector_str)
    results = cursor.fetchall()
    cursor.close()

    return results


def vector_query(consultas_vetoriais: list[str]):
    """Executa consultas vetoriais no Oracle e exibe resultados
    
    Args:
        consultas_vetoriais (list[str]): Lista de consultas para testar
    """
    conn = connect_to_oracle()
    
    for idx, consulta_vetorial in enumerate(consultas_vetoriais):
        # Busca documentos similares para cada consulta
        retrieved = search_closest_documents(conn, embed("query: " + consulta_vetorial), 10)
        
        # Ordena por distância (menor distância = maior similaridade)
        sorted_retrieved = sorted(retrieved, key=lambda x: x[2], reverse=True)

        print(f"\n🔎 Top resultados para a consulta #{idx + 1}:\n\"{consulta_vetorial}\"\n")
        
        # Exibe os resultados formatados
        for rank, no in enumerate(sorted_retrieved[:10], start=1):
            score = 1 - no[2]  # Converte distância para score de similaridade
            slug = no[0]
            
            # Mostra o melhor resultado completo
            if rank == 1:
                print(f"Melhor resultado para a consulta #{idx + 1}:\n\"{no[1]}\"\n")
            
            # Lista todos os resultados com scores
            print(f"{rank:>2}. {slug} - Retriever Score: {no[2]:.4f}" if score is not None else f"{rank:>2}. {no[0]} - Score: N/A")
            
# Consultas de teste para validar o sistema vetorial
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

# Executa os testes (descomente para usar)
# vector_query(consultas_vetoriais.split(","))

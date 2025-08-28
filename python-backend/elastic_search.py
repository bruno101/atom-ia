# Módulo para integração com Elasticsearch
# Executa buscas tradicionais (lexicais) no índice do AtoM
import requests
import json
import os
from dotenv import load_dotenv

# Carrega configurações do ambiente
load_dotenv()

# Configurações do Elasticsearch
BASE_URL = os.getenv('URL_ELASTIC_SEARCH', 'http://elasticsearch:9200')
INDEX_NAME = "atom_qubitinformationobject"  # Índice padrão do AtoM
url = f"{BASE_URL}/{INDEX_NAME}/_msearch"    # Endpoint para múltiplas buscas
headers = {"Content-Type": "application/x-ndjson"}  # Formato NDJSON para msearch


def fetch_from_elastic_search(expressions: list[str], number_results: int):
    """Executa múltiplas buscas no Elasticsearch usando query_string
    
    Args:
        expressions (list[str]): Lista de expressões para buscar
        number_results (int): Número máximo de resultados por expressão
        
    Returns:
        list: Lista de documentos únicos encontrados
    """
    msearch_payload = ""  # Payload para múltiplas buscas em formato NDJSON
    
    # Constrói o payload para cada expressão
    for expression in expressions:
        # Cabeçalho especificando o índice
        header = {"index": INDEX_NAME}
        
        # Query usando query_string para busca textual
        query = {
            "query": {
               "query_string": {
                    "query": f'"{expression}"'  # Busca exata com aspas
                }
            },
            "size": number_results  # Limita número de resultados
        }
        
        # Adiciona header e query ao payload NDJSON
        msearch_payload += json.dumps(header) + "\n"
        msearch_payload += json.dumps(query) + "\n"

    print("the search payload: ", msearch_payload)  # Debug do payload

    all_hits = []  # Lista para acumular todos os resultados
    try:    
        # Executa a requisição POST para o Elasticsearch
        response = requests.post(url, headers=headers, data=msearch_payload.encode('utf-8'))
        response.raise_for_status()  # Lança exceção se status HTTP for erro
        
        parsed_response = response.json()

        # Processa cada resposta individual
        for sub_response in parsed_response["responses"]:
            if not sub_response.get("error"):
                # Adiciona os hits de cada busca à lista geral
                all_hits.extend(sub_response["hits"]["hits"])

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com o Elasticsearch: {e}")
        return []  # Retorna lista vazia em caso de erro de conexão
    except (KeyError, IndexError) as e:
        print(f"Erro ao analisar a resposta do Elasticsearch: {e}")
        print(f"Resposta recebida: {response.text}")
        return []  # Retorna lista vazia em caso de erro de parsing
        
    # Remove duplicatas usando o _id como chave única
    unique_results = {hit["_id"]: hit for hit in all_hits}.values()
    
    return list(unique_results)

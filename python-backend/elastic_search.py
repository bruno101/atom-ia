import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('URL_ELASTIC_SEARCH', 'http://elasticsearch:9200')
INDEX_NAME = "atom_qubitinformationobject" 
url = f"{BASE_URL}/{INDEX_NAME}/_msearch"  
headers = {"Content-Type": "application/x-ndjson"}


def fetch_from_elastic_search(expressions: list[str], number_results: int):

    msearch_payload = "" 
    for expression in expressions:
        header = {"index": INDEX_NAME}
        
        query = {
            "query": {
               "query_string": {
                    "query": f'"{expression}"'
                }
            },
            "size": number_results
        }
        
        msearch_payload += json.dumps(header) + "\n"
        msearch_payload += json.dumps(query) + "\n"

    print("the search payload: ", msearch_payload) 

    all_hits = []
    try:    
        response = requests.post(url, headers=headers, data=msearch_payload.encode('utf-8'))
        response.raise_for_status()  
        
        parsed_response = response.json()

        for sub_response in parsed_response["responses"]:
            if not sub_response.get("error"):
                all_hits.extend(sub_response["hits"]["hits"])

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com o Elasticsearch: {e}")
        return [] 
    except (KeyError, IndexError) as e:
        print(f"Erro ao analisar a resposta do Elasticsearch: {e}")
        print(f"Resposta recebida: {response.text}")
        return []
        
    unique_results = {hit["_id"]: hit for hit in all_hits}.values()
    
    return list(unique_results)

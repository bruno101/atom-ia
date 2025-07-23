import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


url = f"{os.getenv('URL_ELASTIC_SEARCH', 'http://elasticsearch:9200')}/atom_qubitinformationobject/_search"
headers = {"Content-Type": "application/json"}


def fetch_from_elastic_search(expressions: list[str], number_results: int):
    
    all_results = []
    
    for expression in expressions:
        
        try:
            payload = {
                "query": {
                    "query_string": {
                        "query": expression
                    }
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            parsed_response = response.json()
            results = parsed_response['hits']['hits'][:number_results]
            all_results = list(all_results) + list(results)
        except Exception as e:
            print("Erro buscando: ", expression, "\n", e)
        
    return all_results

import json
import re
from datetime import datetime
from typing import Dict, List, Any
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class URLProcessor:
    def __init__(self):
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_academic_info(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Usa LLM para extrair informações acadêmicas do conteúdo web
        """
        content = scraped_data.get('content', '')
        title = scraped_data.get('title', '')
        url = scraped_data.get('url', '')
        
        prompt = f"""
        Analise o seguinte conteúdo de uma página web e extraia informações acadêmicas relevantes:
        
        TÍTULO: {title}
        URL: {url}
        CONTEÚDO: {content[:3000]}...
        
        Extraia as seguintes informações em formato JSON:
        1. assunto_principal: O tema/assunto principal do conteúdo
        2. autores: Lista de nomes de autores mencionados (se houver)
        3. ano_publicacao: Ano de publicação se mencionado (número)
        4. palavras_chave: Lista de 3-5 palavras-chave relevantes
        5. input_busca: Termos que alguém usaria para buscar este conteúdo
        
        Responda APENAS com um JSON válido no formato:
        {{
            "assunto_principal": "texto",
            "autores": ["autor1", "autor2"],
            "ano_publicacao": 2024,
            "palavras_chave": ["palavra1", "palavra2"],
            "input_busca": "termos de busca"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extrai JSON da resposta
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                extracted_info = json.loads(json_match.group())
            else:
                # Fallback se não conseguir extrair JSON
                extracted_info = {
                    "assunto_principal": title or "Conteúdo web",
                    "autores": [],
                    "ano_publicacao": datetime.now().year,
                    "palavras_chave": [],
                    "input_busca": title or "pesquisa web"
                }
            
            return extracted_info
            
        except Exception as e:
            print(f"Erro ao processar com LLM: {e}")
            # Fallback em caso de erro
            return {
                "assunto_principal": title or "Conteúdo web",
                "autores": [],
                "ano_publicacao": datetime.now().year,
                "palavras_chave": [],
                "input_busca": title or "pesquisa web"
            }
    
    def process_scraped_data(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados do web scraping e gera JSON estruturado para consulta
        """
        print("🔄 Iniciando processamento dos dados...")
        
        if scraped_data.get('status') == 'error':
            raise Exception(f"Erro no scraping: {scraped_data.get('error')}")
        
        print("🤖 Extraindo informações com LLM...")
        # Extrai informações usando LLM
        extracted_info = self.extract_academic_info(scraped_data)
        print("✅ Extração LLM concluída")
        
        # Gera ID único com data atual
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_id = f"AUTO_AUDIT_QUERY-{current_date}"
        
        print("📝 Montando JSON estruturado...")
        # Monta JSON estruturado
        structured_query = {
            "query_id": query_id,
            "search_target": "ACADEMIC_LITERATURE",
            "conteúdo": scraped_data.get('content', ''),
            "url": scraped_data.get('url', ''),
            "input_busca": extracted_info.get('input_busca', ''),
            "filters": {
                "main_subject": extracted_info.get('assunto_principal', ''),
                "author_names": extracted_info.get('autores', []),
                "publication_year_min": extracted_info.get('ano_publicacao', datetime.now().year),
                "keywords_must_contain": extracted_info.get('palavras_chave', [])
            },
            "sort_by": "relevance",
            "max_results": 10,
            "return_fields": ["title", "abstract_snippet", "publication_link"]
        }
        print("✅ JSON estruturado criado com sucesso")
        
        return structured_query

def process_url_data(scraped_json: str) -> Dict[str, Any]:
    """
    Função principal para processar dados de URL
    """
    processor = URLProcessor()
    scraped_data = json.loads(scraped_json) if isinstance(scraped_json, str) else scraped_json
    return processor.process_scraped_data(scraped_data)
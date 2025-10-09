import json
import re
from datetime import datetime
from typing import Dict, List, Any
import google.generativeai as genai
import os
from dotenv import load_dotenv
from processors.youtube_url_processor import process_youtube_url_data

load_dotenv()

class URLProcessor:
    def __init__(self):
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    def extract_info(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Usa LLM para extrair informações do conteúdo web
        """
        content = scraped_data.get('content', '')
        title = scraped_data.get('title', '')
        url = scraped_data.get('url', '')
        
        prompt = f"""
        Analise o seguinte conteúdo de uma página web e extraia informações acadêmicas relevantes:
        
        TÍTULO: {title}
        URL: {url}
        CONTEÚDO: {content[:3000]}...
        
        Extraia e formate as seguintes informações em JSON:
        1. Assunto Principal: Área principal
        2. Termos-Chave: 3-5 termos essenciais para a busca de arquivos relacionados
        3. Resumo: Resumo detalhado com introdução sobre os assuntos tratados (5-7 frases)

        Responda APENAS com um JSON válido no seguinte formato:
        {{
            "assunto_principal": "área de estudo",
            "termos_chave": ["termo1", "termo2", "termo3"],
            "resumo": "Este documento aborda [assunto principal] e apresenta [principais tópicos]."
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
                    "termos_chave": [],
                    "resumo": ""
                }
            
            return extracted_info
            
        except Exception as e:
            print(f"Erro ao processar com LLM: {e}")
            # Fallback em caso de erro
            return {
                "assunto_principal": title or "Conteúdo web",
                "termos_chave": [],
                "resumo": ""
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
        extracted_info = self.extract_info(scraped_data)
        print("✅ Extração LLM concluída")
        
        # Gera ID único com data atual
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_id = f"AUTO_AUDIT_QUERY-{current_date}"
        
        print("📝 Montando JSON estruturado...")
        # Monta JSON estruturado
        structured_query = {
            "query_id": query_id,
            "resumo": extracted_info["resumo"],
            "input_busca": "",
            "assunto_principal": extracted_info["assunto_principal"],
            "termos_chave": extracted_info["termos_chave"]
        }
        print("✅ JSON estruturado criado com sucesso")
        
        return structured_query

def process_url_data(scraped_json: str) -> Dict[str, Any]:
    """
    Função principal para processar dados de URL
    """
    scraped_data = json.loads(scraped_json) if isinstance(scraped_json, str) else scraped_json
    url = scraped_data.get('url', '')
    
    # Verifica se é URL do YouTube
    if 'youtube.com/watch?' in url or 'youtu.be/' in url:
        return process_youtube_url_data(url)
    
    # Processa URLs normais
    processor = URLProcessor()
    return processor.process_scraped_data(scraped_data)
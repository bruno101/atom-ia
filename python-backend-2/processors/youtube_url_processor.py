import json
import re
from datetime import datetime
from typing import Dict, Any
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

class YouTubeURLProcessor:
    def __init__(self):
        self.client = genai.Client(
        api_key=os.getenv("GEMINI_API"),
    )
    
    def extract_info(self, youtube_url: str) -> Dict[str, Any]:
        """
        Usa LLM para extrair informações do vídeo do YouTube
        """
        prompt = f"""
        Analise o vídeo do YouTube na URL: {youtube_url}
        
        Extraia e formate as seguintes informações em JSON:
        1. Assunto Principal: Área principal do vídeo
        2. Termos-Chave: 3-5 termos essenciais para a busca de arquivos relacionados
        3. Resumo: Resumo detalhado com introdução sobre os assuntos tratados (5-7 frases)

        Responda APENAS com um JSON válido no seguinte formato:
        {{
            "assunto_principal": "assunto do vídeo",
            "termos_chave": ["termo1", "termo2", "termo3"],
            "resumo": "Este vídeo aborda [assunto principal] e apresenta [principais tópicos]."
        }}
        """

        print("Prompt enviada: ")
        print(prompt)
        
        try:
            model = "gemini-2.5-pro"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                        file_data=types.FileData(file_uri=youtube_url),
                        video_metadata=types.VideoMetadata(
                            start_offset="10s",
                            end_offset="70s",
                            fps=1
                        )
                    ),
                    types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            tools = [{'google_search': {}}]
            generate_content_config = types.GenerateContentConfig(
                thinking_config = types.ThinkingConfig(
                    thinking_budget=-1,
                ),
                tools=tools,
            )

            full_response = ""
            for chunk in self.client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                print(chunk.text, end="")
                full_response += chunk.text
            
            json_match = re.search(r'\{.*\}', full_response, re.DOTALL)
            if json_match:
                extracted_info = json.loads(json_match.group())
            else:
                extracted_info = {
                    "assunto_principal": "Vídeo do YouTube",
                    "termos_chave": [],
                    "resumo": ""
                }
            
            return extracted_info
            
        except Exception as e:
            print(f"Erro ao processar com LLM: {e}")
            return {
                "assunto_principal": "Vídeo do YouTube",
                "termos_chave": [],
                "resumo": ""
            }
    
    def process_youtube_url(self, youtube_url: str) -> Dict[str, Any]:
        """
        Processa URL do YouTube e gera JSON estruturado para consulta
        """
        print("🔄 Iniciando processamento do vídeo do YouTube...")
        
        print("🤖 Extraindo informações com LLM...")
        extracted_info = self.extract_info(youtube_url)
        print("✅ Extração LLM concluída")
        
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_id = f"AUTO_AUDIT_QUERY-{current_date}"
        
        print("📝 Montando JSON estruturado...")
        structured_query = {
            "query_id": query_id,
            "resumo": extracted_info["resumo"],
            "input_busca": "",
            "assunto_principal": extracted_info["assunto_principal"],
            "termos_chave": extracted_info["termos_chave"]
        }
        print("✅ JSON estruturado criado com sucesso")
        
        return structured_query

def process_youtube_url_data(youtube_url: str) -> Dict[str, Any]:
    """
    Função principal para processar URL do YouTube
    """
    processor = YouTubeURLProcessor()
    return processor.process_youtube_url(youtube_url)

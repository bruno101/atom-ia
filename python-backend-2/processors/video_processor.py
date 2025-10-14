import json
import tempfile
import os
import subprocess
import time
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import imageio_ffmpeg

load_dotenv()

def analyze_video_with_gemini(video_file):
    """Analisa vídeo diretamente com Gemini e gera JSON estruturado"""
    try:
        print("[DEBUG] Configurando Gemini API...")
        genai.configure(api_key=os.getenv("GEMINI_API"))
        model = genai.GenerativeModel('gemini-2.0-flash-lite')

        print("[DEBUG] Salvando vídeo temporário...")
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_file.write(video_file)
            temp_path = temp_file.name
        print(f"[DEBUG] Vídeo salvo em: {temp_path}")
        
        trimmed_path = temp_path.replace('.mp4', '_trimmed.mp4')
        print(f"[DEBUG] Cortando vídeo (10s-70s) e comprimindo...")
        
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([
            ffmpeg_exe, '-i', temp_path, '-ss', '10', '-t', '60',
            '-c:v', 'libx264', '-crf', '28', '-preset', 'fast',
            '-y', trimmed_path
        ], check=True, capture_output=True)
        
        print(f"[DEBUG] Vídeo cortado salvo em: {trimmed_path}")
        os.unlink(temp_path)
        
        print("[DEBUG] Fazendo upload para Gemini...")
        video_upload = genai.upload_file(trimmed_path)
        print(f"[DEBUG] Upload concluído: {video_upload.name}")
        
        print("[DEBUG] Aguardando processamento do vídeo...")
        while video_upload.state.name == "PROCESSING":
            time.sleep(2)
            video_upload = genai.get_file(video_upload.name)
        
        if video_upload.state.name == "FAILED":
            raise ValueError(f"Falha no processamento do vídeo")
        
        print(f"[DEBUG] Vídeo pronto para análise (estado: {video_upload.state.name})")
        
        prompt = """
        Analise este arquivo de vídeo e extraia as informações solicitadas:

        Extraia e formate as seguintes informações em JSON:
        1. Assunto Principal: Área principal do vídeo
        2. Termos-Chave: 3-5 termos essenciais para a busca de conteúdo relacionado
        3. Resumo: Resumo detalhado sobre o que foi discutido no vídeo (5-7 frases)

        Responda APENAS com um JSON válido no seguinte formato:
        {
            "assunto_principal": "área de estudo",
            "termos_chave": ["termo1", "termo2", "termo3"],
            "resumo": "Este vídeo aborda [assunto principal] e apresenta [principais tópicos]."
        }
        """
        
        print("[DEBUG] Gerando análise com Gemini...")
        response = model.generate_content([prompt, video_upload])
        print(f"[DEBUG] Resposta recebida: {response.text[:200]}...")
        
        genai.delete_file(video_upload.name)
        os.unlink(trimmed_path)
        
        json_text = response.text.strip()
        print(f"[DEBUG] Processando JSON...")
        
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0]
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0]
        
        result = json.loads(json_text.strip())
        print(f"[DEBUG] ✅ Análise concluída com sucesso")
        return result
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Erro ao parsear JSON: {e}")
        print(f"[DEBUG] Texto recebido: {response.text if 'response' in locals() else 'N/A'}")
        if 'trimmed_path' in locals() and os.path.exists(trimmed_path):
            os.unlink(trimmed_path)
        return {
            "assunto_principal": "Arquivo de vídeo",
            "termos_chave": ["vídeo", "conteúdo", "análise"],
            "resumo": "Arquivo de vídeo processado. Não foi possível extrair conteúdo detalhado para análise."
        }
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Erro ffmpeg: {e.stderr.decode()}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        if 'trimmed_path' in locals() and os.path.exists(trimmed_path):
            os.unlink(trimmed_path)
        return {
            "assunto_principal": "Arquivo de vídeo",
            "termos_chave": ["vídeo", "conteúdo", "análise"],
            "resumo": "Arquivo de vídeo processado. Não foi possível extrair conteúdo detalhado para análise."
        }
    except Exception as e:
        print(f"[ERROR] Erro durante processamento: {type(e).__name__}: {str(e)}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        if 'trimmed_path' in locals() and os.path.exists(trimmed_path):
            os.unlink(trimmed_path)
        
        return {
            "assunto_principal": "Arquivo de vídeo",
            "termos_chave": ["vídeo", "conteúdo", "análise"],
            "resumo": "Arquivo de vídeo processado. Não foi possível extrair conteúdo detalhado para análise."
        }

def create_search_json(metadata):
    """Cria JSON estruturado para busca"""
    if not metadata:
        raise ValueError("Metadata é None ou vazia")
    
    current_date = datetime.now().strftime("%Y%m%d")
    
    assunto = metadata.get('assunto_principal', 'Vídeo processado')
    termos = metadata.get('termos_chave', ['vídeo'])
    resumo = metadata.get('resumo', 'Vídeo processado sem resumo disponível')
    
    input_busca = f"Procure informações sobre {assunto} relacionadas aos termos {', '.join(termos)}."
    
    return {
        "query_id": f"AUTO_VIDEO_QUERY-{current_date}",
        "resumo": resumo,
        "input_busca": input_busca,
        "assunto_principal": assunto,
        "termos_chave": termos
    }

def processVideoBackend(video_file):
    """Processa arquivo de vídeo e retorna JSON estruturado para busca"""
    try:
        metadata = analyze_video_with_gemini(video_file)
        search_json = create_search_json(metadata)
        return search_json
        
    except Exception as error:
        return {
            "query_id": f"ERROR_VIDEO_QUERY-{datetime.now().strftime('%Y%m%d')}",
            "resumo": "Erro no processamento do vídeo",
            "input_busca": "Pesquise sobre o vídeo anexado",
            "assunto_principal": "Arquivo de vídeo",
            "termos_chave": ["vídeo", "transcrição", "pesquisa"]
        }

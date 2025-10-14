import json
import tempfile
import os
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

def show_progress(current, total, step):
    """Exibe barra de progresso no terminal"""
    percentage = round((current / total) * 100)
    bar = '█' * (percentage // 5) + '░' * (20 - percentage // 5)
    print(f"\r[{bar}] {percentage}% - {step}", end='', flush=True)

def analyze_image_with_gemini(image_file):
    """Analisa imagem diretamente com Gemini e gera JSON estruturado"""
    print(f"🤖 Analisando imagem diretamente com Gemini...")
    
    show_progress(1, 3, 'Configurando Gemini...')
    
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API"))
        
        show_progress(2, 3, 'Enviando imagem para análise...')
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(image_file)
            temp_path = temp_file.name
        
        with open(temp_path, 'rb') as f:
            image_upload = client.files.upload(file=f, config={'mime_type': 'image/jpeg'})
        
        prompt = """
        Analise esta imagem e extraia as informações solicitadas:

        Extraia e formate as seguintes informações em JSON:
        1. Assunto Principal: Área principal da imagem
        2. Termos-Chave: 3-5 termos essenciais para a busca de conteúdo relacionado
        3. Resumo: Resumo detalhado sobre o que está representado na imagem (5-7 frases)

        Responda APENAS com um JSON válido no seguinte formato:
        {
            "assunto_principal": "área de estudo",
            "termos_chave": ["termo1", "termo2", "termo3"],
            "resumo": "Esta imagem mostra [assunto principal] e apresenta [principais elementos]."
        }
        """
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=[prompt, image_upload]
        )
        
        client.files.delete(name=image_upload.name)
        os.unlink(temp_path)
        
        json_text = response.text.strip()
        if json_text.startswith('```json'):
            json_text = json_text[7:-3]
        elif json_text.startswith('```'):
            json_text = json_text[3:-3]
        
        return json.loads(json_text)
        
    except Exception as e:
        print(f"❌ Erro na análise com Gemini: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        
        return {
            "assunto_principal": "Arquivo de imagem",
            "termos_chave": ["imagem", "conteúdo", "análise"],
            "resumo": "Arquivo de imagem processado. Não foi possível extrair conteúdo detalhado para análise."
        }

def create_search_json(metadata):
    """Cria JSON estruturado para busca"""
    print(f"🔍 Criando JSON. Metadata válida: {metadata is not None}")
    
    show_progress(3, 3, 'Gerando JSON de busca...')
    
    if not metadata:
        raise ValueError("Metadata é None ou vazia")
    
    current_date = datetime.now().strftime("%Y%m%d")
    
    assunto = metadata.get('assunto_principal', 'Imagem processada')
    termos = metadata.get('termos_chave', ['imagem'])
    resumo = metadata.get('resumo', 'Imagem processada sem resumo disponível')
    
    input_busca = f"Procure informações sobre {assunto} relacionadas aos termos {', '.join(termos)}."
    
    search_json = {
        "query_id": f"AUTO_IMAGE_QUERY-{current_date}",
        "resumo": resumo,
        "input_busca": input_busca,
        "assunto_principal": assunto,
        "termos_chave": termos
    }
    
    return search_json

def processImageBackend(image_file):
    """Processa arquivo de imagem e retorna JSON estruturado para busca"""
    print("\n🔄 Iniciando processamento da imagem no backend...")
    print(f"📊 Tamanho do arquivo: {len(image_file) if image_file else 'None'} bytes")
    
    try:
        # Etapa 1: Analisar imagem diretamente com Gemini
        print("🤖 Analisando imagem com Gemini...")
        metadata = analyze_image_with_gemini(image_file)
        print(f"📋 Metadata gerada: {metadata}")
        
        # Etapa 2: Criar JSON de busca
        print("🔍 Criando JSON de busca...")
        search_json = create_search_json(metadata)
        
        print("\n✅ Imagem processada com sucesso\n")
        return search_json
        
    except Exception as error:
        import traceback
        print(f"\n❌ Erro ao processar imagem: {str(error)}")
        print(f"🔍 Traceback completo: {traceback.format_exc()}")
        return {
            "query_id": f"ERROR_IMAGE_QUERY-{datetime.now().strftime('%Y%m%d')}",
            "resumo": "Erro no processamento da imagem",
            "input_busca": "Pesquise sobre a imagem anexada",
            "assunto_principal": "Arquivo de imagem",
            "termos_chave": ["imagem", "análise", "pesquisa"]
        }

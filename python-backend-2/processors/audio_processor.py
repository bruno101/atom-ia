# Processador de arquivos de áudio
# Analisa áudio com Gemini e gera JSON estruturado para busca
import json
import tempfile
import os
import time
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

def show_progress(current, total, step):
    """Exibe barra de progresso visual no terminal
    
    Args:
        current (int): Passo atual
        total (int): Total de passos
        step (str): Descrição do passo atual
    """
    percentage = round((current / total) * 100)
    bar = '█' * (percentage // 5) + '░' * (20 - percentage // 5)
    print(f"\r[{bar}] {percentage}% - {step}", end='', flush=True)

def analyze_audio_with_gemini(audio_file):
    """Analisa áudio com Gemini e extrai informações estruturadas
    
    Args:
        audio_file (bytes): Conteúdo do arquivo de áudio
        
    Returns:
        dict: JSON com assunto_principal, termos_chave e resumo
    """
    print(f"🤖 Analisando áudio diretamente com Gemini...")
   
    show_progress(1, 3, 'Configurando Gemini...')
   
    try:
        # Inicializa cliente Gemini
        client = genai.Client(api_key=os.getenv("GEMINI_API"))
        
        show_progress(2, 3, 'Enviando áudio para análise...')
        
        # Cria arquivo temporário para upload
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as temp_file:
            temp_file.write(audio_file)
            temp_path = temp_file.name
        
        # Faz upload do áudio para Gemini File API
        with open(temp_path, 'rb') as f:
            audio_upload = client.files.upload(file=f, config={'mime_type': 'audio/m4a'})
        
        # Prompt para extração estruturada de informações
        prompt = """
        Analise este arquivo de áudio e extraia as informações solicitadas:
        Extraia e formate as seguintes informações em JSON:
        1. Assunto Principal: Área principal do áudio
        2. Termos-Chave: 3-5 termos essenciais para a busca de conteúdo relacionado
        3. Resumo: Resumo detalhado sobre o que foi discutido no áudio (5-7 frases)
        Responda APENAS com um JSON válido no seguinte formato:
        {
            "assunto_principal": "área de estudo",
            "termos_chave": ["termo1", "termo2", "termo3"],
            "resumo": "Este áudio aborda [assunto principal] e apresenta [principais tópicos]."
        }
        """
        
        # Gera análise com Gemini 2.0 Flash Lite
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=[prompt, audio_upload]
        )
        
        # Limpa recursos temporários
        client.files.delete(name=audio_upload.name)
        os.unlink(temp_path)
        
        # Extrai e limpa JSON da resposta
        json_text = response.text.strip() if hasattr(response, 'text') else str(response)
        if json_text.startswith('```json'):
            json_text = json_text[7:-3]
        elif json_text.startswith('```'):
            json_text = json_text[3:-3]
        
        return json.loads(json_text)
    
    except Exception as e:
        print(f"❌ Erro na análise com Gemini: {e}")
        # Limpa arquivo temporário em caso de erro
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        
        # Retorna fallback em caso de erro
        return {
            "assunto_principal": "Arquivo de áudio",
            "termos_chave": ["áudio", "conteúdo", "análise"],
            "resumo": f"Arquivo de áudio processado. Erro: {str(e)}"
        }

def create_search_json(metadata):
    """Cria JSON estruturado para busca a partir dos metadados
    
    Args:
        metadata (dict): Metadados extraídos do áudio
        
    Returns:
        dict: JSON estruturado para busca no sistema RAG
    """
    print(f"🔍 Criando JSON. Metadata válida: {metadata is not None}")
    
    show_progress(3, 3, 'Gerando JSON de busca...')
    
    if not metadata:
        raise ValueError("Metadata é None ou vazia")
    
    current_date = datetime.now().strftime("%Y%m%d")
    
    # Extrai informações dos metadados
    assunto = metadata.get('assunto_principal', 'Áudio processado')
    termos = metadata.get('termos_chave', ['áudio'])
    resumo = metadata.get('resumo', 'Áudio processado sem resumo disponível')
    
    # Cria query de busca natural
    input_busca = f"Procure informações sobre {assunto} relacionadas aos termos {', '.join(termos)}."
    
    search_json = {
        "query_id": f"AUTO_AUDIO_QUERY-{current_date}",
        "resumo": resumo,
        "input_busca": input_busca,
        "assunto_principal": assunto,
        "termos_chave": termos
    }
    
    return search_json

def processAudioBackend(audio_file):
    """Processa arquivo de áudio e retorna JSON estruturado para busca
    
    Args:
        audio_file (bytes): Conteúdo do arquivo de áudio
        
    Returns:
        dict: JSON estruturado com query_id, resumo, input_busca, assunto_principal e termos_chave
    """
    print("\n🔄 Iniciando processamento do áudio no backend...")
    print(f"📊 Tamanho do arquivo: {len(audio_file) if audio_file else 'None'} bytes")
    
    try:
        # Etapa 1: Analisar áudio com Gemini
        print("🤖 Analisando áudio com Gemini...")
        metadata = analyze_audio_with_gemini(audio_file)
        print(f"📋 Metadata gerada: {metadata}")
        
        # Etapa 2: Criar JSON estruturado para busca
        print("🔍 Criando JSON de busca...")
        search_json = create_search_json(metadata)
        
        print("\n✅ Áudio processado com sucesso\n")
        return search_json
        
    except Exception as error:
        import traceback
        print(f"\n❌ Erro ao processar áudio: {str(error)}")
        print(f"🔍 Traceback completo: {traceback.format_exc()}")
        # Retorna JSON de fallback em caso de erro
        return {
            "query_id": f"ERROR_AUDIO_QUERY-{datetime.now().strftime('%Y%m%d')}",
            "resumo": "Erro no processamento do áudio",
            "input_busca": "Pesquise sobre o áudio anexado",
            "assunto_principal": "Arquivo de áudio",
            "termos_chave": ["áudio", "transcrição", "pesquisa"]
        }
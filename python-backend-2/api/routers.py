# Rotas da API - define endpoints HTTP para o chatbot
# Implementa endpoints para chat síncrono e streaming
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from sse_starlette.sse import EventSourceResponse
from .models import ConsultaRequest, ConsultaMultimodalRequest, ConsultaResponse, URLRequest
from .api_service import handle_stream, handle_multimodal_stream, handle_transcribe_stream
import logging

# Configura roteador com prefixo vazio e tag para documentação
router = APIRouter(prefix="", tags=["Chatbot"])
logger = logging.getLogger(__name__)


@router.post("/ask-stream") 
async def ask_stream(request: Request, req: ConsultaRequest):
    """Endpoint para consultas com streaming de progresso (SSE)
    
    Args:
        request (Request): Requisição HTTP para controle de conexão
        req (ConsultaRequest): Dados da consulta
        
    Returns:
        EventSourceResponse: Stream de eventos SSE com progresso
    """
    # Cria gerador de eventos para streaming
    event_generator = handle_stream(request, req, "thinking")
    # Retorna resposta SSE (Server-Sent Events)
    return EventSourceResponse(event_generator)

@router.post("/ask-stream-flash") 
async def ask_stream_flash(request: Request, req: ConsultaRequest):
    """Endpoint para consultas com streaming de progresso (SSE)
    
    Args:
        request (Request): Requisição HTTP para controle de conexão
        req (ConsultaRequest): Dados da consulta
        
    Returns:
        EventSourceResponse: Stream de eventos SSE com progresso
    """
    # Cria gerador de eventos para streaming
    event_generator = handle_stream(request, req, "flash")
    # Retorna resposta SSE (Server-Sent Events)
    return EventSourceResponse(event_generator)

@router.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    """Endpoint para processamento de arquivo PDF
    
    Args:
        file (UploadFile): Arquivo PDF enviado
        
    Returns:
        dict: JSON estruturado para busca
    """
    try:
        # Lê o conteúdo do arquivo PDF
        pdf_content = await file.read()
        
        # Processa PDF com LLM usando o processador existente
        from processors.pdf_processor import processPDFBackend
        result = processPDFBackend(pdf_content)
        
        response_json = {"query": result["input_busca"], "metadata": result}
        
        # Log detalhado do JSON gerado
        print("\n" + "="*50)
        print("📄 JSON GERADO PARA UPLOAD DE PDF")
        print("="*50)
        import json
        print(json.dumps(response_json, ensure_ascii=False, indent=2))
        print("="*50 + "\n")
        
        return response_json
        
    except Exception as e:
        logger.error(f"Erro ao processar PDF: {str(e)}")
        # Retorna resposta básica mesmo com erro
        error_response = {
            "query": "Procure informações sobre o documento anexado",
            "metadata": {"status": "error"}
        }
        
        # Log do erro
        print("\n" + "="*50)
        print("❌ ERRO NO PROCESSAMENTO DE PDF")
        print("="*50)
        import json
        print(json.dumps(error_response, ensure_ascii=False, indent=2))
        print("="*50 + "\n")
        
        return error_response

@router.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    """Endpoint para processamento de arquivo de áudio
    
    Args:
        file (UploadFile): Arquivo de áudio enviado
        
    Returns:
        dict: JSON estruturado para busca
    """
    try:
        print(f"🎵 Recebido arquivo: {file.filename if file else 'None'}")
        print(f"📊 Tipo do arquivo: {file.content_type if file else 'None'}")
        
        # Lê o conteúdo do arquivo de áudio
        audio_content = await file.read()
        print(f"📦 Conteúdo lido: {len(audio_content) if audio_content else 'None'} bytes")
        
        if not audio_content:
            raise ValueError("Arquivo de áudio vazio ou não foi possível ler o conteúdo")
        
        # Processa áudio com Whisper e LLM
        from processors.audio_processor import processAudioBackend
        print("🚀 Chamando processAudioBackend...")
        result = processAudioBackend(audio_content)
        print(f"✅ Resultado do processamento: {result}")
        
        response_json = {"query": result["input_busca"], "metadata": result}
        
        # Log detalhado do JSON gerado
        print("\n" + "="*50)
        print("🎵 JSON GERADO PARA UPLOAD DE ÁUDIO")
        print("="*50)
        import json
        print(json.dumps(response_json, ensure_ascii=False, indent=2))
        print("="*50 + "\n")
        
        return response_json
        
    except Exception as e:
        import traceback
        print(f"💥 Erro capturado no router: {str(e)}")
        print(f"🔍 Traceback completo: {traceback.format_exc()}")
        logger.error(f"Erro ao processar áudio: {str(e)}")
        error_response = {
            "query": "Procure informações sobre o áudio anexado",
            "metadata": {"status": "error"}
        }
        
        print("\n" + "="*50)
        print("❌ ERRO NO PROCESSAMENTO DE ÁUDIO")
        print("="*50)
        import json
        print(json.dumps(error_response, ensure_ascii=False, indent=2))
        print("="*50 + "\n")
        
        return error_response

@router.post("/transcribe-audio")
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    """Endpoint para transcrição de arquivo de áudio com streaming
    
    Args:
        request (Request): Requisição HTTP para controle de conexão
        file (UploadFile): Arquivo de áudio enviado
        
    Returns:
        EventSourceResponse: Stream de eventos SSE com transcrição
    """
    audio_content = await file.read()
    if not audio_content:
        raise HTTPException(status_code=400, detail="Arquivo de áudio vazio")
    
    event_generator = handle_transcribe_stream(request, audio_content, "audio")
    return EventSourceResponse(event_generator)

@router.post("/transcribe-video")
async def transcribe_video(request: Request, file: UploadFile = File(...)):
    """Endpoint para transcrição de arquivo de vídeo com streaming
    
    Args:
        request (Request): Requisição HTTP para controle de conexão
        file (UploadFile): Arquivo de vídeo enviado
        
    Returns:
        EventSourceResponse: Stream de eventos SSE com transcrição
    """
    video_content = await file.read()
    if not video_content:
        raise HTTPException(status_code=400, detail="Arquivo de vídeo vazio")
    
    event_generator = handle_transcribe_stream(request, video_content, "video")
    return EventSourceResponse(event_generator)

@router.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    """Endpoint para processamento de arquivo de imagem
    
    Args:
        file (UploadFile): Arquivo de imagem enviado
        
    Returns:
        dict: JSON estruturado para busca
    """
    try:
        print(f"🖼️ Recebido arquivo: {file.filename if file else 'None'}")
        print(f"📊 Tipo do arquivo: {file.content_type if file else 'None'}")
        
        # Lê o conteúdo do arquivo de imagem
        image_content = await file.read()
        print(f"📦 Conteúdo lido: {len(image_content) if image_content else 'None'} bytes")
        
        if not image_content:
            raise ValueError("Arquivo de imagem vazio ou não foi possível ler o conteúdo")
        
        # Processa imagem com Gemini
        from processors.image_processor import processImageBackend
        print("🚀 Chamando processImageBackend...")
        result = processImageBackend(image_content)
        print(f"✅ Resultado do processamento: {result}")
        
        response_json = {"query": result["input_busca"], "metadata": result}
        
        # Log detalhado do JSON gerado
        print("\n" + "="*50)
        print("🖼️ JSON GERADO PARA UPLOAD DE IMAGEM")
        print("="*50)
        import json
        print(json.dumps(response_json, ensure_ascii=False, indent=2))
        print("="*50 + "\n")
        
        return response_json
        
    except Exception as e:
        import traceback
        print(f"💥 Erro capturado no router: {str(e)}")
        print(f"🔍 Traceback completo: {traceback.format_exc()}")
        logger.error(f"Erro ao processar imagem: {str(e)}")
        error_response = {
            "query": "Procure informações sobre a imagem anexada",
            "metadata": {"status": "error"}
        }
        
        print("\n" + "="*50)
        print("❌ ERRO NO PROCESSAMENTO DE IMAGEM")
        print("="*50)
        import json
        print(json.dumps(error_response, ensure_ascii=False, indent=2))
        print("="*50 + "\n")
        
        return error_response

@router.post("/process-video")
async def process_video(file: UploadFile = File(...)):
    """Endpoint para processamento de arquivo de vídeo
    
    Args:
        file (UploadFile): Arquivo de vídeo enviado
        
    Returns:
        dict: JSON estruturado para busca
    """
    try:
        video_content = await file.read()
        
        if not video_content:
            raise ValueError("Arquivo de vídeo vazio ou não foi possível ler o conteúdo")
        
        from processors.video_processor import processVideoBackend
        result = processVideoBackend(video_content)
        
        response_json = {"query": result["input_busca"], "metadata": result}
        
        print("\n" + "="*50)
        print("🎬 JSON GERADO PARA UPLOAD DE VÍDEO")
        print("="*50)
        import json
        print(json.dumps(response_json, ensure_ascii=False, indent=2))
        print("="*50 + "\n")
        
        return response_json
        
    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {str(e)}")
        error_response = {
            "query": "Procure informações sobre o vídeo anexado",
            "metadata": {"status": "error"}
        }
        
        print("\n" + "="*50)
        print("❌ ERRO NO PROCESSAMENTO DE VÍDEO")
        print("="*50)
        import json
        print(json.dumps(error_response, ensure_ascii=False, indent=2))
        print("="*50 + "\n")
        
        return error_response

@router.post("/ask-file-stream")
async def ask_file_stream(request: Request, req: ConsultaMultimodalRequest):
    """Endpoint para consultas geradas a partir de PDF anexado com streaming
    
    Args:
        request (Request): Requisição HTTP para controle de conexão
        req (ConsultaRequest): Dados da consulta gerada do PDF
        
    Returns:
        EventSourceResponse: Stream de eventos SSE com progresso
    """
    # Cria gerador de eventos para streaming usando modelo flash (rápido)
    event_generator = handle_multimodal_stream(request, req)
    # Retorna resposta SSE (Server-Sent Events)
    return EventSourceResponse(event_generator)

@router.post("/process-url")
async def process_url(request: URLRequest):
    """Endpoint para processamento de URL de página web
    
    Args:
        request (URLRequest): JSON com a URL a ser processada
        
    Returns:
        dict: JSON estruturado para consulta acadêmica
    """
    try:
        url = request.url
        
        # Executa web scraping
        import subprocess
        import json
        import os
        
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONHTTPSVERIFY'] = '0'
        env['CURL_CA_BUNDLE'] = ''
        
        # Adiciona proxy se configurado no .env
        if 'PROXY' in os.environ:
            env['HTTP_PROXY'] = os.environ['PROXY']
            env['HTTPS_PROXY'] = os.environ['PROXY']
            env['http_proxy'] = os.environ['PROXY']
            env['https_proxy'] = os.environ['PROXY']
        
        script_code = '''
import ssl
import sys
ssl._create_default_https_context = ssl._create_unverified_context
sys.path.insert(0, ".")
with open("web_scraper.py", encoding="utf-8") as f:
    exec(f.read())
'''
        
        result = subprocess.run(
            ['python', '-c', script_code, url],
            capture_output=True,
            text=True,
            cwd='.',
            encoding='utf-8',
            env=env
        )
        
        if result.returncode != 0:
            raise Exception(f"Erro no scraping: {result.stderr}")
        
        if not result.stdout.strip():
            raise Exception(f"Web scraper retornou saída vazia. stderr: {result.stderr}")
        
        # Extrai apenas a parte JSON do output (ignora mensagens de debug)
        output_lines = result.stdout.strip().split('\n')
        json_start = -1
        for i, line in enumerate(output_lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start == -1:
            raise Exception(f"Nenhum JSON encontrado no output: {result.stdout[:200]}...")
        
        json_output = '\n'.join(output_lines[json_start:])
        
        try:
            scraped_data = json.loads(json_output)
        except json.JSONDecodeError as e:
            raise Exception(f"Erro ao parsear JSON: '{json_output[:200]}...'. Erro: {str(e)}")
        
        # Processa com LLM
        from processors.url_processor_backend import process_url_data
        structured_query = process_url_data(scraped_data)
        
        # Log detalhado do JSON gerado
        print("\n" + "="*80)
        print("🌐 JSON ESTRUTURADO GERADO PARA CONSULTA ACADÊmica")
        print("="*80)
        print(f"🔗 URL Processada: {url}")
        print(f"🎯 Assunto Principal: {structured_query['assunto_principal']}")
        print(f"🔍 Termos de Busca: {structured_query['termos_chave']}")
        print(f"📅 Query ID: {structured_query['query_id']}")
        print("-" * 80)
        print("JSON COMPLETO:")
        print(json.dumps(structured_query, ensure_ascii=False, indent=2))
        print("="*80 + "\n")
        
        return structured_query
        
    except Exception as e:
        logger.error(f"Erro ao processar URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar URL: {str(e)}")

@router.post("/ask-url-stream")
async def ask_url_stream(request: Request, req: ConsultaRequest):
    """Endpoint para consultas geradas a partir de URL processada com streaming
    
    Args:
        request (Request): Requisição HTTP para controle de conexão
        req (ConsultaRequest): Dados da consulta gerada da URL
        
    Returns:
        EventSourceResponse: Stream de eventos SSE com progresso
    """
    # Cria gerador de eventos para streaming usando modelo flash (rápido)
    event_generator = handle_stream(request, req, "flash")
    # Retorna resposta SSE (Server-Sent Events)
    return EventSourceResponse(event_generator)
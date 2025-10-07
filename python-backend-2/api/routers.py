# Rotas da API - define endpoints HTTP para o chatbot
# Implementa endpoints para chat síncrono e streaming
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from sse_starlette.sse import EventSourceResponse
from .models import ConsultaRequest, ConsultaMultimodalRequest, ConsultaResponse
from .api_service import handle_stream, handle_multimodal_stream
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
async def process_url(request: dict):
    """Endpoint para processamento de URL de página web
    
    Args:
        request (dict): JSON com a URL a ser processada
        
    Returns:
        dict: JSON estruturado para consulta acadêmica
    """
    try:
        url = request.get('url')
        if not url:
            raise HTTPException(status_code=400, detail="URL é obrigatória")
        
        # Executa web scraping
        import subprocess
        import json
        
        result = subprocess.run(
            ['python', 'web_scraper.py', url],
            capture_output=True,
            text=True,
            cwd='.',
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            raise Exception(f"Erro no scraping: {result.stderr}")
        
        scraped_data = json.loads(result.stdout)
        
        # Processa com LLM
        from processors.url_processor_backend import process_url_data
        structured_query = process_url_data(scraped_data)
        
        # Log detalhado do JSON gerado
        print("\n" + "="*80)
        print("🌐 JSON ESTRUTURADO GERADO PARA CONSULTA ACADÊmica")
        print("="*80)
        print(f"🔗 URL Processada: {url}")
        print(f"🎯 Assunto Principal: {structured_query['filters']['main_subject']}")
        print(f"🔍 Termos de Busca: {structured_query['input_busca']}")
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
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

@router.post("/ask-pdf-stream")
async def ask_pdf_stream(request: Request, req: ConsultaRequest):
    """Endpoint para consultas geradas a partir de PDF anexado com streaming
    
    Args:
        request (Request): Requisição HTTP para controle de conexão
        req (ConsultaRequest): Dados da consulta gerada do PDF
        
    Returns:
        EventSourceResponse: Stream de eventos SSE com progresso
    """
    # Cria gerador de eventos para streaming usando modelo flash (rápido)
    event_generator = handle_stream(request, req, "flash")
    # Retorna resposta SSE (Server-Sent Events)
    return EventSourceResponse(event_generator)
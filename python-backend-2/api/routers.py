# Rotas da API - define endpoints HTTP para o chatbot
# Implementa endpoints para chat síncrono e streaming
from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse
from .models import ConsultaRequest, ConsultaResponse
from .api_service import handle_stream
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
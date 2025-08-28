# Rotas da API - define endpoints HTTP para o chatbot
# Implementa endpoints para chat síncrono e streaming
from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse
from .models import ConsultaRequest, ConsultaResponse
from .api_service import handle_chat, handle_stream
import logging

# Configura roteador com prefixo vazio e tag para documentação
router = APIRouter(prefix="", tags=["Chatbot"])
logger = logging.getLogger(__name__)

@router.post("/ask", response_model=ConsultaResponse)
async def ask(req: ConsultaRequest):
    """Endpoint para consultas síncronas (sem streaming)
    
    Args:
        req (ConsultaRequest): Dados da consulta
        
    Returns:
        ConsultaResponse: Resposta completa do chatbot
    """
    return await handle_chat(req)

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
    event_generator = handle_stream(request, req)
    # Retorna resposta SSE (Server-Sent Events)
    return EventSourceResponse(event_generator)
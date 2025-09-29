# Serviços da API - lógica de negócio para endpoints
# Processa requisições de chat e streaming de respostas
from rag_models.thinking.query import handle_query
from rag_models.flash.query import handle_query_flash
from rag_models.multimodal.query import handle_query_multimodal
from api.models import ConsultaRequest, ConsultaMultimodalRequest, ConsultaResponse
from fastapi import HTTPException, Request
import logging

# Logger para rastreamento de operações
logger = logging.getLogger(__name__)

async def handle_stream(request: Request, req: ConsultaRequest, model_name: str):
    """Processa consulta com streaming de progresso em tempo real
    
    Args:
        request (Request): Requisição FastAPI para verificar desconexão
        req (ConsultaRequest): Dados da consulta
        
    Yields:
        dict: Eventos SSE com progresso ou resultado final
    """
    try:
        # Formata histórico da conversa
        historico_str = format_history(req.historico)
        message_stream = None
        # Inicia o pipeline de processamento com streaming
        if model_name == "flash":
            message_stream = handle_query_flash(req.consulta, historico_str)
        elif model_name == "multimodal":
            message_stream = handle_query_multimodal(req.consulta, historico_str, req.tipo_de_arquivo, req.texto_arquivo)
        else:
            message_stream = handle_query(req.consulta, historico_str)
        
        # Processa cada mensagem do stream
        async for message in message_stream:
            # Verifica se cliente desconectou
            if await request.is_disconnected():
                logger.info("Client disconnected")
                break
            
            # Identifica tipo de mensagem e formata evento SSE
            if message.startswith("FINAL_RESULT::"):
                # Resultado final - remove prefixo e envia como evento 'done'
                yield {
                    "event": "done",
                    "data": message.replace("FINAL_RESULT::", "")
                }
            elif message.startswith("PARTIAL_RESPONSE:"):
                # Resposta parcial do LLM
                yield {
                    "event": "partial",
                    "data": message.replace("PARTIAL_RESPONSE:", "")
                }
            else:
                # Mensagem de progresso
                yield {
                    "event": "progress",
                    "data": message
                }
                
    except Exception as e:
        # Em caso de erro, envia evento de erro
        logger.exception("Stream error")
        yield {
            "event": "error",
            "data": f"Server error: {str(e)}"
        }

def format_history(historico):
    """Formata histórico de mensagens em string para o modelo
    
    Args:
        historico (list): Lista de mensagens do histórico
        
    Returns:
        str or None: Histórico formatado ou None se vazio
    """
    if not historico: 
        return None
    # Formata cada mensagem como "Usuário: ... Bot: ..." separado por "---"
    return "\n".join(f"Usuário: {m.usuario}\nBot: {m.bot}\n---" for m in historico)

def handle_error(e):
    """Trata erros e converte para HTTPException apropriada
    
    Args:
        e (Exception): Exceção capturada
        
    Raises:
        HTTPException: Erro HTTP com status code e mensagem adequados
    """
    if isinstance(e, ValueError):
        # Erros de validação retornam 422 (Unprocessable Entity)
        logger.warning(f"Erro de validação: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    
    # Outros erros retornam 500 (Internal Server Error)
    logger.exception("Erro inesperado")
    raise HTTPException(status_code=500, detail="Erro interno")

async def handle_multimodal_stream(request: Request, req: ConsultaMultimodalRequest):
    """Processa consulta multimodal com streaming de progresso em tempo real"""
    try:
        historico_str = format_history(req.historico)
        message_stream = handle_query_multimodal(req.consulta, historico_str, req.tipo_de_arquivo, req.texto_arquivo)
        
        async for message in message_stream:
            if await request.is_disconnected():
                logger.info("Client disconnected")
                break
            
            if message.startswith("FINAL_RESULT::"):
                yield {
                    "event": "done",
                    "data": message.replace("FINAL_RESULT::", "")
                }
            elif message.startswith("PARTIAL_RESPONSE:"):
                yield {
                    "event": "partial",
                    "data": message.replace("PARTIAL_RESPONSE:", "")
                }
            else:
                yield {
                    "event": "progress",
                    "data": message
                }
                
    except Exception as e:
        logger.exception("Multimodal stream error")
        yield {
            "event": "error",
            "data": f"Server error: {str(e)}"
        }
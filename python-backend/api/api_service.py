# Serviços da API - lógica de negócio para endpoints
# Processa requisições de chat e streaming de respostas
from rag_models.model4.query import handle_query
from rag_models.model2 import pipeline_completo
from api.models import ConsultaRequest, ConsultaResponse
from fastapi import HTTPException, Request
import logging

# Logger para rastreamento de operações
logger = logging.getLogger(__name__)

async def handle_chat(req: ConsultaRequest):
    """Processa consulta de chat sem streaming
    
    Args:
        req (ConsultaRequest): Requisição com consulta e histórico
        
    Returns:
        ConsultaResponse: Resposta completa do sistema
    """
    try:
        logger.info(f"Recebida consulta: {req.consulta}")
        # Formata o histórico da conversa
        historico_str = format_history(req.historico)
        # Executa pipeline com ou sem histórico
        return pipeline_completo(req.consulta, historico_str) if historico_str else pipeline_completo(req.consulta)
    except Exception as e:
        handle_error(e)  # Trata erros e lança HTTPException apropriada

async def handle_stream(request: Request, req: ConsultaRequest):
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
        # Inicia o pipeline de processamento com streaming
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
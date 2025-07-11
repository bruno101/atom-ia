from rag_models.model4.query import handle_query
from rag_models.model2 import pipeline_completo
from api.models import ConsultaRequest, ConsultaResponse
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)

async def handle_chat(req: ConsultaRequest):
    try:
        logger.info(f"Recebida consulta: {req.consulta}")
        historico_str = format_history(req.historico)
        return pipeline_completo(req.consulta, historico_str) if historico_str else pipeline_completo(req.consulta)
    except Exception as e:
        handle_error(e)

async def handle_stream(request: Request, req: ConsultaRequest):
    try:
        historico_str = format_history(req.historico)
        message_stream = handle_query(req.consulta, historico_str)
        
        async for message in message_stream:
            if await request.is_disconnected():
                logger.info("Client disconnected")
                break
                
            if message.startswith("FINAL_RESULT::"):
                yield {
                    "event": "done",
                    "data": message.replace("FINAL_RESULT::", "")
                }
            else:
                yield {
                    "event": "progress",
                    "data": message
                }
                
    except Exception as e:
        logger.exception("Stream error")
        yield {
            "event": "error",
            "data": f"Server error: {str(e)}"
        }

def format_history(historico):
    if not historico: return None
    return "\n".join(f"Usuário: {m.usuario}\nBot: {m.bot}\n---" for m in historico)

def handle_error(e):
    if isinstance(e, ValueError):
        logger.warning(f"Erro de validação: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    logger.exception("Erro inesperado")
    raise HTTPException(status_code=500, detail="Erro interno")
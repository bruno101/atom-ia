from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse
from .models import ConsultaRequest, ConsultaResponse
from .api_service import handle_chat, handle_stream
import logging

router = APIRouter(prefix="", tags=["Chatbot"])
logger = logging.getLogger(__name__)

@router.post("/ask", response_model=ConsultaResponse)
async def ask(req: ConsultaRequest):
    return await handle_chat(req)

@router.post("/ask-stream") 
async def ask_stream(request: Request, req: ConsultaRequest):
    event_generator = handle_stream(request, req)
    return EventSourceResponse(event_generator)
from fastapi import FastAPI
from api import routers
from config import configure_app

app = FastAPI(
    title="Chatbot AtoModesto",
    description="API para responder consultas com RAG e LLM",
    version="1.1.0"
)

configure_app(app)
app.include_router(routers.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)

"""import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
from rag_models.model4.query import handle_query
from rag_models.model2 import pipeline_completo
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chatbot AtoModesto",
    description="API para responder consultas com RAG e LLM, com histórico opcional",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:63001"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MensagemHistorico(BaseModel):
    usuario: str = Field(..., description="Mensagem do usuário")
    bot: str = Field(..., description="Resposta do bot")

class ConsultaRequest(BaseModel):
    consulta: str = Field(..., min_length=3, description="Texto da consulta a ser respondida.")
    historico: Optional[List[MensagemHistorico]] = Field(
        default=None,
        description="Histórico opcional de interações anteriores"
    )
    
class Link(BaseModel):
    url: str = Field(..., description="URL da página recomendada")
    title: str = Field(..., description="Título da página recomendada")
    slug: str = Field(..., description="Slug da página recomendada")
    justificativa: Optional[str] = Field(None, description="Justificativa para a recomendação da página")
    descricao: Optional[str] = Field(None, description="Descrição da página recomendada")

class ConsultaResponse(BaseModel):
    resposta: str
    links: List[Link]

@app.post("/ask", response_model=ConsultaResponse)
async def ask(req: ConsultaRequest):
    try:
        logger.info(f"Recebida consulta: {req.consulta}")

        historico_str = None
        if req.historico:
            historico_formatado = [(m.usuario, m.bot) for m in req.historico]
            historico_str = "\n".join(
                f"Usuário: {usuario}\nBot: {bot}\n---"
                for usuario, bot in historico_formatado
                )

        if historico_str:
            resposta = pipeline_completo(req.consulta, historico_str)
        else:
            resposta = pipeline_completo(req.consulta)

        return resposta

    except ValueError as e:
        logger.warning(f"Erro de validação: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except TypeError as e:
        logger.error(f"Erro de tipo: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Erro inesperado")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
    
@app.post("/ask-stream") 
async def ask_stream(request: Request, req: ConsultaRequest): 
    async def event_generator():
        try:
            historico_str = None
            if req.historico:
                historico_formatado = [(m.usuario, m.bot) for m in req.historico]
                historico_str = "\n".join(
                    f"Usuário: {usuario}\nBot: {bot}\n---"
                    for usuario, bot in historico_formatado
                )
            
            async for message in handle_query(req.consulta, historico_str): 
                if await request.is_disconnected():
                    logger.info("Client disconnected from SSE stream.")
                    break

                if message.startswith("FINAL_RESULT::"):
                    final_data = message.replace("FINAL_RESULT::", "")
                    yield {
                        "event": "done",
                        "data": final_data 
                    }
                    return 
                else:
                    yield {
                        "event": "progress",
                        "data": message
                    }
        except Exception as e:
            error_message = f"Erro no servidor: {str(e)}"
            logger.exception(f"Erro inesperado no event_generator para consulta '{req.consulta}'")
            yield {
                "event": "error",
                "data": error_message
            }
            return 

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)"""
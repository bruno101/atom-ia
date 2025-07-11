from pydantic import BaseModel, Field
from typing import List, Optional

class MensagemHistorico(BaseModel):
    usuario: str = Field(..., description="Mensagem do usuário")
    bot: str = Field(..., description="Resposta do bot")

class ConsultaRequest(BaseModel):
    consulta: str = Field(..., min_length=3)
    historico: Optional[List[MensagemHistorico]] = Field(default=None)

class Link(BaseModel):
    url: str = Field(...)
    title: str = Field(...)
    slug: str = Field(...)
    justificativa: Optional[str] = None
    descricao: Optional[str] = None

class ConsultaResponse(BaseModel):
    resposta: str
    links: List[Link]
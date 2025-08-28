# Modelos Pydantic para validação de dados da API
# Define estruturas de requisição e resposta para endpoints
from pydantic import BaseModel, Field
from typing import List, Optional

class MensagemHistorico(BaseModel):
    """Representa uma mensagem no histórico da conversa"""
    usuario: str = Field(..., description="Mensagem do usuário")
    bot: str = Field(..., description="Resposta do bot")

class ConsultaRequest(BaseModel):
    """Modelo para requisições de consulta ao chatbot"""
    consulta: str = Field(..., min_length=3, description="Consulta do usuário (mínimo 3 caracteres)")
    historico: Optional[List[MensagemHistorico]] = Field(
        default=None, 
        description="Histórico opcional da conversa"
    )

class Link(BaseModel):
    """Representa um link recomendado na resposta"""
    url: str = Field(..., description="URL completa da página")
    title: str = Field(..., description="Título da página")
    slug: str = Field(..., description="Identificador único da página")
    justificativa: Optional[str] = Field(None, description="Justificativa da recomendação")
    descricao: Optional[str] = Field(None, description="Descrição do conteúdo")

class ConsultaResponse(BaseModel):
    """Modelo para respostas do chatbot"""
    resposta: str = Field(..., description="Resposta textual do bot")
    links: List[Link] = Field(..., description="Lista de links recomendados")
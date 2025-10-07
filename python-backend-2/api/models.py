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

class FileMetadata(BaseModel):
    """Metadados do arquivo processado"""
    query_id: str = Field(..., description="ID único da consulta")
    resumo: str = Field(..., description="Resumo do conteúdo do arquivo")
    input_busca: str = Field(..., description="Consulta de busca processada")
    assunto_principal: str = Field(..., description="Assunto principal do arquivo")
    termos_chave: List[str] = Field(..., description="Termos-chave extraídos")

class ConsultaMultimodalRequest(BaseModel):
    """Modelo para requisições multimodais ao chatbot"""
    consulta: str = Field(..., min_length=3, description="Consulta do usuário (mínimo 3 caracteres)")
    historico: Optional[List[MensagemHistorico]] = Field(
        default=None, 
        description="Histórico opcional da conversa"
    )
    metadata: FileMetadata = Field(..., description="Metadados do arquivo processado")

class Link(BaseModel):
    """Representa um link recomendado na resposta"""
    url: str = Field(..., description="URL completa da página")
    title: str = Field(..., description="Título da página")
    slug: str = Field(..., description="Identificador único da página")
    justificativa: Optional[str] = Field(None, description="Justificativa da recomendação")
    descricao: Optional[str] = Field(None, description="Descrição do conteúdo")

class URLRequest(BaseModel):
    """Modelo para requisições de processamento de URL"""
    url: str = Field(..., description="URL a ser processada")

class ConsultaResponse(BaseModel):
    """Modelo para respostas do chatbot"""
    resposta: str = Field(..., description="Resposta textual do bot")
    links: List[Link] = Field(..., description="Lista de links recomendados")
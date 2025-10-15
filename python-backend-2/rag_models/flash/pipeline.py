# Pipeline do modelo Flash - versão rápida do RAG
# Processa consultas com busca vetorial + BM25 e streaming de respostas
import json
import asyncio
from .config import MAX_QUERY_CHARS
from .utils import extrair_links_corrigidos
from . import messages
from .query_engine import global_query, llm_query


async def pipeline_stream(consulta, historico=None, llm=None):
    """Pipeline principal do modelo Flash com streaming
    
    Args:
        consulta (str): Consulta do usuário
        historico (str, optional): Histórico da conversa
        llm: Modelo de linguagem
        
    Yields:
        str: Mensagens de progresso, respostas parciais e resultado final
    """
    
    # Calcula tamanho máximo do histórico baseado no limite de caracteres
    tamanho_maximo_historico = max(MAX_QUERY_CHARS - len(consulta), 0)
    # Trunca histórico se necessário, mantendo pelo menos 100 caracteres
    historico_str = historico[:tamanho_maximo_historico] if historico and tamanho_maximo_historico >= 100 else ""
        
    # Envia mensagem de inicialização
    if messages.MENSAGEM_PIPELINE_INICIALIZANDO:
        yield messages.MENSAGEM_PIPELINE_INICIALIZANDO
    
    # Busca documentos relevantes usando busca híbrida
    nos = global_query(consulta)
    num_documentos = len(nos)
    
    # Informa quantidade de documentos encontrados
    if messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS:
        yield messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS.format(num_documentos=num_documentos)
    
    # Configura sistema de retry com backoff exponencial
    retry_intervals = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    resposta = None
    
    # Loop de retry para garantir resposta válida
    for i, interval in enumerate([0] + retry_intervals):
        if i > 0:
            await asyncio.sleep(interval)
        
        try:
            resposta_parts = []
            # Faz query ao LLM com streaming
            for chunk in llm_query(llm, consulta, historico_str, nos):
                yield chunk
                if chunk.startswith("PARTIAL_RESPONSE:"):
                    resposta_parts.append(chunk[17:])  # Remove prefixo
            resposta = ''.join(resposta_parts)
            # Valida se resposta é adequada
            if resposta and len(resposta.strip()) > 10:
                break
            print("Tentando de novo")
        except Exception:
            print("Ocorreu exceção")
            if i == len(retry_intervals):
                resposta = "Desculpe, ocorreu um erro na requisição da API. Tente novamente em alguns minutos."
    
    # Extrai e valida links da resposta
    links_validos = [no["url"] for no in nos]
    resposta_corrigida, links = extrair_links_corrigidos(resposta, nos)
    
    # Monta resultado final com resposta e metadados
    final = {
            "resposta": resposta_corrigida,
            "links": links,
            "palavras_chave" : [consulta],
            "links_analisados": links_validos
        }

    # Envia resultado final como JSON
    yield f"FINAL_RESULT::{json.dumps(final, ensure_ascii=False)}"
    return
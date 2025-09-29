import json
import asyncio
import logging
from .config import MAX_QUERY_CHARS
from .utils import extrair_links_corrigidos
from . import messages
from .query_engine import global_query, llm_query, expand_multimodal_query

logger = logging.getLogger(__name__)


async def pipeline_stream(consulta, historico=None, llm=None, tipo_de_arquivo=None, texto_arquivo=None):
    
    # Calcula o tamanho máximo do histórico baseado no limite de caracteres
    tamanho_maximo_historico = max(MAX_QUERY_CHARS - len(consulta), 0)
    # Trunca o histórico se necessário, mantendo pelo menos 100 caracteres
    historico_str = historico[:tamanho_maximo_historico] if historico and tamanho_maximo_historico >= 100 else ""
        
    if messages.MENSAGEM_PIPELINE_INICIALIZANDO:
        yield messages.MENSAGEM_PIPELINE_INICIALIZANDO
        
    if tipo_de_arquivo and texto_arquivo:
        logger.info(f"Processing multimodal query with file type: {tipo_de_arquivo}")
        expanded_queries = expand_multimodal_query(consulta, tipo_de_arquivo, texto_arquivo)
        logger.info(f"Executing queries for {len(expanded_queries)} expanded queries")
        all_nos = []
        for i, query in enumerate(expanded_queries):
            logger.debug(f"Query {i+1}: {query}")
            query_nos = global_query(query)
            all_nos.extend(query_nos)
            logger.debug(f"Query {i+1} returned {len(query_nos)} documents")
        nos = list({no['url']: no for no in all_nos}.values())  # Remove duplicates by URL
        logger.info(f"Total unique documents after expansion: {len(nos)}")
    else:
        logger.info("Processing standard query (no multimodal context)")
        nos = global_query(consulta)
    num_documentos = len(nos)
    
    if messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS:
        yield messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS.format(num_documentos=num_documentos)
        
    retry_intervals = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    resposta = None
    
    for i, interval in enumerate([0] + retry_intervals):
        if i > 0:
            await asyncio.sleep(interval)
        
        try:
            resposta_parts = []
            for chunk in llm_query(llm, consulta, historico_str, nos):
                yield chunk
                if chunk.startswith("PARTIAL_RESPONSE:"):
                    resposta_parts.append(chunk[17:])  # Remove "PARTIAL_RESPONSE:" prefix
            resposta = ''.join(resposta_parts)
            if resposta and len(resposta.strip()) > 10:
                break
            print("Tentando de novo")
        except Exception:
            print("Ocorreu exceção")
            if i == len(retry_intervals):
                resposta = "Desculpe, ocorreu um erro na requisição da API. Tente novamente em alguns minutos."
    
    links_validos = [no["url"] for no in nos]
    resposta_corrigida, links = extrair_links_corrigidos(resposta, nos)
    
    final = {
            "resposta": resposta_corrigida,
            "links": links,
            "palavras_chave" : [consulta],
            "links_analisados": links_validos
        }

    yield f"FINAL_RESULT::{json.dumps(final, ensure_ascii=False)}"
    return
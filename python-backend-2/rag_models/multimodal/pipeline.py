import json
import asyncio
import logging
from .config import MAX_QUERY_CHARS
from .utils import extrair_links_corrigidos
from . import messages
from .query_engine import global_query, llm_query

logger = logging.getLogger(__name__)


async def pipeline_stream(consulta, historico=None, llm=None, file_metadata=None):
    
    # Calcula o tamanho máximo do histórico baseado no limite de caracteres
    tamanho_maximo_historico = max(MAX_QUERY_CHARS - len(consulta), 0)
    # Trunca o histórico se necessário, mantendo pelo menos 100 caracteres
    historico_str = historico[:tamanho_maximo_historico] if historico and tamanho_maximo_historico >= 100 else ""
        
    if messages.MENSAGEM_PIPELINE_INICIALIZANDO:
        yield messages.MENSAGEM_PIPELINE_INICIALIZANDO

    nos = global_query(consulta, file_metadata)
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
            for chunk in llm_query(llm, consulta, historico_str, nos, file_metadata):
                yield chunk
                if chunk.startswith("PARTIAL_RESPONSE:"):
                    resposta_parts.append(chunk[17:])  # Remove "PARTIAL_RESPONSE:" prefix
            resposta = ''.join(resposta_parts)
            if resposta and len(resposta.strip()) > 10:
                break
            print("Tentando de novo")
        except Exception as e:
            logger.exception(f"Erro na tentativa {i+1}: {str(e)}")
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
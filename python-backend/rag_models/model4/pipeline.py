from .validation import (
    extrair_json_da_resposta,
    validando,
    formatando_respostas
)
from . import messages
from .config import URL_ATOM, NUMBER_OF_VECTOR_QUERIES, NUMBER_OF_TRADITIONAL_QUERIES, MAX_QUERY_CHARS
from db_connection import fetch_slugs
import json

async def pipeline_stream(consulta, historico=None, query_engine=None, llm=None, slugs_validos=None):
    
    tamanho_maximo_historico = max(MAX_QUERY_CHARS - len(consulta), 0)
    historico_str = historico[:tamanho_maximo_historico] if historico and tamanho_maximo_historico >= 100 else ""
    
    print("Histórico é: ", historico_str)
    
    if messages.MENSAGEM_PIPELINE_INICIALIZANDO:
        yield messages.MENSAGEM_PIPELINE_INICIALIZANDO
    
    try:
        prompt = f"""
            Extraia as palavras-chave E expressões curtas mais importantes e relevantes para busca vetorial de documentos que ajudem a responder a seguinte consulta.
            Separe cada item por vírgula. Ordene do mais importante para o menos importante, e gere ${max(NUMBER_OF_VECTOR_QUERIES, NUMBER_OF_TRADITIONAL_QUERIES)} expressões.\n
            {f"Histórico da Conversa: {historico_str}." if historico_str else ""}
            \nConsulta: {consulta}.\n
            Resultado (apenas termos e expressões separadas por vírgula):
        """
        raw_output = llm.complete(prompt)
        if messages.MENSAGEM_CONSULTA_VETORIAL_GERADA:
            yield messages.MENSAGEM_CONSULTA_VETORIAL_GERADA
        
        nos = query_engine.custom_global_query(raw_output)
        print("Nós encontrados: \n\n", nos)
        num_documentos = len(nos) 
        if messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS:
            yield messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS.format(num_documentos=num_documentos)
        
        resposta = query_engine.custom_query(consulta, historico_str or "", nos)
        print("Resposta gerada: \n\n", resposta)
        resposta_json = extrair_json_da_resposta(resposta)
        try:
            numero_paginas = len(resposta_json["data"]["paginas"])
            if messages.MENSAGEM_PAGINAS_SELECIONADAS:
                yield messages.MENSAGEM_PAGINAS_SELECIONADAS.format(numero_paginas=numero_paginas)
        except:
            logger.debug("Exceção calculando número de páginas. Continuando com a validação.")
            
        resposta_json_validada = validando(resposta_json, slugs_validos)
        if messages.MENSAGEM_RESPOSTA_VALIDADA:
            yield messages.MENSAGEM_RESPOSTA_VALIDADA

        resposta_textual = formatando_respostas(resposta_json_validada, consulta, llm, historico_str or "")

        final = {
            "resposta": resposta_textual,
            "links": [
                {
                    "url": f"{URL_ATOM}/index.php/{p.get('slug', '')}", 
                    "slug": p.get('slug', ''),
                    "title": p.get('title', ''),
                    "justificativa": p.get('justificativa', None),
                    "descricao": p.get('descricao', None)
                }
                for p in resposta_json_validada.get('data', {}).get('paginas', [])
            ]
        }

        yield f"FINAL_RESULT::{json.dumps(final, ensure_ascii=False)}"
        return  

    except ValueError as ve:
        yield f"Erro: {str(ve)}"
        return  
    except TypeError as te:
        yield f"Erro: {str(te)}"
        return  
    except Exception as e:
        yield f"Erro inesperado no pipeline: {str(e)}"
        return  
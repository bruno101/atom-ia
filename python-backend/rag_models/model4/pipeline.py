from .validation import (
    extrair_json_da_resposta,
    validando,
    formatando_respostas
)
from . import messages
from db_connection import fetch_slugs
import json

async def pipeline_stream(consulta, historico=None, query_engine=None, llm=None, slugs_validos=None):
    
    if messages.MENSAGEM_PIPELINE_INICIALIZANDO:
        yield messages.MENSAGEM_PIPELINE_INICIALIZANDO
    
    try:
        
        nodes = query_engine.retriever.retrieve(consulta)
        num_documentos = len(nodes) 
        if messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS:
            yield messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS.format(num_documentos=num_documentos)
        
        response = query_engine.custom_query(consulta, historico or "", nodes)
        resposta_json = extrair_json_da_resposta(response)
        try:
            numero_paginas = len(resposta_json["data"]["paginas"])
            if messages.MENSAGEM_PAGINAS_SELECIONADAS:
                yield messages.MENSAGEM_PAGINAS_SELECIONADAS.format(numero_paginas=numero_paginas)
        except:
            logger.debug("Exceção calculando número de páginas. Continuando com a validação.")
            
        resposta_json_validada = validando(resposta_json, slugs_validos)
        if messages.MENSAGEM_RESPOSTA_VALIDADA:
            yield messages.MENSAGEM_RESPOSTA_VALIDADA

        resposta_textual = formatando_respostas(resposta_json_validada, consulta, llm)

        final = {
            "resposta": resposta_textual,
            "links": [
                {
                    "url": f"http://localhost:63001/index.php/{p.get('slug', '')}", 
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
from .validation import (
    extrair_json_da_resposta,
    validando,
    formatando_respostas
)
from . import messages
from .config import URL_ATOM, NUMBER_OF_VECTOR_QUERIES
from db_connection import fetch_slugs
import json

async def pipeline_stream(consulta, historico=None, query_engine=None, llm=None, slugs_validos=None):
    
    if messages.MENSAGEM_PIPELINE_INICIALIZANDO:
        yield messages.MENSAGEM_PIPELINE_INICIALIZANDO
    
    try:
        prompt = f"""
            Extraia as palavras-chave E expressões curtas mais importantes e relevantes para busca vetorial de documentos que ajudem a responder a seguinte consulta.
            Separe cada item por vírgula. Ordene do mais importante para o menos importante, e gere ${NUMBER_OF_VECTOR_QUERIES} expressões.
            Consulta: {consulta}
            Resultado (apenas termos e expressões separadas por vírgula):
        """
        raw_output = llm.complete(prompt)
        if messages.MENSAGEM_CONSULTA_VETORIAL_GERADA:
            yield messages.MENSAGEM_CONSULTA_VETORIAL_GERADA
            
        lista_consultas_vectoriais = str(raw_output).split(",")[:NUMBER_OF_VECTOR_QUERIES]
        consultas_vetoriais = [q.strip() for q in lista_consultas_vectoriais if q.strip()]
        nos = query_engine.custom_vector_query(consultas_vetoriais)
        num_documentos = len(nos) 
        if messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS:
            yield messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS.format(num_documentos=num_documentos)
        
        resposta = query_engine.custom_query(consulta, historico or "", nos)
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

        resposta_textual = formatando_respostas(resposta_json_validada, consulta, llm)

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
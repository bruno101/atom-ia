from query_engine import create_query_engine
from validation import (
    extrair_json_da_resposta,
    validando,
    formatando_respostas
)
from db_connection import fetch_slugs
import json

async def pipeline_stream(consulta, historico=None):
    yield "Inicializando pipeline..."
    
    try:
        nodes = query_engine_customize.retriever.retrieve(consulta)
        num_documents = len(nodes) 
        
        yield f"Encontrei {num_documents} documentos relacionados à sua pesquisa. Analisando o conteúdo..."
        response = query_engine_customize.custom_query(consulta, historico or "")
        
        resposta_json = extrair_json_da_resposta(response)
        try:
            numero_paginas = len(resposta_json["data"]["paginas"])
            yield f"Selecionei as {numero_paginas} páginas mais relevantes para sua consulta. Validando e preparando resposta final..."
        except:
            logger.debug("Exceção calculando número de páginas. Continuando com a validação.")
            
        resposta_json_validada = validando(resposta_json, slugs_validos)


        resposta_textual = formatando_respostas(resposta_json_validada, consulta)

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
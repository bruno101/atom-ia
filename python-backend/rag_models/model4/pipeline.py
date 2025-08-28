from .validation import (
    extrair_json_da_resposta,
    validando,
    formatando_respostas
)
from . import messages
from .config import NUMBER_OF_VECTOR_QUERIES, NUMBER_OF_TRADITIONAL_QUERIES, MAX_QUERY_CHARS
from db_connection import fetch_slugs
import json
import os
from dotenv import load_dotenv

load_dotenv()
URL_ATOM = os.getenv('URL_ATOM', 'http://localhost:63001')

async def pipeline_stream(consulta, historico=None, query_engine=None, llm=None, slugs_validos=None):
    
    tamanho_maximo_historico = max(MAX_QUERY_CHARS - len(consulta), 0)
    historico_str = historico[:tamanho_maximo_historico] if historico and tamanho_maximo_historico >= 100 else ""
        
    if messages.MENSAGEM_PIPELINE_INICIALIZANDO:
        yield messages.MENSAGEM_PIPELINE_INICIALIZANDO
    
    try:
        prompt = f"""
                    Extraia as palavras-chave E expressões curtas mais importantes e relevantes para busca vetorial e lexical de documentos que ajudem a responder a consulta que será dada ao fim dessa prompt.
                    Sua tarefa é determinar o que é adequado para busca vetorial e o que é adequado para busca lexical exata.

                    Para a **busca vetorial**, produza exatamente {NUMBER_OF_VECTOR_QUERIES} consultas robustas:
                    - Cada consulta deve ter de 4 a 8 palavras em português, sem vírgulas internas.
                    - Use expressões completas e naturais que incluam:
                    - o tema principal,
                    - sinônimos e variações de grafia relevantes,
                    - entidades, datas, locais e instituições associadas,
                    - subtemas ou facetas relacionadas (ex.: suportes documentais, personagens, eventos).
                    - Não gere consultas redundantes: cada uma deve focar em um aspecto diferente do tema.

                    Para a **busca lexical exata**, produza {NUMBER_OF_TRADITIONAL_QUERIES} expressões curtas de uma ou duas palavras relevantes:
                    - Inclua variações de gênero, número e grafia,
                    - Inclua formas alternativas de escrever o mesmo termo (incluindo erros comuns),
                    - Não ultrapasse duas palavras por termo.

                    Exemplo:
                    Se a consulta fosse "Estou pesquisando sobre a história dos judeus no Brasil":
                    1) a consulta "judeus no Brasil cristãos-novos inquisição antissemitismo" etc. seria adequada para busca vetorial, pois considera variações do tema e termos relacionados.
                    2) as consultas "judeu,judeus,judaico,judaica,judaicos,judaicas,cristão-novo,cristão novo,cristãos-novos,cristãos novos,hebreu,hebreus,Israel,inquisição" seriam adequadas para busca lexical exata, pois são expressões de uma ou no máximo duas palavras relevantes que incluem variações de grafia, gênero, número, escritas alternativas possíveis para o mesmo termo (incluindo erros comuns) etc.

                    Separe cada item por vírgula. Gere {(NUMBER_OF_VECTOR_QUERIES + NUMBER_OF_TRADITIONAL_QUERIES)} expressões, sendo as {NUMBER_OF_VECTOR_QUERIES} primeiras para busca vetorial e as {NUMBER_OF_TRADITIONAL_QUERIES} últimas para busca lexical exata.
                    Segue a consulta real.
                    
                    {f"Histórico da Conversa: {historico_str}." if historico_str else ""}
                    Consulta: {consulta}.

                    Resultado (apenas termos e expressões separados por vírgula):
                """
        raw_output = llm.complete(prompt)
        
        if messages.MENSAGEM_CONSULTA_VETORIAL_GERADA:
            yield messages.MENSAGEM_CONSULTA_VETORIAL_GERADA
        
        nos = query_engine.custom_global_query(raw_output)
        num_documentos = len(nos) 
        if messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS:
            yield messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS.format(num_documentos=num_documentos)
        
        resposta = query_engine.custom_query(consulta, historico_str or "", nos)
        print("segundo output gerado, deve ser json válido: :")
        print(resposta)
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
            ],
            "palavras_chave" : str(raw_output).split(","),
            "links_analisados": [f"{URL_ATOM}/index.php/" + no["slug"] for no in nos]
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
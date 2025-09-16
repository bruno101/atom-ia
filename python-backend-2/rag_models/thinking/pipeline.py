# Pipeline principal do sistema RAG
# Orquestra todo o fluxo de processamento de consultas do usuário
from .validation import (
    extrair_json_da_resposta,
    validando,
    formatando_respostas
)
from . import messages
from .config import NUMBER_OF_VECTOR_QUERIES, NUMBER_OF_TRADITIONAL_QUERIES, MAX_QUERY_CHARS
import json
import os
from dotenv import load_dotenv
import time

async def pipeline_stream(consulta, historico=None, query_engine=None, llm=None, urls_validas=None):
    """Pipeline principal para processamento de consultas com streaming de progresso
    
    Args:
        consulta (str): Consulta do usuário
        historico (str, optional): Histórico da conversa
        query_engine: Motor de consulta RAG
        llm: Modelo de linguagem
        urls_validas (list): Lista de urls válidas do banco
        
    Yields:
        str: Mensagens de progresso e resultado final
    """
    
    # Calcula o tamanho máximo do histórico baseado no limite de caracteres
    tamanho_maximo_historico = max(MAX_QUERY_CHARS - len(consulta), 0)
    # Trunca o histórico se necessário, mantendo pelo menos 100 caracteres
    historico_str = historico[:tamanho_maximo_historico] if historico and tamanho_maximo_historico >= 100 else ""
        
    if messages.MENSAGEM_PIPELINE_INICIALIZANDO:
        yield messages.MENSAGEM_PIPELINE_INICIALIZANDO
    
    try:
        prompt = f"""
                    Extraia as palavras-chave E expressões curtas mais importantes e relevantes para busca vetorial e lexical de documentos que ajudem a responder a consulta que será dada ao fim dessa prompt.
                    Sua tarefa é determinar o que é adequado para busca vetorial e o que é adequado para busca lexical com BM25.

                    Para a **busca vetorial com Multilingual Instruct**, produza exatamente {NUMBER_OF_VECTOR_QUERIES - 1} consultas robustas:
                    - Cada consulta deve ter de 4 a 15 palavras em português, sem vírgulas internas.
                    - As consultas devem ser instruções com comandos e escritas em linguagem natural.
                    - Priorize consultas no imperativo.
                    - Use comandos completos e naturais que incluam:
                    - o tema principal,
                    - sinônimos e variações de grafia relevantes,
                    - entidades, datas, locais e instituições associadas,
                    - subtemas ou facetas relacionadas (ex.: suportes documentais, personagens, eventos).
                    - Não gere consultas redundantes: cada uma deve focar em um aspecto diferente do tema.

                    Para a **busca lexical com BM25**, produza {NUMBER_OF_TRADITIONAL_QUERIES} expressões com palavras relevantes:
                    - Priorize consultas que possuem entre 3 e 8 palavras em português, incluindo variações de escrita dos termos principais
                    - Inclua variações de gênero, número e grafia,
                    - Inclua formas alternativas de escrever o mesmo termo (incluindo erros comuns),
                    - Inclua sinônimos e alguns termos relacionados ao termo principal
                    - Algumas das expressões devem combinar mais de um termo relevante

                    Exemplo:
                    Se a consulta fosse "Estou pesquisando sobre a história dos judeus no Brasil":
                    1) as consultas "Encontre documentos históricos sobre judeus no Brasil, Pesquise sobre chegada dos cristão-novos no Brasil, Busque sobre antissemitismo no Brasil historicamente" etc. seriam adequadas para busca vetorial, pois são comandos/instruções/perguntas e consideram variações do tema e termos relacionados.
                    2) as consultas "historia história judeu judeu judeus brasil,história historia judeu judeus judaico judaica judio judios,historia cristão-novo cristão-novos cristãos novos cristãos-novos brasil brazil,inquisição judeus,antissemitismo anti-semitismo brasil,história historia hebreus hebraico, historia Israel Brasil" seriam adequadas para busca lexical, pois são expressões com palavras relevantes que incluem variações de grafia, gênero, número, escritas arcaicas ou alternativas possíveis para o mesmo termo (incluindo erros comuns), versões com ou sem acentos/diacríticos, além de alguns sinônimos/hiperônimos/palavras relacionadas etc.

                    Separe cada item por vírgula. Gere {(NUMBER_OF_VECTOR_QUERIES + NUMBER_OF_TRADITIONAL_QUERIES)} expressões, sendo as {NUMBER_OF_VECTOR_QUERIES} primeiras para busca vetorial e as {NUMBER_OF_TRADITIONAL_QUERIES} últimas para busca lexical.
                    Segue a consulta real.
                    
                    {f"Histórico da Conversa: {historico_str}." if historico_str else ""}
                    Consulta: {consulta}.

                    Resultado (apenas termos e expressões separados por vírgula):
                """        
        
        raw_output = None
        max_attempts = 10  # Número máximo de tentativas
        sleep_durations = [3, 5, 7, 9, 11, 13, 15, 17, 19]  # Tempos de espera entre tentativas
        
        # Sistema de retry para lidar com falhas temporárias da API
        for attempt in range(max_attempts):
            try:
                # Faz a chamada para o modelo LLM com timeout de 60s
                import threading
                result = [None]
                exception = [None]
                
                def llm_call():
                    try:
                        result[0] = llm.complete(prompt)
                    except Exception as e:
                        exception[0] = e
                
                thread = threading.Thread(target=llm_call)
                thread.daemon = True
                thread.start()
                thread.join(timeout=60)  # 60s timeout
                
                if thread.is_alive():
                    print(f"DEBUG: Timeout na chamada LLM (tentativa {attempt + 1}/{max_attempts})")
                    raw_output = None
                elif exception[0]:
                    raise exception[0]
                else:
                    raw_output = result[0]

                # Se recebeu uma resposta válida, sai do loop
                if raw_output and str(raw_output):
                    print(f"DEBUG: Resposta válida recebida na tentativa {attempt + 1}.")
                    break
                    
            except Exception as e:
                print(f"DEBUG: Erro na chamada LLM (tentativa {attempt + 1}/{max_attempts}): {str(e)}")
                raw_output = None

            # Se a resposta está vazia/erro e ainda há tentativas restantes
            if attempt < max_attempts - 1:
                sleep_time = sleep_durations[attempt]
                print(f"DEBUG: Tentando novamente em {sleep_time} segundos... (Tentativa {attempt + 2}/{max_attempts})")
                time.sleep(sleep_time)
            else:
                # Esta foi a última tentativa
                print("DEBUG: Falha após todas as tentativas.") 
                final_erro = {
                        "resposta": "Desculpe, ocorreu um erro na requisição da API. Tente novamente em alguns minutos.",
                        "links": [],
                        "palavras_chave": str(raw_output).split(",") if raw_output else [],
                        "links_analisados": []
                }
                yield f"FINAL_RESULT::{json.dumps(final_erro, ensure_ascii=False)}"
                return
        
        if messages.MENSAGEM_CONSULTA_VETORIAL_GERADA:
            yield messages.MENSAGEM_CONSULTA_VETORIAL_GERADA
        
        nos = query_engine.custom_global_query(raw_output, consulta)
        num_documentos = len(nos) 
        if messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS:
            yield messages.MENSAGEM_DOCUMENTOS_ENCONTRADOS.format(num_documentos=num_documentos)
        
        resposta_json_validada = None
        
        # Sistema de retry para extração e validação do JSON
        for attempt in range(max_attempts):
            try:
                resposta = query_engine.custom_query(consulta, historico_str or "", nos)
                if not resposta:
                    raise ValueError("Resposta vazia.")
                print("segundo output gerado, deve ser json válido: :")
                print(resposta)
                resposta_json = extrair_json_da_resposta(resposta)
                try:
                    numero_paginas = len(resposta_json["data"]["paginas"])
                    if messages.MENSAGEM_PAGINAS_SELECIONADAS:
                        yield messages.MENSAGEM_PAGINAS_SELECIONADAS.format(numero_paginas=numero_paginas)
                except:
                    print("Exceção calculando número de páginas. Continuando com a validação.")
                    
                resposta_json_validada = validando(resposta_json, urls_validas)
                break  # Se chegou até aqui, deu certo
                
            except Exception as e:
                print(f"Erro na extração/validação do JSON (tentativa {attempt + 1}/{max_attempts}): {str(e)}")
                if attempt < max_attempts - 1:
                    sleep_time = sleep_durations[attempt]
                    print(f"Tentando novamente em {sleep_time} segundos...")
                    time.sleep(sleep_time)
                else:
                    # Após todas as tentativas falharem, retorna erro ao usuário
                    final_erro = {
                        "resposta": "Desculpe, ocorreu um erro na requisição da API. Tente novamente em alguns minutos.",
                        "links": [],
                        "palavras_chave": str(raw_output).split(","),
                        "links_analisados": [no["url"] for no in nos]
                    }
                    yield f"FINAL_RESULT::{json.dumps(final_erro, ensure_ascii=False)}"
                    return
                    
        if messages.MENSAGEM_RESPOSTA_VALIDADA:
            yield messages.MENSAGEM_RESPOSTA_VALIDADA

        resposta_textual = formatando_respostas(resposta_json_validada, consulta, llm, historico_str or "")

        final = {
            "resposta": resposta_textual,
            "links": [
                {
                    "url": p.get('url', ''),
                    "title": p.get('titulo', ''),
                    "justificativa": p.get('justificativa', None),
                    "descricao": p.get('descricao', None)
                }
                for p in resposta_json_validada.get('data', {}).get('paginas', [])
            ],
            "palavras_chave" : str(raw_output).split(","),
            "links_analisados": [no["url"] for no in nos]
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
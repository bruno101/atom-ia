# Módulo de validação e formatação de respostas
# Responsável por validar urls, extrair JSON e formatar respostas finais
import json
import re
from rapidfuzz import process
import os
import time
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
# URL base do sistema para geração de links
URL_ATOM = os.getenv('URL_ATOM', 'http://localhost:63001')

def remover_urls_duplicadas(nodes):
    """Remove nós duplicados baseado na url
    
    Args:
        nodes (list): Lista de nós com urls
        
    Returns:
        list: Lista de nós únicos (sem duplicatas)
    """
    seen_urls = set()  # Conjunto para rastrear urls já vistos
    unique_nodes = []   # Lista de nós únicos

    for node in nodes:
        url = node["url"]
        # Adiciona apenas se a url existe e não foi visto antes
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_nodes.append(node)

    return unique_nodes

def extrair_json_da_resposta(texto):
    """Extrai JSON da resposta do modelo de linguagem
    
    Args:
        texto (str): Texto da resposta do modelo
        
    Returns:
        dict: JSON extraído ou estrutura padrão em caso de erro
    """
    # Usa regex para capturar o primeiro bloco JSON entre chaves
    match = re.search(r'\{[\s\S]*\}', texto)
    if not match:
        print("Não foi possível extrair JSON da resposta do modelo.")
        return {"data": {"paginas": []}}  # Retorna estrutura vazia padrão
    
    json_str = match.group()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return {"data": {"paginas": []}}  # Retorna estrutura vazia em caso de erro
    
def corrigir_url(url_modelo, urls_validas):
    """Corrige url usando busca fuzzy para encontrar correspondência mais próxima
    
    Args:
        url_modelo (str): Url gerada pelo modelo
        urls_validas (list): Lista de urls válidas do banco
        
    Returns:
        str or None: Url corrigida ou None se não encontrar correspondência
    """
    # Usa RapidFuzz para encontrar a melhor correspondência com score mínimo de 90%
    match = process.extractOne(url_modelo, urls_validas, score_cutoff=90)
    
    if match:
        melhor, _, _ = match  # Desempacota: (melhor_match, score, index)
        return melhor
    
    return None  # Retorna None se não encontrar correspondência suficiente

def validando(resposta_json, urls_validas):
    """Valida e corrige urls na resposta JSON
    
    Args:
        resposta_json (dict): JSON com páginas recomendadas
        urls_validas (list): Lista de urls válidos do banco
        
    Returns:
        dict: JSON validado com urls corrigidos
        
    Raises:
        ValueError: Se a estrutura JSON for inválida
    """
    # Verifica se a estrutura JSON é válida
    if 'data' not in resposta_json or 'paginas' not in resposta_json['data']:
        raise ValueError("Estrutura JSON inesperada. 'data' ou 'paginas' ausente.")

    # Valida cada página na resposta
    for i, pagina in enumerate(resposta_json['data']['paginas']):
        url = pagina.get('url') 
        if not url:
            continue  # Pula páginas sem url

        # Verifica se a url existe na base de dados
        if url not in urls_validas:
            # Tenta corrigir o url usando busca fuzzy
            url_corrigida = corrigir_url(url, urls_validas)
            if url_corrigida:
                pagina['url'] = url_corrigida  # Atualiza com url corrigido
            else:
                # Remove página se não conseguir corrigir o url
                resposta_json['data']['paginas'].pop(i)
        
        # Adiciona campos obrigatórios à página
        pagina['title'] = pagina.get('title', '')
        pagina['descricao'] = pagina.get('descricao', None) 
        pagina['justificativa'] = pagina.get('justificativa', None) 
    
    return resposta_json

def formatando_respostas(resposta_json, consulta, llm, historico_str=None):
    """Formata a resposta JSON em texto natural usando o modelo de linguagem
    
    Args:
        resposta_json (dict): JSON com páginas validadas
        consulta (str): Consulta original do usuário
        llm: Modelo de linguagem para geração de texto
        historico_str (str, optional): Histórico da conversa
        
    Returns:
        str: Resposta formatada em texto natural
    """
    # Prompt para formatar a resposta em linguagem natural
    prompt = f'''
Você é um assistente que recomenda páginas para ajudar na pesquisa.\n

{f"Atenção às mensagens anteriores do usuário para que você entenda o contexto da conversa. Histórico de Conversa: {historico_str}." if historico_str else ""}
\nSegue a consulta que deve ser respondida. Consulta: "{consulta}".\n

Com base neste JSON:
{json.dumps(resposta_json, ensure_ascii=False, indent=2)}

Recomende todas as páginas listadas no JSON - na ordem em que são listadas - , explique por que são úteis e forneça o link em notação correta de markdown, conforme exemplos abaixo.

Responda em português, de forma clara e objetiva. Se não houver informações relevantes ou evidências claras no contexto acima, informe isso explicitamente. Lembre-se de que você está respondendo a uma consulta do usuário, então não mencione o fato de que você recebeu uma lista de informações.

Exemplo de como formatar com markdown as recomendações:
"*   **Título da página XYZ.**\n    [Comentário sobre página XYZ, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página XYZ](Link para a página XYZ, copiado exatamente como aparece no campo "url")\n\n"
"*   **Título da página ABC.**\n    [Comentário sobre página ABC, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página ABC](Link para a página ABC, copiado exatamente como aparece no campo "url")\n\n"
"*   **Título da página DEF.**\n    [Comentário sobre página DEF, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página DEF](Link para a página DEF, copiado exatamente como aparece no campo "url")\n\n"
"*   **Título da página GHI.**\n    [Comentário sobre página GHI, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página GHI](Link para a página GHI, copiado exatamente como aparece no campo "url")\n\n"
'''
    output = None
    max_attempts = 10  # Número máximo de tentativas
    sleep_durations = [3, 5, 7, 9, 11, 13, 15, 17, 19]  # Tempos de espera entre tentativas
        
    # Sistema de retry para lidar com falhas temporárias da API
    for attempt in range(max_attempts):
        # Faz a chamada para o modelo LLM
        output = llm.complete(prompt=prompt).text

        # Se recebeu uma resposta válida, sai do loop
        if output and str(output):
            print(f"DEBUG: Resposta válida recebida na tentativa {attempt + 1}.")
            break

        # Se a resposta está vazia e ainda há tentativas restantes
        if attempt < max_attempts - 1:
            sleep_time = sleep_durations[attempt]
            print(f"DEBUG: Resposta vazia. Tentando novamente em {sleep_time} segundos... (Tentativa {attempt + 2}/{max_attempts})")
            time.sleep(sleep_time)
        else:
           # Esta foi a última tentativa
            print("DEBUG: Resposta ainda vazia após todas as tentativas.") 
            output = "Desculpe, ocorreu um erro na requisição da API. Tente novamente em alguns minutos."
    
    # Gera resposta formatada usando o modelo de linguagem
    return output
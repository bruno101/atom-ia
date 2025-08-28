# Módulo de validação e formatação de respostas
# Responsável por validar slugs, extrair JSON e formatar respostas finais
import json
import re
from rapidfuzz import process
from db_connection import fetch_slugs
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
# URL base do sistema para geração de links
URL_ATOM = os.getenv('URL_ATOM', 'http://localhost:63001')

def remover_slugs_duplicadas(nodes):
    """Remove nós duplicados baseado no slug
    
    Args:
        nodes (list): Lista de nós com slugs
        
    Returns:
        list: Lista de nós únicos (sem duplicatas)
    """
    seen_slugs = set()  # Conjunto para rastrear slugs já vistos
    unique_nodes = []   # Lista de nós únicos

    for node in nodes:
        slug = node["slug"]
        # Adiciona apenas se o slug existe e não foi visto antes
        if slug and slug not in seen_slugs:
            seen_slugs.add(slug)
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
    
def corrigir_slug(slug_modelo, slugs_validos):
    """Corrige slug usando busca fuzzy para encontrar correspondência mais próxima
    
    Args:
        slug_modelo (str): Slug gerado pelo modelo
        slugs_validos (list): Lista de slugs válidos do banco
        
    Returns:
        str or None: Slug corrigido ou None se não encontrar correspondência
    """
    # Usa RapidFuzz para encontrar a melhor correspondência com score mínimo de 90%
    match = process.extractOne(slug_modelo, slugs_validos, score_cutoff=90)
    
    if match:
        melhor, _, _ = match  # Desempacota: (melhor_match, score, index)
        return melhor
    
    return None  # Retorna None se não encontrar correspondência suficiente

def validando(resposta_json, slugs_validos):
    """Valida e corrige slugs na resposta JSON
    
    Args:
        resposta_json (dict): JSON com páginas recomendadas
        slugs_validos (list): Lista de slugs válidos do banco
        
    Returns:
        dict: JSON validado com slugs corrigidos
        
    Raises:
        ValueError: Se a estrutura JSON for inválida
    """
    # Verifica se a estrutura JSON é válida
    if 'data' not in resposta_json or 'paginas' not in resposta_json['data']:
        raise ValueError("Estrutura JSON inesperada. 'data' ou 'paginas' ausente.")

    # Valida cada página na resposta
    for i, pagina in enumerate(resposta_json['data']['paginas']):
        slug = pagina.get('slug') 
        if not slug:
            continue  # Pula páginas sem slug

        # Verifica se o slug existe na base de dados
        if slug not in slugs_validos:
            # Tenta corrigir o slug usando busca fuzzy
            slug_corrigido = corrigir_slug(slug, slugs_validos)
            if slug_corrigido:
                pagina['slug'] = slug_corrigido  # Atualiza com slug corrigido
            else:
                # Remove página se não conseguir corrigir o slug
                resposta_json['data']['paginas'].pop(i)
        
        # Adiciona campos obrigatórios à página
        pagina['url'] = f"{URL_ATOM}/index.php/{pagina.get('slug', '')}"
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
Você é um assistente que recomenda páginas do AtoM para ajudar na pesquisa.\n

{f"Atenção às mensagens anteriores do usuário para que você entenda o contexto da conversa. Histórico de Conversa: {historico_str}." if historico_str else ""}
\nSegue a consulta que deve ser respondida. Consulta: "{consulta}".\n

Com base neste JSON:
{json.dumps(resposta_json, ensure_ascii=False, indent=2)}

Recomende as páginas listadas no JSON - na ordem em que são listadas - , explique por que são úteis e forneça o link completo no formato:
{URL_ATOM}/index.php/{{slug}}

Responda em português, de forma clara e objetiva. Se não houver informações relevantes ou evidências claras no contexto acima, informe isso explicitamente. Lembre-se de que você está respondendo a uma consulta do usuário, então não mencione o fato de que você recebeu uma lista de informações.

Exemplo de como formatar com markdown uma das recomendações:
"*   **[Título da página XYZ.]**\n    [Comentário sobre página XYZ, que pode, por exemplo, explicar a sua utilidade para a busca].\n    Link: [Link para a página XYZ]\n\n"
'''
    # Gera resposta formatada usando o modelo de linguagem
    return llm.complete(prompt=prompt).text
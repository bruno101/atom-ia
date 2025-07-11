import json
import re
from rapidfuzz import process
from db_connection import fetch_slugs

def extrair_json_da_resposta(texto):
    # Tenta capturar o primeiro bloco JSON entre chaves
    match = re.search(r'\{[\s\S]*\}', texto)
    if not match:
        raise ValueError("Não foi possível extrair JSON da resposta do modelo.")
    
    json_str = match.group()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar JSON: {e}")
    
def corrigir_slug(slug_modelo, slugs_validos):
    melhor, _, _ = process.extractOne(slug_modelo, slugs_validos, score_cutoff=90)
    return melhor if melhor else None

def validando(resposta_json, slugs_validos):
    if 'data' not in resposta_json or 'paginas' not in resposta_json['data']:
        raise ValueError("Estrutura JSON inesperada. 'data' ou 'paginas' ausente.")

    for i, pagina in enumerate(resposta_json['data']['paginas']):
        slug = pagina.get('slug') 
        if not slug:
            continue

        if slug not in slugs_validos:
            slug_corrigido = corrigir_slug(slug, slugs_validos)
            if slug_corrigido:
                pagina['slug'] = slug_corrigido
            else:
                resposta_json['data']['paginas'].pop(i)
        pagina['url'] = f"http://localhost:63001/index.php/{pagina.get('slug', '')}"
        pagina['title'] = pagina.get('title', '')
        pagina['descricao'] = pagina.get('descricao', None) 
        pagina['justificativa'] = pagina.get('justificativa', None) 
    
    return resposta_json

def formatando_respostas(resposta_json, consulta, llm):
    prompt = f'''
Você é um assistente que recomenda páginas do AtoM para ajudar na pesquisa.

Consulta: "{consulta}"

Com base neste JSON:
{json.dumps(resposta_json, ensure_ascii=False, indent=2)}

Recomende as páginas listadas no JSON - na ordem em que são listadas - , explique por que são úteis e forneça o link completo no formato:
http://localhost:63001/index.php/{{slug}}

Responda em português, de forma clara e objetiva. Se não houver informações relevantes ou evidências claras no contexto acima, informe isso explicitamente. Lembre-se de que você está respondendo a uma consulta do usuário, então não mencione o fato de que você recebeu uma lista de informações.
'''
    return llm.complete(prompt=prompt).text
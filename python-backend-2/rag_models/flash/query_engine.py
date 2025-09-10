from .utils import remover_urls_duplicadas
from .config import MAX_QUERY_CHARS, MAX_NODES_VECTOR_QUERY, MAX_NODES_TRADITIONAL_QUERY, MAX_CHARS_PER_NODE
from vector_search import search_similar_documents
from text_search import search_documents_by_text
import json

def vector_query(consulta):
    nos = search_similar_documents(consulta[:MAX_QUERY_CHARS], n_results=MAX_NODES_VECTOR_QUERY)
    nos_reformatados = [{"text": no["text"][:MAX_CHARS_PER_NODE], "url": no["url"], "title": no["title"]} for no in nos]
    return nos_reformatados

def traditional_query(consulta):
    nos = search_documents_by_text([consulta[:MAX_QUERY_CHARS]], MAX_NODES_TRADITIONAL_QUERY)
    nos_reformatados = [{"text": no["text"][:MAX_CHARS_PER_NODE], "url": no["url"], "title": no["title"]} for no in nos]
    return nos_reformatados

def global_query(consulta):
    nos_vetoriais = vector_query(consulta)
    nos_tradicionais = traditional_query(consulta)
    nos = nos_vetoriais + nos_tradicionais
    nos_sem_duplicatas = remover_urls_duplicadas(nos)
    return nos_sem_duplicatas


def llm_query(llm, consulta, historico_str, nos):
    prompt = f'''
        Você é um assistente que recomenda páginas para ajudar na pesquisa.\n

        {f"Atenção às mensagens anteriores do usuário para que você entenda o contexto da conversa. Histórico de Conversa: {historico_str}." if historico_str else ""}
        \nSegue a consulta que deve ser respondida. Consulta: "{consulta}".\n

        Com base neste JSON:
        {json.dumps(nos, ensure_ascii=False, indent=2)}

        Recomende as páginas listadas no JSON mais relevantes para a consulta - em ordem de relevância - , explique por que são úteis e forneça o link em notação correta de markdown, conforme exemplos abaixo. Tente recomendar pelo menos cinco páginas, mesmo que isso signifique adicionar páginas que são apenas tangencialmente relacionadas. Caso a página seja apenas tangencialmente ou fracamente relacionada, mencione isso explicitamente.

        Responda em português, de forma clara e objetiva. Lembre-se de que você está respondendo a uma consulta do usuário, então não mencione o fato de que você recebeu uma lista de informações ou um JSON.

        Exemplo de como formatar com markdown as recomendações:
        "*   **Título da página XYZ.**\n    [Comentário sobre página XYZ, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página XYZ](Link para a página XYZ, copiado exatamente como aparece no campo "url")\n\n"
        "*   **Título da página ABC.**\n    [Comentário sobre página ABC, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página ABC](Link para a página ABC, copiado exatamente como aparece no campo "url")\n\n"
        "*   **Título da página DEF.**\n    [Comentário sobre página DEF, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página DEF](Link para a página DEF, copiado exatamente como aparece no campo "url")\n\n"
        "*   **Título da página GHI.**\n    [Comentário sobre página GHI, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página GHI](Link para a página GHI, copiado exatamente como aparece no campo "url")\n\n"
        '''
    print("prompt é " + prompt)
    for chunk in llm.stream_complete(prompt=prompt):
        yield f"PARTIAL_RESPONSE:{chunk.delta}"
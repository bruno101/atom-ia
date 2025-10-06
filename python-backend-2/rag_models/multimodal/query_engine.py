from .utils import remover_urls_duplicadas
from .config import MAX_QUERY_CHARS, MAX_NODES_VECTOR_QUERY, MAX_NODES_TRADITIONAL_QUERY, MAX_CHARS_PER_NODE, GEMINI_API, LLM_EXPANSIONS_MODEL, GEMINI_API_PROVIDER, PROJECT_ID, LOCATION, NUMBER_OF_MULTIMODAL_QUERY_EXPANSIONS
from vector_search import search_similar_documents
from text_search import search_documents_by_text
import json
import logging
import vertexai
from vertexai.generative_models import GenerativeModel
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Initialize expansion LLM
if GEMINI_API_PROVIDER == "vertex":
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    expansion_llm = GenerativeModel(LLM_EXPANSIONS_MODEL)
else:
    genai.configure(api_key=GEMINI_API)
    expansion_llm = genai.GenerativeModel(LLM_EXPANSIONS_MODEL)

def vector_query(consulta):
    nos = search_similar_documents(consulta[:MAX_QUERY_CHARS], n_results=MAX_NODES_VECTOR_QUERY)
    nos_reformatados = [{"text": no["text"][:MAX_CHARS_PER_NODE], "url": no["url"], "title": no["title"]} for no in nos]
    return nos_reformatados

def traditional_query(consulta):
    nos = search_documents_by_text([consulta[:MAX_QUERY_CHARS]], MAX_NODES_TRADITIONAL_QUERY, expand=False)
    nos_reformatados = [{"text": no["text"][:MAX_CHARS_PER_NODE], "url": no["url"], "title": no["title"]} for no in nos]
    return nos_reformatados

def global_query(consulta):
    logger.debug(f"Executing global query for: '{consulta[:100]}...'")
    nos_vetoriais = vector_query(consulta)
    nos_tradicionais = traditional_query(consulta)
    nos = nos_vetoriais + nos_tradicionais
    nos_sem_duplicatas = remover_urls_duplicadas(nos)
    logger.debug(f"Found {len(nos_sem_duplicatas)} unique documents")
    return nos_sem_duplicatas

def expand_multimodal_query(user_query, file_type, transcription, n=NUMBER_OF_MULTIMODAL_QUERY_EXPANSIONS):
    logger.info(f"Expanding multimodal query: '{user_query[:100]}...' for file type: {file_type}")
    
    combined_prompt = f'''Baseado na consulta e arquivo, faça duas tarefas:

1. Gere {n} consultas de busca equivalentes em português que incorporem o contexto do arquivo
2. Crie um resumo conciso de 2-3 frases sobre o conteúdo do arquivo

Consulta original: "{user_query[:1000]}"
Tipo de arquivo: {file_type}
Transcrição: {transcription[:2500]}

Responda EXATAMENTE no formato abaixo, sem usar markdown ou formatação especial:

QUERIES:
Computadores após a Segunda Guerra Mundial
Evolução dos computadores após 1945
Expansão do uso de computadores no pós-guerra

SUMMARY:
O arquivo trata sobre a evolução da tecnologia de computadores após a Segunda Guerra Mundial.'''
    
    response = expansion_llm.generate_content(combined_prompt)
    text = response.text.strip()
    
    queries_section = text.split('SUMMARY:')[0].replace('QUERIES:', '').strip()
    summary_section = text.split('SUMMARY:')[1].strip() if 'SUMMARY:' in text else ""
    queries = [q.strip() for q in queries_section.split('\n') if q.strip() and not q.startswith('```') and len(q.strip()) > 3]
    file_summary = summary_section
    
    logger.info(f"Generated {len(queries)} expanded queries and file summary")
    return queries[:n], file_summary


def llm_query(llm, consulta, historico_str, nos, file_summary=None):
    prompt = f'''
        Você é um assistente que recomenda páginas para ajudar na pesquisa.\n

        {f"Atenção às mensagens anteriores do usuário para que você entenda o contexto da conversa. Histórico de Conversa: {historico_str}." if historico_str else ""}
        {f"\nContexto de um arquivo anexado à consulta: {file_summary}" if file_summary else ""}
        \nSegue a consulta que deve ser respondida. Consulta: "{consulta}".\n

        Com base neste JSON:
        {json.dumps(nos, ensure_ascii=False, indent=2)}

        Recomende as páginas listadas no JSON mais relevantes para a consulta - em ordem de relevância - , explique por que são úteis e forneça o link em notação correta de markdown, conforme exemplos abaixo. Tente recomendar pelo menos cinco páginas, mesmo que isso signifique adicionar páginas que são apenas tangencialmente relacionadas. Apenas caso não haja absolutamente nenhuma relação liste menos que cinco páginas. Caso a página seja apenas tangencialmente ou fracamente relacionada, mencione isso explicitamente. As páginas são completamente independentes umas das outras, então garanta que a análise sobre uma não a confunda com outra.

        Responda em português, de forma clara e objetiva. Lembre-se de que você está respondendo a uma consulta do usuário, então não mencione o fato de que você recebeu uma lista de informações ou um JSON. Além disso, é extremamente importante que os links sejam copiados exatamente como estão em "url", sem modificações.

        Exemplo de como formatar com markdown as recomendações:
        "*   **Título da página XYZ.**\n    [Comentário sobre página XYZ, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página XYZ](Link para a página XYZ, copiado exatamente como aparece no campo "url")\n\n"
        "*   **Título da página ABC.**\n    [Comentário sobre página ABC, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página ABC](Link para a página ABC, copiado exatamente como aparece no campo "url")\n\n"
        "*   **Título da página DEF.**\n    [Comentário sobre página DEF, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página DEF](Link para a página DEF, copiado exatamente como aparece no campo "url")\n\n"
        "*   **Título da página GHI.**\n    [Comentário sobre página GHI, que pode, por exemplo, explicar a sua utilidade para a busca].\n    [Texto do link para a página GHI](Link para a página GHI, copiado exatamente como aparece no campo "url")\n\n"
        '''
    print("prompt é " + prompt)
    
    
    response = llm.generate_content(prompt, stream=True)
    for chunk in response:
        yield f"PARTIAL_RESPONSE:{chunk.text}"

    print("Acabou o stream")
    
    return
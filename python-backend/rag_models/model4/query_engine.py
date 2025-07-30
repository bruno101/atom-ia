from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.response_synthesizers import BaseSynthesizer, get_response_synthesizer
from llama_index.core import PromptTemplate
from llama_index.llms.google_genai import GoogleGenAI
from fetch_documents import fetch_documents_from_db, fetch_documents_from_elastic_search
from .config import NODES_PER_VECTOR_QUERY, NODES_PER_TRADITIONAL_QUERY, MAX_CHARS_PER_NODE, MAX_QUERY_CHARS, NUMBER_OF_TRADITIONAL_QUERIES, NUMBER_OF_VECTOR_QUERIES, MAX_NODES_VECTOR_QUERY, MAX_NODES_TRADITIONAL_QUERY
from .validation import remover_slugs_duplicadas

qa_prompt = PromptTemplate(
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "Given the context information and not prior knowledge, answer the query.\n"
    "Responda em português.\n"
    """Somente responda em json
    Formato resposta em json
    {"data": {
      "paginas": [
        {
        "slug": "Slug da página recomendada",
        "title": "Titulo da página recomendada",
        "descricao": "Descrição resumida do conteúdo da página",
        "justificativa": "Motivo da recomendação e como essa página pode ajudar na pesquisa"
      }
      ]
    }}
    Caso não encontre informações sobre o tema específico, recomende as informações mais relevantes ou relacionadas possíveis. Recomende o máximo possível de documentos relacionados ao tema. Idealmente, retorne pelo menos cinco links. Formate a sua resposta de forma esteticamente agradável, com o uso de markdown.
    Só recomende slugs dessa base de dados. Os slugs são identificadores técnicos. Eles **devem ser copiados exatamente como estão na base**, sem nenhuma alteração. NÃO insira, remova ou modifique hífens, acentos ou letras. Apenas use os slugs retornados pela base.
"""
    "---------------------\n"
    "{historico_str}"
    "\Segue a consulta que deve ser respondida. Consulta: {query_str}\n"
    "Resposta: "
)

# Query engine
class RAGStringQueryEngine(CustomQueryEngine):
    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: GoogleGenAI
    qa_prompt: PromptTemplate
    
    def custom_vector_query(self, consultas_vetoriais: list[str]):
        nos = []
        for consulta_vetorial in consultas_vetoriais:
            nos = nos + self.retriever.retrieve(f"query: {consulta_vetorial}")
        nos_reformatados = [{"slug":no.metadata.get("slug"), "content":no.get_content()} for no in nos]
        print("Busca vetorial encontrou: ", len(nos_reformatados))
        return nos_reformatados[:MAX_NODES_VECTOR_QUERY]
    
    def custom_traditional_query(self, consultas_tradicionais: list[str]):
        nos = []
        resultados = fetch_documents_from_elastic_search(consultas_tradicionais, NODES_PER_TRADITIONAL_QUERY)
        for resultado in resultados:
            no = {"slug":resultado.doc_id, "content":resultado.text}
            nos = list(nos) + [no]
        print("Busca tradicional encontrou: ", len(nos))
        return nos[:MAX_NODES_TRADITIONAL_QUERY]
        
    def custom_global_query(self, keywords_raw_output):
        
        nos_consulta_tradicional = []
        nos_consulta_vetorial = []
        lista_consultas = str(keywords_raw_output).split(",")
        len_lista_consultas = len(lista_consultas)
        
        if (NUMBER_OF_TRADITIONAL_QUERIES > 0):
            lista_consultas_tradicionais = []
            if (len(lista_consultas) < NUMBER_OF_TRADITIONAL_QUERIES + NUMBER_OF_VECTOR_QUERIES):
                print("Ocorreu erro na geração das consultas tradicionais")
                lista_consultas_tradicionais = lista_consultas[:min(len_lista_consultas, NUMBER_OF_TRADITIONAL_QUERIES)]
            else:
                lista_consultas_tradicionais = str(keywords_raw_output).split(",")[NUMBER_OF_VECTOR_QUERIES:(NUMBER_OF_TRADITIONAL_QUERIES+NUMBER_OF_VECTOR_QUERIES)]
            
            consultas_tradicionais = [q.strip() for q in lista_consultas_tradicionais if q.strip()]
            print("Consultas tradicionais geradas: ", consultas_tradicionais)
            nos_consulta_tradicional = self.custom_traditional_query(consultas_tradicionais)
        
        if (NUMBER_OF_VECTOR_QUERIES > 0):
            lista_consultas_vectoriais = lista_consultas[:min(len_lista_consultas, NUMBER_OF_VECTOR_QUERIES)]
            consultas_vetoriais = [q.strip() for q in lista_consultas_vectoriais if q.strip()]
            print("Consultas vetoriais geradas: ", consultas_vetoriais)
            nos_consulta_vetorial = self.custom_vector_query(consultas_vetoriais)
        
        nos_com_repeticao = nos_consulta_vetorial + nos_consulta_tradicional
        nos = remover_slugs_duplicadas(nos_com_repeticao)
        
        return nos
        

    def custom_query(self, query_str: str, historico_str: str, nodes):
    
        clipped_nodes = []
        for i, n in enumerate(nodes):
            content = n["content"]
            slug = n["slug"]
            content = "Atenção! O seguinte é o slug da página, que, se necessário, deve ser copiado exatamente como está: ***" + slug + "***" + content
            clipped_content = content[:MAX_CHARS_PER_NODE]
            clipped_nodes.append(clipped_content)
        
        context_str = "\n\n".join(clipped_nodes)
        historico_instrucoes = "Atenção às mensagens anteriores do usuário para que você entenda o contexto da conversa. Histórico da conversa:\n" + historico_str if historico_str else ""
        #print("Prompt gerada foi: ", self.qa_prompt.format(context_str=context_str, query_str=query_str[:MAX_QUERY_CHARS], historico_str=historico_instrucoes))
        
        response = self.llm.complete(
            prompt = self.qa_prompt.format(context_str=context_str, query_str=query_str[:MAX_QUERY_CHARS], historico_str=historico_instrucoes)
        )
        return str(response)
    
def create_query_engine(index, llm):
    retriever = index.as_retriever(similarity_top_k=NODES_PER_VECTOR_QUERY, with_similarity=True)
    synthesizer = get_response_synthesizer(response_mode="compact", llm=llm)
    return RAGStringQueryEngine(
        retriever=retriever,
        response_synthesizer=synthesizer,
        llm=llm,
        qa_prompt=qa_prompt
    )
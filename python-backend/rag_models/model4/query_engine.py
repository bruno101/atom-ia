from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.response_synthesizers import BaseSynthesizer, get_response_synthesizer
from llama_index.core import PromptTemplate
from llama_index.llms.google_genai import GoogleGenAI
from .config import NODES_PER_VECTOR_QUERY, MAX_CHARS_PER_NODE, MAX_QUERY_CHARS
from .validation import remover_slugs_duplicadas

qa_prompt = PromptTemplate(
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "{historico_str}"
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
    "\nQuery: {query_str}\n"
    "Answer: "
)

# Query engine
class RAGStringQueryEngine(CustomQueryEngine):
    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: GoogleGenAI
    qa_prompt: PromptTemplate
    
    def custom_vector_query(self, consultas_vetoriais: list[str]):
        nos_com_repeticao = []
        for consulta_vetorial in consultas_vetoriais:
            nos_com_repeticao = nos_com_repeticao + self.retriever.retrieve(f"query: {consulta_vetorial}")
        nos = remover_slugs_duplicadas(nos_com_repeticao)
        return nos

    def custom_query(self, query_str: str, historico_str: str, nodes):
    
        clipped_nodes = []
        for i, n in enumerate(nodes):
            content = n.node.get_content()
            slug = n.node.metadata.get("slug", "[sem slug]")
            content = "Atenção! O seguinte é o slug da página, que, se necessário, deve ser copiado exatamente como está: ***" + slug + "***" + content
            clipped_content = content[:MAX_CHARS_PER_NODE]
            clipped_nodes.append(clipped_content)
            print("\n\n***************************\n\n")
            print(clipped_content)
        
        context_str = "\n\n".join(clipped_nodes)
        historico_limit = MAX_QUERY_CHARS - min(MAX_QUERY_CHARS, len(query_str))
        historico_instrucoes = "Histórico da conversa:\n" + historico_str[-historico_limit:] if historico_str and historico_limit>= 50 else ""
        print("query é: \n\n", self.qa_prompt.format(context_str=context_str, query_str=query_str[:MAX_QUERY_CHARS], historico_str=historico_instrucoes))
        
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
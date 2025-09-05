# Importações necessárias para o motor de consulta RAG
from llama_index.core import PromptTemplate
from llama_index.llms.google_genai import GoogleGenAI
from .config import NODES_PER_VECTOR_QUERY, NODES_PER_TRADITIONAL_QUERY, MAX_CHARS_PER_NODE, MAX_QUERY_CHARS, NUMBER_OF_TRADITIONAL_QUERIES, NUMBER_OF_VECTOR_QUERIES, MAX_NODES_VECTOR_QUERY, MAX_NODES_TRADITIONAL_QUERY
from .validation import remover_urls_duplicadas
from vector_search import search_similar_documents
from text_search import search_documents_by_text
import numpy as np
import time


# Template de prompt para geração de respostas em formato JSON
# Define como o modelo deve responder às consultas dos usuários
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
        "url": "Url da página recomendada",
        "titulo": "Titulo da página recomendada",
        "descricao": "Descrição resumida do conteúdo da página",
        "justificativa": "Motivo da recomendação e como essa página pode ajudar na pesquisa"
      }
      ]
    }}
    Caso não encontre informações sobre o tema específico, recomende as informações mais relevantes ou relacionadas possíveis. Recomende o máximo possível de documentos relacionados ao tema. Idealmente, retorne pelo menos cinco links. Formate a sua resposta de forma esteticamente agradável, com o uso de markdown.
    Só recomende urls dessa base de dados. Os urls são identificadores técnicos. Eles **devem ser copiados exatamente como estão na base**, sem nenhuma alteração. NÃO insira, remova ou modifique hífens, acentos ou letras. Apenas use as urls retornadas pela base.
"""
    "---------------------\n"
    "{historico_str}"
    "\nSegue a consulta que deve ser respondida. Consulta: {query_str}\n"
    "Resposta: "
)

# Motor de consulta RAG personalizado
# Combina busca vetorial e tradicional para recuperar documentos relevantes
class RAGStringQueryEngine:
    llm: GoogleGenAI
    qa_prompt: PromptTemplate
    
    def __init__(self, llm, qa_prompt):
            self.llm = llm
            self.qa_prompt = qa_prompt
    
    def custom_vector_query(self, consultas_vetoriais: list[str]):
        """Executa consultas vetoriais usando embeddings semânticos
        
        Args:
            consultas_vetoriais: Lista de strings para busca vetorial
            
        Returns:
            Lista de nós sem duplicatas limitada pelo MAX_NODES_VECTOR_QUERY
        """
        nos = []  # Lista para armazenar todos os nós recuperados
        for idx, consulta_vetorial in enumerate(consultas_vetoriais):
            # Recupera documentos usando busca vetorial com prefixo "query:"
            retrieved = search_similar_documents(consulta_vetorial, n_results=NODES_PER_VECTOR_QUERY)
            nos += retrieved  # Adiciona todos os nós recuperados à lista 

        # Reformata os nós para estrutura padronizada
        nos_reformatados = [{"text": no["text"], "url": no["url"], "title": no["title"]} for no in nos]
        print("Consulta vetorial achou: " + str(len(nos_reformatados)))
        # Remove duplicatas baseado na url
        nos_sem_duplicatas = remover_urls_duplicadas(nos_reformatados)
        return nos_sem_duplicatas[:MAX_NODES_VECTOR_QUERY]
    
    def custom_traditional_query(self, consultas_tradicionais: list[str]):
        """Executa consultas tradicionais usando Elasticsearch
        
        Args:
            consultas_tradicionais: Lista de strings para busca tradicional
            
        Returns:
            Lista de nós limitada pelo MAX_NODES_TRADITIONAL_QUERY
        """
        nos = []
        # Busca documentos no Elasticsearch usando consultas tradicionais
        resultados = search_documents_by_text(consultas_tradicionais, NODES_PER_TRADITIONAL_QUERY)
        print("Consulta tradicional achou: " + str(len(resultados)))
        
        for resultado in resultados:
            # Extrai o texto do resultado de forma segura
            no = {"text": resultado["text"], "url": resultado["url"], "title": resultado["title"]}
            nos.append(no)
            
        return nos[:MAX_NODES_TRADITIONAL_QUERY]
        
    def custom_global_query(self, keywords_raw_output):
        """Combina consultas vetoriais e tradicionais baseado nas palavras-chave
        
        Args:
            keywords_raw_output: String com palavras-chave separadas por vírgula
            
        Returns:
            Lista combinada de nós sem duplicatas
        """
        
        nos_consulta_tradicional = []
        nos_consulta_vetorial = []
        # Divide as palavras-chave em lista de consultas
        lista_consultas = str(keywords_raw_output).split(",")
        len_lista_consultas = len(lista_consultas)
        
        # Executa consultas tradicionais se configurado
        if (NUMBER_OF_TRADITIONAL_QUERIES > 0):
            lista_consultas_tradicionais = []
            # Distribui as consultas entre vetorial e tradicional
            if (len(lista_consultas) < NUMBER_OF_TRADITIONAL_QUERIES + NUMBER_OF_VECTOR_QUERIES):
                lista_consultas_tradicionais = lista_consultas[:min(len_lista_consultas, NUMBER_OF_TRADITIONAL_QUERIES)]
            else:
                lista_consultas_tradicionais = str(keywords_raw_output).split(",")[NUMBER_OF_VECTOR_QUERIES:(NUMBER_OF_TRADITIONAL_QUERIES+NUMBER_OF_VECTOR_QUERIES)]
            
            # Remove espaços em branco e consultas vazias
            consultas_tradicionais = [q.strip() for q in lista_consultas_tradicionais if q.strip()]
            nos_consulta_tradicional = self.custom_traditional_query(consultas_tradicionais)
        
        # Executa consultas vetoriais se configurado
        if (NUMBER_OF_VECTOR_QUERIES > 0):
            lista_consultas_vectoriais = lista_consultas[:min(len_lista_consultas, NUMBER_OF_VECTOR_QUERIES)]
            # Remove espaços em branco e consultas vazias
            consultas_vetoriais = [q.strip() for q in lista_consultas_vectoriais if q.strip()]
            nos_consulta_vetorial = self.custom_vector_query(consultas_vetoriais)
        
        # Combina resultados de ambas as consultas
        nos_com_repeticao = nos_consulta_vetorial + nos_consulta_tradicional
        # Remove duplicatas baseado na url
        nos = remover_urls_duplicadas(nos_com_repeticao)
        
        return nos
        

    def custom_query(self, query_str: str, historico_str: str, nodes):
        """Gera resposta final usando LLM com contexto dos documentos recuperados
        
        Args:
            query_str: Consulta do usuário
            historico_str: Histórico da conversa
            nodes: Lista de nós/documentos recuperados
            
        Returns:
            Resposta gerada pelo modelo em formato string
        """
    
        clipped_nodes = []
        # Processa cada nó para criar o contexto
        for i, n in enumerate(nodes):
            title = n["title"]
            content = n["text"]
            url = n["url"] 
            # Adiciona url  como identificador único no início do conteúdo
            content = "Atenção! O seguinte é a url da página, que, se necessário, deve ser copiada exatamente como está: ***" + url + "***\n título: " + title + "\n\n***conteúdo: " + content
            # Limita o tamanho do conteúdo para evitar excesso de tokens
            clipped_content = content[:MAX_CHARS_PER_NODE]
            clipped_nodes.append(clipped_content)
        
        # Junta todos os nós em uma string de contexto
        context_str = "\n\n".join(clipped_nodes)
        # Adiciona histórico da conversa se disponível
        historico_instrucoes = "Atenção às mensagens anteriores do usuário para que você entenda o contexto da conversa. Histórico da conversa:\n" + historico_str if historico_str else ""

        # Formata o prompt final com contexto, consulta e histórico
        final_prompt = self.qa_prompt.format(context_str=context_str, query_str=query_str[:MAX_QUERY_CHARS], historico_str=historico_instrucoes)
                
        response = self.llm.complete(prompt=final_prompt)      
    
        return str(response)
    
def create_query_engine(llm):
    """Cria uma instância do motor de consulta RAG
    
    Args:
        index: Índice vetorial do LlamaIndex
        llm: Modelo de linguagem (GoogleGenAI)
        
    Returns:
        Instância configurada do RAGStringQueryEngine
    """
    # Configura o recuperador com busca por similaridade
    
    return RAGStringQueryEngine(
        llm,
        qa_prompt
    )
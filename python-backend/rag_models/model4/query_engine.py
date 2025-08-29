# Importações necessárias para o motor de consulta RAG
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.response_synthesizers import BaseSynthesizer, get_response_synthesizer
from llama_index.core import PromptTemplate
from llama_index.llms.google_genai import GoogleGenAI
from fetch_documents import fetch_documents_from_db, fetch_documents_from_elastic_search
from .config import NODES_PER_VECTOR_QUERY, NODES_PER_TRADITIONAL_QUERY, MAX_CHARS_PER_NODE, MAX_QUERY_CHARS, NUMBER_OF_TRADITIONAL_QUERIES, NUMBER_OF_VECTOR_QUERIES, MAX_NODES_VECTOR_QUERY, MAX_NODES_TRADITIONAL_QUERY
from .validation import remover_slugs_duplicadas
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

# Motor de consulta RAG personalizado
# Combina busca vetorial e tradicional para recuperar documentos relevantes
class RAGStringQueryEngine(CustomQueryEngine):
    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: GoogleGenAI
    qa_prompt: PromptTemplate
    
    
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
            retrieved = self.retriever.retrieve("query: " + consulta_vetorial)
            
            # Ordena os resultados por score de similaridade (maior para menor)
            sorted_retrieved = sorted(retrieved, key=lambda x: getattr(x, "score", 0), reverse=True)

            # Log dos resultados para debug (opcional)
            for rank, no in enumerate(sorted_retrieved[:10], start=1):
                score = getattr(no, "score", None)
                slug = no.metadata.get("slug")
        
            nos += retrieved  # Adiciona todos os nós recuperados à lista 

        # Reformata os nós para estrutura padronizada
        nos_reformatados = [{"slug": no.metadata.get("slug"), "content": no.get_content()} for no in nos]
        # Remove duplicatas baseado no slug
        nos_sem_duplicatas = remover_slugs_duplicadas(nos_reformatados)
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
        resultados = fetch_documents_from_elastic_search(consultas_tradicionais, NODES_PER_TRADITIONAL_QUERY)
        
        for resultado in resultados:
            # Extrai o texto do resultado de forma segura
            text = resultado.text if isinstance(resultado.text, str) else resultado.get_content()
            no = {"slug": resultado.doc_id, "content": text}
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
        # Remove duplicatas baseado no slug
        nos = remover_slugs_duplicadas(nos_com_repeticao)
        
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
            content = n["content"]
            slug = n["slug"] 
            # Extrai conteúdo se necessário
            if hasattr(content, 'get_content'):
                content = content.get_content()
            # Adiciona slug como identificador único no início do conteúdo
            content = "Atenção! O seguinte é o slug da página, que, se necessário, deve ser copiado exatamente como está: ***" + slug + "***" + content
            # Limita o tamanho do conteúdo para evitar excesso de tokens
            clipped_content = content[:MAX_CHARS_PER_NODE]
            clipped_nodes.append(clipped_content)
        
        # Junta todos os nós em uma string de contexto
        context_str = "\n\n".join(clipped_nodes)
        # Adiciona histórico da conversa se disponível
        historico_instrucoes = "Atenção às mensagens anteriores do usuário para que você entenda o contexto da conversa. Histórico da conversa:\n" + historico_str if historico_str else ""

        # Formata o prompt final com contexto, consulta e histórico
        final_prompt = self.qa_prompt.format(context_str=context_str, query_str=query_str[:MAX_QUERY_CHARS], historico_str=historico_instrucoes)
        
        response = None
        max_attempts = 10  # Número máximo de tentativas
        sleep_durations = [3, 5, 7, 9, 11, 13, 15, 17, 19]  # Tempos de espera entre tentativas
        
        # Sistema de retry para lidar com falhas temporárias da API
        for attempt in range(max_attempts):
            # Faz a chamada para o modelo LLM
            response = self.llm.complete(prompt=final_prompt)

            # Se recebeu uma resposta válida, sai do loop
            if response and str(response):
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
    
        return str(response)
    
def create_query_engine(index, llm):
    """Cria uma instância do motor de consulta RAG
    
    Args:
        index: Índice vetorial do LlamaIndex
        llm: Modelo de linguagem (GoogleGenAI)
        
    Returns:
        Instância configurada do RAGStringQueryEngine
    """
    # Configura o recuperador com busca por similaridade
    retriever = index.as_retriever(similarity_top_k=NODES_PER_VECTOR_QUERY, with_similarity=True)
    # Configura o sintetizador de respostas em modo compacto
    synthesizer = get_response_synthesizer(response_mode="compact", llm=llm)
    
    return RAGStringQueryEngine(
        retriever=retriever,
        response_synthesizer=synthesizer,
        llm=llm,
        qa_prompt=qa_prompt
    )
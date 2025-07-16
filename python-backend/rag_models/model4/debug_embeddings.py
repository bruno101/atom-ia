from .config import GEMINI_API, NUMBER_OF_VECTOR_QUERIES
from llama_index.llms.google_genai import GoogleGenAI
from .index_management import create_or_load_index
from .query_engine import create_query_engine
from .embeddings import get_embedding_model
from .validation import remover_slugs_duplicadas
from llama_index.core import Settings


print("DEBUG IS RUNNING")
llm = GoogleGenAI(model="gemini-2.5-flash", api_key=GEMINI_API)
Settings.llm = llm
Settings.embed_model = get_embedding_model()

index, _ = create_or_load_index()
query_engine = create_query_engine(index, llm)



def debug_embeddings():
    consulta = "Me encontre documentos sobre alforria"
    #summarized_consulta = llm.complete(f"Extraia as três palavras-chave mais importantes e relevantes para busca vetorial de documentos que ajudem a responder a seguinte consulta, separando por vírgula: CONSULTA ${consulta} PALAVRAS RELEVANTES PARA RESPONDER À CONSULTA, SEPARADAS POR VÍRGULA: " )
    #terms = str(summarized_consulta).split(",")
    #print(str(summarized_consulta))
    #nodes_with_repetition = []
    #print(terms)
    #for term in terms:
        #nodes_with_repetition = nodes_with_repetition + query_engine.retriever.retrieve(term)  
    #nodes = remove_duplicate_slugs(nodes_with_repetition)  
    prompt = f"""
        Extraia as palavras-chave E expressões curtas mais importantes e relevantes para busca vetorial de documentos que ajudem a responder a seguinte consulta.
        Separe cada item por vírgula. Ordene do mais importante para o menos importante, e gere ${NUMBER_OF_VECTOR_QUERIES} expressões.
        Consulta: {consulta}
        Resultado (apenas termos e expressões separadas por vírgula):
    """
    raw_output = llm.complete(prompt)
    query_list = str(raw_output).split(",")[:NUMBER_OF_VECTOR_QUERIES]
    queries = [q.strip() for q in query_list if q.strip()]
    all_nodes = []
    
    
    with open("output.txt", "w", encoding="utf-8") as f:
        for query in queries:
            f.write(f"Searching for: {query}\n")
            print(f"Searching for: {query}")
            retrieved = query_engine.retriever.retrieve(f"query: {query}")
            all_nodes.extend(retrieved)
            for n in retrieved:
                content = n.node.get_content()
                score = getattr(n, 'score', None) 
                f.write(f"Score: {score}\n")
                f.write(f"Content:\n{content}\n")
                f.write("="*40 + "\n") 
            
    nodes = remover_slugs_duplicadas(all_nodes)

    print("Conteúdo e scores salvos em output.txt")

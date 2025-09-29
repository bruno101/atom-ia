# -*- coding: utf-8 -*-
"""
Módulo de interface para busca semântica usando embeddings vetoriais

Este módulo serve como interface de compatibilidade para o algoritmo de busca
vetorial que foi movido para search_algorithms/vector_search.py. Mantém a mesma
API para não quebrar código existente, mas agora utiliza o sistema modular
de algoritmos de busca.
"""
import logging
from dotenv import load_dotenv

# Configuração do sistema de logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Nota: Funções de modelo e vetorização movidas para search_algorithms/vector_search.py
# Este módulo agora serve como interface de compatibilidade

def search_similar_documents(query_text, n_results=5):
    """Busca documentos similares usando busca vetorial semântica
    
    Interface de compatibilidade que utiliza o algoritmo vetorial modular.
    Mantém a mesma assinatura para não quebrar código existente.
    
    Args:
        query_text (str): Consulta em linguagem natural
        n_results (int): Número de resultados a retornar (padrão: 5)
        
    Returns:
        list[dict]: Lista de documentos com campos 'text', 'url' e 'title'
    """
    # Importa algoritmo vetorial do módulo search_algorithms
    from search_algorithms.vector_search import search_documents_by_text
    
    # Converte para formato esperado pelo algoritmo modular
    queries = [query_text] if query_text else []
    
    # Chama algoritmo vetorial modular
    results = search_documents_by_text(queries, n_results_per_query=n_results)
    
    # Remove campo relevance_score para manter compatibilidade
    for doc in results:
        if 'relevance_score' in doc:
            del doc['relevance_score']
    
    return results

def test_vector_search():
    """Função de teste para verificar se a busca vetorial está funcionando
    
    Testa o algoritmo vetorial através da interface de compatibilidade.
    Valida integração com o sistema modular de algoritmos de busca.
    
    Returns:
        bool: True se teste passou, False caso contrário
    """
    logger.info("=== TESTE DA BUSCA VETORIAL SEMÂNTICA ===")
    
    try:
        # Teste com consulta simples sobre tema histórico
        test_query = "como se vestia a elite brasileira no século XIX"
        results = search_similar_documents(test_query, n_results=10)
        
        logger.info(f"Teste executado com sucesso!")
        logger.info(f"Consulta de teste: '{test_query}'")
        logger.info(f"Resultados encontrados: {len(results)}")
        
        # Exibe preview dos resultados encontrados
        for i, doc in enumerate(results, 1):
            logger.info(f"\n--- Resultado {i} ---")
            logger.info(f"URL: {doc['url']}")
            text_preview = doc['text'] if doc['text'] else 'Sem texto'
            logger.info(f"Texto: {text_preview}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Teste da busca vetorial falhou: {e}")
        return False

# Execução principal do módulo
if __name__ == "__main__":
    # Executa teste da busca vetorial quando script é rodado diretamente
    test_vector_search()
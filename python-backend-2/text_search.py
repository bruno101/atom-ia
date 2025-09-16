# -*- coding: utf-8 -*-
"""
Módulo principal de busca textual com algoritmos de busca plugáveis

Este módulo fornece uma interface unificada para diferentes algoritmos de busca,
permitindo fácil comparação e troca entre diferentes estratégias de busca.
"""
import os
import logging
from datetime import datetime
from search_algorithms import elasticsearch_search
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()
URL_ELASTIC_SEARCH = os.getenv("URL_ELASTIC_SEARCH")
print("url encontrada:", URL_ELASTIC_SEARCH)

# Configuração do sistema de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Algoritmo de busca padrão (BM25)
DEFAULT_SEARCH_ALGORITHM = elasticsearch_search
EVALUATE_WITH_GEMINI = False

def search_documents_by_text(queries, n_results_per_query=5):
    """Função principal de busca usando algoritmo BM25 padrão
    
    Args:
        queries (list[str]): Lista de consultas textuais
        n_results_per_query (int): Número de resultados por consulta
        
    Returns:
        list[dict]: Lista de documentos encontrados com scores de relevância
    """
    # Converte consultas para minúsculas para busca case-insensitive
    print("RES PER QUERY: ")
    print(n_results_per_query)
    if isinstance(queries, list):
        queries = [q.lower() if q else q for q in queries]
        print("Consultas:\n")
        print(queries)
    return DEFAULT_SEARCH_ALGORITHM.search_documents_by_text(queries, n_results_per_query, url_elastic_search=URL_ELASTIC_SEARCH)


def evaluate_with_gemini(query, all_results):
    """Avalia resultados dos algoritmos usando Gemini 2.5 Flash
    
    Args:
        query (str): Consulta de teste
        all_results (dict): Resultados de todos os algoritmos
        
    Returns:
        str: Relatório em markdown gerado pelo Gemini
    """
    try:
        # Configura Gemini
        genai.configure(api_key=os.getenv('GEMINI_API'))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Prepara dados para análise
        analysis_data = {
            "query": query,
            "algorithms": {}
        }
        
        for algo_name, results in all_results.items():
            analysis_data["algorithms"][algo_name] = [
                {
                    "rank": i+1,
                    "score": doc['relevance_score'],
                    "url": doc['url'],
                    "text_preview": doc['text'][:5000] + "..."
                }
                for i, doc in enumerate(results[:10])
            ]
        
        # Prompt para Gemini
        prompt = f"""
Analise os resultados de busca de diferentes algoritmos para a consulta: "{query}"

Dados dos algoritmos:
{json.dumps(analysis_data, indent=2, ensure_ascii=False)}

Gere um relatório estruturado em markdown seguindo EXATAMENTE este formato:

## Resumo Executivo
[Breve análise geral]

## Avaliação Detalhada por Resultado

Para CADA resultado dos top 10 de CADA algoritmo, atribua uma nota de relevância:
- **Nota 3**: Altamente relevante para "{query}"
- **Nota 2**: Moderadamente relevante
- **Nota 1**: Pouco relevante
- **Nota 0**: Irrelevante

### [Nome do Algoritmo]
| Posição | Nota Relevância | Nota com Peso Posição | URL | Justificativa |
|----------|------------------|------------------------|-----|---------------|
| 1        | X                | X.X                    | ... | [justificativa] |
| 2        | X                | X.X                    | ... | [justificativa] |
| ...      | ...              | ...                    | ... | ... |
| 10       | X                | X.X                    | ... | [justificativa] |
**Score Final**: X.XX (média das notas com peso)

[Repita para todos os algoritmos]

## Cálculo de Scores
**Fórmula**: Nota com Peso = Nota Relevância × (1 + (11 - posição) × 0.1)
- Posição 1: multiplicador 2.0 (100% bônus)
- Posição 5: multiplicador 1.6 (60% bônus)
- Posição 10: multiplicador 1.1 (10% bônus)

## Ranking Final dos Algoritmos
| Posição | Algoritmo | Score Final | Melhor Resultado |
|----------|-----------|-------------|------------------|
| 1º       | [nome]    | X.XX        | [descrição] |
| 2º       | [nome]    | X.XX        | [descrição] |
| 3º       | [nome]    | X.XX        | [descrição] |

## Análise Estatística
- **Melhor resultado individual**: Nota X na posição Y ([algoritmo])
- **Algoritmo mais consistente**: [nome] (menor variação)
- **Melhor uso de posições altas**: [nome]

## Recomendações
- **Para "{query}"**: Use [algoritmo] (score X.XX)
- **Para consultas similares**: [recomendação]
- **Observações**: [insights sobre posicionamento]

Avalie APENAS a relevância semântica para "{query}", ignorando scores técnicos dos algoritmos.
"""
        
        # Gera relatório
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Erro na avaliação com Gemini: {e}")
        return None

def test_all_algorithms():
    """Testa todos os algoritmos de busca e gera relatório de avaliação com Gemini
    
    Esta função executa uma consulta de teste em todos os algoritmos disponíveis,
    salva os resultados em arquivos separados e gera um relatório comparativo
    usando Gemini 2.5 Flash para avaliar a relevância dos resultados.
    """
    # Importa todos os algoritmos de busca disponíveis
    from search_algorithms import (bm25_search, tfidf_search, simple_like_search, 
                                 bm25p_search, lambdamart_search, 
                                 elasticsearch_search, vector_search)
    
    # Consulta de teste padrão
    test_queries = ['práticas religiosas populares Brasil colonial imperial']
    query = test_queries[0]  # Usa primeira consulta para avaliação
    
    # Dicionário com todos os algoritmos disponíveis
    algorithms = {
        'bm25': bm25_search,           # BM25 clássico
        'bm25p': bm25p_search,         # BM25 com proximidade
        'lambdamart': lambdamart_search, # LambdaMART re-ranking
        'vector': vector_search,       # Busca vetorial semântica
        'elasticsearch': elasticsearch_search, # Elasticsearch
        'tfidf': tfidf_search,         # TF-IDF com similaridade cosseno
        'simple_like': simple_like_search # Busca simples com LIKE
    }
    
    # Timestamp para identificar execução nos logs
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_results = {}
    
    # Testa cada algoritmo individualmente
    for algo_name, algo_module in algorithms.items():
        logger.info(f"Testando algoritmo {algo_name}...")
        
        try:
            # Executa busca com o algoritmo atual (top 10 para avaliação)
            results = algo_module.search_documents_by_text(test_queries, n_results_per_query=10, url_elastic_search=URL_ELASTIC_SEARCH)
            all_results[algo_name] = results
            
            # Salva resultados em arquivo de log específico do algoritmo
            log_filename = f"search_algorithms/{algo_name}_results.txt"
            with open(log_filename, 'a', encoding='utf-8') as f:
                f.write(f"\n=== Execução de Teste: {timestamp} ===\n")
                f.write(f"Consultas: {test_queries}\n")
                f.write(f"Total de resultados: {len(results)}\n\n")
                
                # Escreve cada resultado encontrado
                for i, doc in enumerate(results, 1):
                    f.write(f"--- Resultado {i} ---\n")
                    f.write(f"Score: {doc['relevance_score']:.4f}\n")
                    f.write(f"URL: {doc['url']}\n")
                    f.write(f"Trecho do texto: {doc['text']}...\n\n")
            
            logger.info(f"{algo_name}: {len(results)} resultados salvos em {log_filename}")
            
        except Exception as e:
            logger.error(f"Erro ao testar {algo_name}: {e}")
            all_results[algo_name] = []  # Lista vazia em caso de erro
    
    if EVALUATE_WITH_GEMINI:
        # Cria pasta para relatórios se não existir
        reports_dir = "search_algorithms/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Gera relatório de avaliação com Gemini
        logger.info("Gerando relatório de avaliação com Gemini...")
        gemini_report = evaluate_with_gemini(query, all_results)
        
        if gemini_report:
            # Salva relatório em arquivo markdown na pasta reports
            report_filename = f"{reports_dir}/evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(f"# Relatório de Avaliação de Algoritmos de Busca\n\n")
                f.write(f"**Data:** {timestamp}\n")
                f.write(f"**Consulta:** `{query}`\n\n")
                f.write("---\n\n")
                f.write(gemini_report)
            
            logger.info(f"\u2705 Relatório de avaliação salvo em: {report_filename}")
        else:
            logger.warning("⚠️ Não foi possível gerar relatório com Gemini")

def test_text_search():
    """Testa o algoritmo BM25 padrão
    
    Executa uma busca de teste usando apenas o algoritmo padrão (BM25)
    e exibe os resultados no console para verificação rápida.
    
    Returns:
        list[dict]: Lista de documentos encontrados
    """
    # Consulta de teste
    test_queries = ["questão de limites piauí ceará demarcação serras"]
    logger.info(f"Testando algoritmo padrão com consultas: {test_queries}")

    # Executa busca com algoritmo padrão
    results = search_documents_by_text(test_queries, n_results_per_query=5)
    logger.info(f"Total de resultados encontrados: {len(results)}")

    # Exibe resultados no console
    for i, doc in enumerate(results, 1):
        logger.info(f"\n--- Resultado {i} ---")
        logger.info(f"Score de relevância: {doc['relevance_score']:.2f}")
        logger.info(f"URL: {doc['url']}")
        logger.info(f"Trecho do texto: {doc['text']}...")

    return results


# Execução principal do módulo
if __name__ == "__main__":
    # Testa todos os algoritmos disponíveis e gera relatório de avaliação
    #test_all_algorithms()
    
    # Descomente a linha abaixo para testar apenas o algoritmo padrão
    #test_text_search()
    test_text_search()

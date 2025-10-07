#!/usr/bin/env python3
"""
Script de teste para o processador de URLs
Demonstra como usar o sistema de web scraping + LLM
"""

import json
import sys
import os

# Adiciona o diretório atual ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_scraper import scrape_webpage
from processors.url_processor_backend import process_url_data

def test_url_processing(url):
    """
    Testa o processamento completo de uma URL
    """
    print(f"🔄 Testando processamento da URL: {url}")
    print("="*60)
    
    # Etapa 1: Web Scraping
    print("📡 Executando web scraping...")
    scraped_data = scrape_webpage(url)
    
    if scraped_data.get('status') == 'error':
        print(f"❌ Erro no scraping: {scraped_data.get('error')}")
        return
    
    print("✅ Scraping concluído")
    print(f"📄 Título: {scraped_data.get('title', 'N/A')}")
    print(f"📝 Conteúdo: {len(scraped_data.get('content', ''))} caracteres")
    
    # Etapa 2: Processamento com LLM
    print("\n🤖 Processando com LLM...")
    try:
        structured_query = process_url_data(scraped_data)
        print("✅ Processamento LLM concluído")
        
        # Exibe resultado final
        print("\n📋 JSON ESTRUTURADO GERADO:")
        print("="*60)
        print(json.dumps(structured_query, ensure_ascii=False, indent=2))
        print("="*60)
        
        return structured_query
        
    except Exception as e:
        print(f"❌ Erro no processamento LLM: {e}")
        return None

if __name__ == "__main__":
    # URLs de teste
    test_urls = [
        "https://www.scielo.br/j/rbef/a/example",  # Exemplo de artigo científico
        "https://scholar.google.com/scholar?q=machine+learning",  # Página de busca acadêmica
        "https://arxiv.org/abs/2301.00001"  # Exemplo de paper no arXiv
    ]
    
    # Permite testar URL específica via argumento
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        test_url_processing(test_url)
    else:
        print("💡 Uso: python test_url_processor.py <URL>")
        print("📝 Exemplo: python test_url_processor.py https://example.com")
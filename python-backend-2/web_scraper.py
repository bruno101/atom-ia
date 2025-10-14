import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

def scrape_webpage(url):
    """
    Realiza web scraping de uma URL e extrai o conteúdo textual
    """
    try:
        print(f"🔍 Fazendo scraping da URL: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("🌐 Baixando conteúdo da página...")
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        print("✅ Download concluído")
        
        print("📝 Analisando HTML...")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts e styles
        for script in soup(["script", "style"]):
            script.decompose()
        print("✅ Análise HTML concluída")
        
        # Extrai título
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Extrai meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        # Extrai conteúdo principal
        content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section'])
        content_text = ' '.join([tag.get_text().strip() for tag in content_tags if tag.get_text().strip()])
        
        # Extrai links
        links = []
        for link in soup.find_all('a', href=True):
            href = urljoin(url, link['href'])
            link_text = link.get_text().strip()
            if link_text:
                links.append({'url': href, 'text': link_text})
        
        print(f"✅ Scraping concluído - Extraídos {len(content_text)} caracteres")
        return {
            'url': url,
            'title': title_text,
            'description': description,
            'content': content_text,
            'links': links[:10],  # Limita a 10 links
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'status': 'error'
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        result = scrape_webpage(url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
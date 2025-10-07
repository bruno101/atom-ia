# Processador de URLs - Web Scraping + LLM

## Visão Geral

Este sistema permite processar URLs de páginas web, extrair conteúdo através de web scraping e usar LLM para gerar consultas estruturadas para literatura acadêmica.

## Componentes

### 1. Frontend (JavaScript)
- **Arquivo**: `chatbot-frontend/src/features/fileUpload/fileProcessor.js`
- **Método**: `processURL(url)`
- **Função**: Envia URL para o backend e recebe JSON estruturado

### 2. Web Scraper (Python)
- **Arquivo**: `web_scraper.py`
- **Função**: Extrai conteúdo textual de páginas web usando BeautifulSoup
- **Saída**: JSON com título, conteúdo, links e metadados

### 3. Processador Backend (Python)
- **Arquivo**: `processors/url_processor_backend.py`
- **Função**: Usa LLM (Gemini) para extrair informações acadêmicas
- **Saída**: JSON estruturado para consulta acadêmica

### 4. API Endpoints
- **POST /process-url**: Processa URL e retorna JSON estruturado
- **POST /ask-url-stream**: Executa consulta baseada em URL processada

## Fluxo de Processamento

```
URL → Web Scraping → LLM Processing → Structured JSON → Academic Query
```

### Feedback Visual
- **Frontend**: Barra de progresso com 4 etapas
- **Backend**: Logs detalhados no terminal

## Estrutura do JSON de Saída

```json
{
  "query_id": "AUTO_AUDIT_QUERY-20241220_143022",
  "search_target": "ACADEMIC_LITERATURE",
  "conteúdo": "[CONTEÚDO DA PÁGINA]",
  "url": "[URL DA PÁGINA]",
  "input_busca": "[TERMOS DE BUSCA EXTRAÍDOS]",
  "filters": {
    "main_subject": "[ASSUNTO PRINCIPAL]",
    "author_names": ["autor1", "autor2"],
    "publication_year_min": 2024,
    "keywords_must_contain": ["palavra1", "palavra2"]
  },
  "sort_by": "relevance",
  "max_results": 10,
  "return_fields": ["title", "abstract_snippet", "publication_link"]
}
```

## Como Usar

### Frontend (JavaScript)
```javascript
import { processURL } from './fileProcessor.js';

const url = 'https://example.com/academic-paper';
try {
  const structuredQuery = await processURL(url);
  // Barra de progresso automática:
  // 📊 [████████████████████] 100% - Processamento concluído!
  console.log('Query gerada:', structuredQuery);
} catch (error) {
  console.error('Erro:', error.message);
}
```

### Backend (Python)
```python
# Teste direto
from processors.url_processor_backend import process_url_data
from web_scraper import scrape_webpage

url = "https://example.com"
scraped_data = scrape_webpage(url)
structured_query = process_url_data(scraped_data)
```

### API REST
```bash
# Processar URL
curl -X POST "http://localhost:8000/process-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Dependências

### Python
- `requests`: Para requisições HTTP
- `beautifulsoup4`: Para parsing HTML
- `google.generativeai`: Para processamento LLM
- `python-dotenv`: Para variáveis de ambiente

### Instalação
```bash
pip install requests beautifulsoup4
```

## Logs do Sistema

### Frontend (Console)
```
🔄 Iniciando processamento da URL: https://example.com
📊 [█████░░░░░░░░░░░░░░░] 25% - Enviando URL para processamento...
📊 [██████████░░░░░░░░░░] 50% - Recebendo resposta do servidor...
📊 [███████████████░░░░░] 75% - Processando dados com LLM...
📊 [████████████████████] 100% - Processamento concluído!
✅ URL processada com sucesso
```

### Backend (Terminal)
```
🔍 Fazendo scraping da URL: https://example.com
🌐 Baixando conteúdo da página...
✅ Download concluído
📝 Analisando HTML...
✅ Análise HTML concluída
✅ Scraping concluído - Extraídos 2847 caracteres
🔄 Iniciando processamento dos dados...
🤖 Extraindo informações com LLM...
✅ Extração LLM concluída
📝 Montando JSON estruturado...
✅ JSON estruturado criado com sucesso

================================================================================
🌐 JSON ESTRUTURADO GERADO PARA CONSULTA ACADÊMICA
================================================================================
🔗 URL Processada: https://example.com
🎯 Assunto Principal: Machine Learning
🔍 Termos de Busca: machine learning algorithms
📅 Query ID: AUTO_AUDIT_QUERY-20241220_143022
--------------------------------------------------------------------------------
JSON COMPLETO:
{
  "query_id": "AUTO_AUDIT_QUERY-20241220_143022",
  ...
}
================================================================================
```

## Configuração

1. Configure a API key do Google Gemini no arquivo `.env`:
```
GOOGLE_API_KEY=sua_api_key_aqui
```

2. Certifique-se de que o servidor FastAPI está rodando na porta 8000

## Teste

Execute o script de teste:
```bash
python test_url_processor.py https://example.com
```

## Recursos Visuais

### Barra de Progresso
- 4 etapas de processamento
- Indicador visual com percentual
- Mensagens descritivas de cada fase

### Logs Estruturados
- **Web Scraper**: Progresso do download e análise
- **LLM Processor**: Status da extração de informações
- **API**: Resumo detalhado do JSON gerado

## Limitações

- Funciona melhor com páginas de conteúdo acadêmico
- Requer conexão com internet para scraping e LLM
- Limitado por rate limits das APIs utilizadas
- Alguns sites podem bloquear scraping automatizado

## Tratamento de Erros

O sistema inclui tratamento robusto de erros:
- Timeout de requisições (30s)
- Fallback para dados básicos se LLM falhar
- Logs detalhados para debugging
- Respostas de erro estruturadas
- Feedback visual de erros na barra de progresso
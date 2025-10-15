# 🐍 Python Backend - Sistema RAG SIAN

Backend FastAPI para o chatbot SIAN com sistema RAG (Retrieval-Augmented Generation) e processamento multimodal.

## ✨ Características

- 🤖 **RAG Avançado**: Sistema de recuperação e geração aumentada com múltiplos modelos
- 🔍 **Busca Híbrida**: Combina busca vetorial e lexical (BM25, TF-IDF, Elasticsearch)
- 📄 **Processamento Multimodal**: Suporte para PDF, áudio, vídeo, imagens e URLs
- 🎙️ **Transcrição**: Transcrição de áudio e vídeo com Gemini
- ⚡ **Streaming SSE**: Respostas em tempo real com Server-Sent Events
- 🔄 **Retry Automático**: Sistema robusto de retry para APIs externas
- 📊 **Múltiplos Modelos**: Flash (rápido) e Thinking (preciso)

## 🚀 Tecnologias

### Core
- **FastAPI** - Framework web assíncrono
- **Python 3.10+** - Linguagem principal
- **Uvicorn** - Servidor ASGI de alta performance

### IA e LLM
- **Google Gemini 2.5 Flash** - Modelo de linguagem principal
- **Multilingual Instruct** - Embeddings multilingues

### Busca e Indexação
- **Elasticsearch 8.11** - Motor de busca distribuído
- **Oracle Database** - Banco de dados principal

### Processamento
- **BeautifulSoup4** - Web scraping
- **imageio-ffmpeg** - Processamento de vídeo

## 📦 Instalação

```bash
# Clone o repositório
git clone [url-do-repositorio]

# Entre no diretório
cd python-backend-2

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# Inicie o servidor
python main.py
```

## 🛠️ Estrutura do Projeto

```
python-backend-2/
├── api/                      # Camada de API
│   ├── api_service.py       # Lógica de negócio
│   ├── models.py            # Modelos Pydantic
│   └── routers.py           # Endpoints HTTP
├── processors/              # Processadores de arquivos
│   ├── audio_processor.py   # Processamento de áudio
│   ├── audio_transcriber.py # Transcrição de áudio
│   ├── image_processor.py   # Processamento de imagens
│   ├── pdf_processor.py     # Processamento de PDFs
│   ├── video_processor.py   # Processamento de vídeos
│   ├── video_transcriber.py # Transcrição de vídeos
│   ├── url_processor_backend.py  # Processamento de URLs
│   └── youtube_url_processor.py  # Processamento de YouTube
├── rag_models/              # Modelos RAG
│   ├── flash/              # Modelo rápido
│   │   ├── config.py       # Configurações
│   │   ├── messages.py     # Mensagens de progresso
│   │   ├── pipeline.py     # Pipeline principal
│   │   ├── query_engine.py # Motor de consulta
│   │   ├── query.py        # Handler de consultas
│   │   └── utils.py        # Utilitários
│   ├── thinking/           # Modelo avançado
│   │   ├── config.py       # Configurações
│   │   ├── messages.py     # Mensagens de progresso
│   │   ├── pipeline.py     # Pipeline principal
│   │   ├── query_engine.py # Motor de consulta
│   │   ├── query.py        # Handler de consultas
│   │   └── validation.py   # Validação de respostas
│   └── multimodal/         # Modelo multimodal
│       ├── config.py       # Configurações
│       ├── messages.py     # Mensagens de progresso
│       ├── pipeline.py     # Pipeline principal
│       ├── query_engine.py # Motor de consulta
│       ├── query.py        # Handler de consultas
│       └── utils.py        # Utilitários
├── search_algorithms/       # Algoritmos de busca
│   ├── bm25_search.py      # BM25 tradicional
│   ├── bm25p_search.py     # BM25+ otimizado
│   ├── elasticsearch_search.py  # Busca Elasticsearch
│   ├── lambdamart_search.py     # LambdaMART ranking
│   ├── simple_like_search.py    # Busca SQL LIKE
│   ├── tfidf_search.py     # TF-IDF
│   └── vector_search.py    # Busca vetorial
├── main.py                 # Ponto de entrada
├── config.py               # Configuração global
├── requirements.txt        # Dependências Python
└── README.md              # Este arquivo
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
# API Keys
GEMINI_API=sua_chave_gemini
GOOGLE_API_KEY=sua_chave_google

# Oracle Database
ORACLE_USER=usuario
ORACLE_PASSWORD=senha
ORACLE_DSN=host:porta/servico

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Proxy (opcional)
PROXY=http://proxy:porta
```

## 📡 Endpoints da API

### Chat e Consultas

#### POST /ask-stream-flash
Consulta rápida com streaming (modelo Flash)
```json
{
  "consulta": "Busque documentos sobre...",
  "historico": [
    {"usuario": "pergunta", "bot": "resposta"}
  ]
}
```

#### POST /ask-stream
Consulta avançada com streaming (modelo Thinking)
```json
{
  "consulta": "Busque documentos sobre...",
  "historico": [...]
}
```

#### POST /ask-file-stream
Consulta multimodal com arquivo anexado
```json
{
  "consulta": "Analise este documento",
  "metadata": {
    "assunto_principal": "tema",
    "termos_chave": ["termo1", "termo2"],
    "resumo": "resumo do arquivo"
  },
  "historico": [...]
}
```

### Processamento de Arquivos

#### POST /process-pdf
Processa arquivo PDF
- **Input**: Arquivo PDF (multipart/form-data)
- **Output**: JSON estruturado para busca

#### POST /process-audio
Processa arquivo de áudio
- **Input**: Arquivo de áudio (MP3, M4A, WAV)
- **Output**: JSON estruturado para busca

#### POST /process-video
Processa arquivo de vídeo
- **Input**: Arquivo de vídeo (MP4, AVI, MOV)
- **Output**: JSON estruturado para busca

#### POST /process-image
Processa arquivo de imagem
- **Input**: Arquivo de imagem (JPG, PNG, WEBP)
- **Output**: JSON estruturado para busca

#### POST /process-url
Processa URL de página web
```json
{
  "url": "https://exemplo.com/artigo"
}
```

### Transcrição

#### POST /transcribe-audio
Transcreve áudio com streaming
- **Input**: Arquivo de áudio
- **Output**: Stream SSE com transcrição

#### POST /transcribe-video
Transcreve vídeo com streaming
- **Input**: Arquivo de vídeo
- **Output**: Stream SSE com transcrição

## 🎯 Modelos RAG

### Flash (Rápido)
- **Uso**: Consultas simples e rápidas
- **Latência**: ~2-5 segundos
- **Precisão**: Boa
- **Busca**: Vetorial + BM25

### Thinking (Avançado)
- **Uso**: Consultas complexas e precisas
- **Latência**: ~5-15 segundos
- **Precisão**: Excelente
- **Busca**: Vetorial + BM25 + Validação JSON

### Multimodal
- **Uso**: Consultas com arquivos anexados
- **Latência**: Variável (depende do arquivo)
- **Precisão**: Excelente
- **Busca**: Vetorial + BM25 + Análise de conteúdo

## 🔍 Sistema de Busca

### Busca Vetorial
- **Modelo**: Multilingual Instruct
- **Dimensões**: 768
- **Similaridade**: Cosseno
- **Top-K**: Configurável

### Busca Lexical
- **BM25**: Ranking probabilístico
- **BM25+**: Versão otimizada
- **TF-IDF**: Frequência de termos
- **Elasticsearch**: Motor distribuído

### Busca Híbrida
Combina resultados de busca vetorial e lexical com pesos configuráveis para melhor precisão.

## 📊 Processamento Multimodal

### PDF
1. Extração de texto com PyPDF2
2. Análise de conteúdo com Gemini
3. Geração de termos-chave e resumo
4. Criação de query estruturada

### Áudio
1. Upload para Gemini File API
2. Análise direta com Gemini 2.0 Flash Lite
3. Extração de assunto, termos e resumo
4. Geração de query estruturada

### Vídeo
1. Upload para Gemini File API
2. Análise de áudio e vídeo com Gemini
3. Extração de informações multimodais
4. Geração de query estruturada

### Imagem
1. Upload para Gemini File API
2. Análise visual com Gemini Vision
3. Extração de contexto e elementos
4. Geração de query estruturada

### URL
1. Web scraping com BeautifulSoup
2. Extração de conteúdo principal
3. Análise com Gemini
4. Geração de query acadêmica

## ⚡ Streaming SSE

O sistema utiliza Server-Sent Events para streaming em tempo real:

### Eventos
- **progress**: Mensagens de progresso
- **partial**: Resposta parcial do LLM
- **done**: Resultado final
- **error**: Mensagens de erro
- **chunk**: Chunks de transcrição

### Exemplo de Resposta
```
event: progress
data: Buscando documentos relevantes...

event: progress
data: Encontrados 15 documentos

event: partial
data: Com base nos documentos...

event: done
data: {"resposta": "...", "links": [...]}
```

## 🔄 Sistema de Retry

Implementa retry automático com backoff exponencial:
- **Tentativas**: 10 máximo
- **Intervalos**: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19 segundos
- **Timeout**: 300 segundos por chamada
- **Fallback**: Mensagem de erro amigável

## 🐳 Docker

```bash
# Build da imagem
docker build -t sian-backend .

# Executar container
docker run -p 8000:8000 --env-file .env sian-backend

# Docker Compose
docker-compose up -d
```

## 📝 Logs

O sistema gera logs detalhados para debug:
- Requisições HTTP
- Processamento de arquivos
- Chamadas LLM
- Erros e exceções
- Performance

## 🧪 Testes

```bash
# Executar testes
python -m pytest

# Teste de endpoint específico
python test.py

# Teste de processador de URL
python test_url_processor.py
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

## 🏛️ Sobre

Desenvolvido para o **Arquivo Nacional** como parte do sistema SIAN, fornecendo backend robusto para consultas arquivísticas inteligentes com IA.

---

**SIAN Backend** • *Sistema Inteligente de Arquivos Nacionais* • Dataprev © 2025

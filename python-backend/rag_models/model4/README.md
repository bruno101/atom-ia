# Motor de Consulta RAG - Model4

## Visão Geral

Este módulo implementa um motor de consulta RAG (Retrieval-Augmented Generation) personalizado que combina busca vetorial e tradicional para recuperar documentos relevantes e gerar respostas contextualizadas.

## Arquitetura

### Componentes Principais

- **RAGStringQueryEngine**: Classe principal que herda de `CustomQueryEngine`
- **Busca Híbrida**: Combina consultas vetoriais (embeddings) e tradicionais (Elasticsearch)
- **Sistema de Retry**: Implementa tentativas automáticas para chamadas da API
- **Remoção de Duplicatas**: Evita documentos repetidos baseado no slug

## Funcionalidades

### 1. Consulta Vetorial (`custom_vector_query`)
- Utiliza embeddings semânticos para busca por similaridade
- Ordena resultados por score de relevância
- Limita resultados pelo parâmetro `MAX_NODES_VECTOR_QUERY`

### 2. Consulta Tradicional (`custom_traditional_query`)
- Integra com Elasticsearch para busca textual
- Processa consultas baseadas em palavras-chave
- Limita resultados pelo parâmetro `MAX_NODES_TRADITIONAL_QUERY`

### 3. Consulta Global (`custom_global_query`)
- Combina ambos os tipos de busca
- Distribui palavras-chave entre consultas vetoriais e tradicionais
- Remove duplicatas dos resultados combinados

### 4. Geração de Resposta (`custom_query`)
- Processa documentos recuperados
- Adiciona contexto histórico da conversa
- Implementa sistema de retry para robustez
- Gera resposta em formato JSON estruturado

## Configuração

### Parâmetros Principais (definidos em `config.py`)

```python
NODES_PER_VECTOR_QUERY = 10        # Nós por consulta vetorial
NODES_PER_TRADITIONAL_QUERY = 5    # Nós por consulta tradicional
MAX_CHARS_PER_NODE = 2000         # Caracteres máximos por nó
MAX_QUERY_CHARS = 500             # Caracteres máximos da consulta
NUMBER_OF_TRADITIONAL_QUERIES = 3  # Número de consultas tradicionais
NUMBER_OF_VECTOR_QUERIES = 2      # Número de consultas vetoriais
MAX_NODES_VECTOR_QUERY = 15       # Máximo de nós vetoriais
MAX_NODES_TRADITIONAL_QUERY = 10  # Máximo de nós tradicionais
```

## Formato de Resposta

O sistema gera respostas em formato JSON estruturado:

```json
{
  "data": {
    "paginas": [
      {
        "slug": "identificador-da-pagina",
        "title": "Título da Página",
        "descricao": "Descrição resumida do conteúdo",
        "justificativa": "Motivo da recomendação"
      }
    ]
  }
}
```

## Template de Prompt

O sistema utiliza um template específico que:
- Instrui o modelo a responder em português
- Força formato JSON na resposta
- Preserva slugs exatamente como estão na base
- Inclui contexto histórico da conversa
- Recomenda múltiplos documentos relevantes

## Sistema de Retry

Implementa robustez através de:
- **3 tentativas máximas** para chamadas da API
- **Tempos de espera progressivos**: 10s, 30s
- **Logs detalhados** para debugging
- **Fallback gracioso** em caso de falhas

## Uso

### Criação do Motor de Consulta

```python
from query_engine import create_query_engine

# Criar instância
engine = create_query_engine(index, llm)

# Executar consulta
response = engine.custom_query(
    query_str="sua consulta",
    historico_str="histórico da conversa",
    nodes=documentos_recuperados
)
```

### Fluxo de Execução

1. **Extração de palavras-chave** da consulta do usuário
2. **Busca híbrida** (vetorial + tradicional)
3. **Remoção de duplicatas** baseada em slugs
4. **Formatação do contexto** com limitação de caracteres
5. **Geração da resposta** via LLM com retry
6. **Retorno em formato JSON** estruturado

## Dependências

- `llama_index`: Framework principal para RAG
- `google_genai`: Modelo de linguagem Google
- `elasticsearch`: Busca tradicional
- `numpy`: Operações numéricas
- `time`: Sistema de retry

## Logs e Debugging

O sistema inclui logs detalhados para:
- Tentativas de API e respostas
- Scores de similaridade
- Slugs dos documentos recuperados
- Status das tentativas de retry

## Considerações de Performance

- **Limitação de caracteres** por nó para otimizar tokens
- **Busca paralela** entre vetorial e tradicional
- **Cache implícito** através da remoção de duplicatas
- **Timeout configurável** para chamadas da API
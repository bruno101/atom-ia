# Módulo para busca e processamento de documentos
# Converte dados do banco e Elasticsearch em documentos do LlamaIndex
from db_connection import fetch_content
from elastic_search import fetch_from_elastic_search
from llama_index.core import Document
import json

def fetch_documents_from_db():
    """Busca documentos do banco de dados e converte para formato LlamaIndex
    
    Returns:
        list[Document]: Lista de documentos formatados para indexação
    """
    rows = fetch_content()  # Busca dados do banco MySQL
    documents = []

    for row in rows:
        slug = ""
        parts = []  # Lista para construir o conteúdo do documento
        
        # Processa cada campo do registro
        for key, value in row.items():
            val_str = value if value is not None else ''
            if key == 'slug':
                slug = val_str  # Armazena o slug para usar como ID
            if key == 'subjects':
                subjects = val_str  # Armazena assuntos para referência
            # Adiciona cada campo ao conteúdo do documento
            parts.append(f"{key}: {val_str}.")
                
        if not slug:
            print("No slug!")  # Aviso se documento não tem slug
            
        # Monta o conteúdo final com prefixo "passage:"
        content = "passage: " + "\n".join(parts)
        
        # Cria documento do LlamaIndex com slug como ID e metadata
        doc = Document(text=content, doc_id=slug, metadata={"slug": slug})
        documents.append(doc)
    
    return documents

def handle_slug(key, value, parts):
    """Processa campo slug adicionando-o ao conteúdo"""
    parts.append(f"{key}: {value}.")

def handle_subjects(key, value, parts):
    """Processa assuntos extraindo nomes em português"""
    subjects = "".join(subject['i18n']['pt']['name'] or "" for subject in value)
    parts.append(f"{key}: {subjects}.")

def handle_dates(key, dates, parts):
    """Processa datas formatando intervalo de data"""
    try:
        # Verifica se há datas válidas na estrutura esperada
        if (
            isinstance(dates, list) and len(dates) > 0 and
            isinstance(dates[0], dict) and
            'startDate' in dates[0] and 'endDate' in dates[0] and
            dates[0]['startDate'] and dates[0]['endDate']
        ):
            date = dates[0]
            parts.append(f"{key}: {date['startDate']} - {date['endDate']}.")
    except Exception as e:
        pass  # Ignora erros de processamento de data

def handle_i18n(value, parts):
    """Processa campos internacionalizados extraindo versão em português"""
    i18n = value['pt']  # Extrai dados em português
    for i18n_key, i18n_value in i18n.items():
        parts.append(f"{i18n_key}: {i18n_value}")
        
def contains_any_word(value_str, expression):
    """Verifica se alguma palavra da expressão está presente no valor"""
    value_str = value_str.lower()
    # Divide a expressão em palavras, tratando vírgulas como espaços
    words = [word.strip().lower() for word in expression.replace(',', ' ').split()]
    return any(word in value_str for word in words)
        
def handle_generic_attribute(key, value, parts, expression):
    """Processa atributos genéricos verificando relevância com a expressão"""
    value_str = json.dumps(value)  # Converte valor para string JSON
    # Adiciona apenas se o valor contém palavras relevantes da expressão
    if (value_str != "" and contains_any_word(value_str, expression)):
        parts.append(f"{key}: {value_str}")
        
def process_key_value(key, value, parts, expression):
    """Processa pares chave-valor baseado no tipo de campo
    
    Args:
        key (str): Nome do campo
        value: Valor do campo
        parts (list): Lista para adicionar conteúdo processado
        expression (str): Expressão de busca para filtrar relevância
    """
    match key:
        case 'slug':
            return handle_slug(key, value, parts) or parts
        case 'subjects':
            return handle_subjects(key, value, parts) or parts
        case 'dates':
            return handle_dates(key, value, parts) or parts
        case 'i18n':
            return handle_i18n(value, parts) or parts
        case _:
            # Caso padrão para campos genéricos
            return handle_generic_attribute(key, value, parts, expression) or parts

def fetch_documents_from_elastic_search(queries: list[str], number_results: int):
    """Busca documentos do Elasticsearch e converte para formato LlamaIndex
    
    Args:
        queries (list[str]): Lista de consultas para buscar
        number_results (int): Número máximo de resultados
        
    Returns:
        list[Document]: Lista de documentos formatados
    """
    # Busca dados do Elasticsearch
    rows = fetch_from_elastic_search(queries, number_results)
    documents = []
    
    for row in rows:
        slug = ""
        parts = []  # Lista para construir conteúdo
        # Extrai o campo _source do resultado do Elasticsearch
        source = row.get('_source') if isinstance(row, dict) else None
        
        if not isinstance(source, dict):
            continue  # Pula registros inválidos
        
        # Processa cada campo do documento
        for key, value in source.items():
            # Usa todas as queries como contexto para filtrar relevância
            process_key_value(key, value, parts, " ".join(queries))
            if key == "slug":
                slug = value  # Armazena slug para usar como ID
            
        if not slug:
            print("No slug!")  # Aviso se documento não tem slug
    
        # Monta conteúdo final com prefixo "passage:"
        content = "passage: " + "\n".join(parts)        
        doc = Document(text=content, doc_id=slug, metadata={"slug": slug})
        documents.append(doc)
    
    return documents

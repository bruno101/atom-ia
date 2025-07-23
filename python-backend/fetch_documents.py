from db_connection import fetch_content
from elastic_search import fetch_from_elastic_search
from llama_index.core import Document
import json

def fetch_documents_from_db():
    rows =  fetch_content()
    documents = []

    for row in rows:

        slug = ""
        parts = []
        for key, value in row.items():
            val_str = value if value is not None else ''
            if key == 'slug':
                slug = val_str
            if key == 'subjects':
                subjects = val_str
            parts.append(f"{key}: {val_str}.")
                
        if not slug:
            print("No slug!")
        content = "passage: " + "\n".join(parts)
        
        doc = Document(text=content, doc_id=slug, metadata={"slug": slug})
        documents.append(doc)
    
    print("fetched documents")

    return documents

def handle_slug(key, value, parts):
    parts.append(f"{key}: {value}.")

def handle_subjects(key, value, parts):
    subjects = "".join(subject['i18n']['pt']['name'] or "" for subject in value)
    parts.append(f"{key}: {subjects}.")

def handle_dates(key, dates, parts):
    try:
        if (
            isinstance(dates, list) and len(dates) > 0 and
            isinstance(dates[0], dict) and
            'startDate' in dates[0] and 'endDate' in dates[0] and
            dates[0]['startDate'] and dates[0]['endDate']
        ):
            date = dates[0]
            parts.append(f"{key}: {date['startDate']} - {date['endDate']}.")
    except Exception as e:
        pass  

def handle_i18n(value, parts):
    i18n = value['pt']
    for i18n_key, i18n_value in i18n.items():
        parts.append(f"{i18n_key}: {i18n_value}")
        
def contains_any_word(value_str, expression):
    value_str = value_str.lower()
    words = [word.strip().lower() for word in expression.replace(',', ' ').split()]
    return any(word in value_str for word in words)
        
def handle_generic_attribute(key, value, parts, expression):
    value_str = json.dumps(value)
    print("handling generic: \n\n", value, "\n\n", expression, "\n\n", contains_any_word(value_str, expression), "\n\n")
    if (value_str != "" and contains_any_word(value_str, expression)):
        parts.append(f"{key}: {value_str}")
        
def process_key_value(key, value, parts, expression):
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
            return handle_generic_attribute(key, value, parts, expression) or parts

def fetch_documents_from_elastic_search(queries: list[str], number_results: int):
    
    rows = fetch_from_elastic_search(queries, number_results)
    documents = []
    
    for row in rows:
        
        print("row is", row)

        slug = ""
        parts = []
        source = row.get('_source') if isinstance(row, dict) else None
        
        if not isinstance(source, dict):
            continue
        
        print("source is", source)

        for key, value in source.items():
            
            print("key is", key)
            print("value is", value)
            
            process_key_value(key, value, parts, " ".join(queries))
            if key == "slug":
                slug = value
            
        if not slug:
            
            print("No slug!")
        
        print("finished generating parts for this row")
        print("the parts are\n\n", parts, "\n\n")
            
        content = "passage: " + "\n".join(parts)
        
        print("finished generating content for this row")
        
        doc = Document(text=content, doc_id=slug, metadata={"slug": slug})
        
        print("finished generating doc for this row")

        documents.append(doc)
    

    return documents

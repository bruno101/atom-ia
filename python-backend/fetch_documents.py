from db_connection import fetch_content, traditional_query
from llama_index.core import Document

def fetch_documents_from_db():
    rows =  fetch_content()
    documents = []

    for row in rows:

        slug = ""
        subjects = ""
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
        
        doc = Document(text=content, doc_id=slug, metadata={"slug": slug, "subjects": subjects})
        documents.append(doc)
    
    print("fetched documents")

    return documents

def search_db(queries: list[str], number_results: int):
    
    rows = traditional_query(queries, number_results)
    print("trad_query: ", rows)
    documents = []
    
    for row in rows:

        slug = ""
        subjects = ""
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
        
        doc = Document(text=content, doc_id=slug, metadata={"slug": slug, "subjects": subjects})
        documents.append(doc)
    
    print("fetched documents")

    return documents

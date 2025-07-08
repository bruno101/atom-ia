from db_connection import fetch_content

def fetch_documents_from_db():
    rows = fetch_content()
    documents = []

    for row in rows:


        slug = ""
        parts = []
        for key, value in row.items():
            val_str = value if value is not None else ''
            parts.append(f"{key}: {val_str}")
            if key == 'slug':
                slug = val_str
                
        if not slug:
            print("No slug!")
        content = "\n".join(parts)
        
        #print(parts)
        doc = Document(text=content, doc_id=slug, metadata={"slug": slug})
        documents.append(doc)

    return documents
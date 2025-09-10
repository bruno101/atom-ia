def remover_urls_duplicadas(nodes):
    """Remove nós duplicados baseado na url
    
    Args:
        nodes (list): Lista de nós com urls
        
    Returns:
        list: Lista de nós únicos (sem duplicatas)
    """
    seen_urls = set()  # Conjunto para rastrear urls já vistos
    unique_nodes = []   # Lista de nós únicos

    for node in nodes:
        url = node["url"]
        # Adiciona apenas se a url existe e não foi visto antes
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_nodes.append(node)

    return unique_nodes

def extrair_links(resposta, nos):
    """Extrai os links válidos da resposta

    Args:
        resposta (str): Resposta do modelo
        links_validos (list): Lista de links válidos

    Returns:
        list: Lista de links válidos encontrados na resposta
    """
    resultados = []
    for no in nos:
        link = no["url"]
        if link in resposta:
            resultados.append({
                "url": link,
                "title": no["title"],
                })
    print("Links filtrados: ")
    print(resultados)
    return resultados
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

def extrair_links_corrigidos(resposta, nos):
    """Extrai e corrige links da resposta usando fuzzy matching
    
    Args:
        resposta (str): Resposta do modelo
        nos (list): Lista de nós com urls válidas
        
    Returns:
        tuple: (resposta_corrigida, lista_de_links)
    """
    import re
    from difflib import get_close_matches
    
    urls_resposta = re.findall(r'https?://[^\s\[\]\(\)]+', resposta)
    resultados = []
    resposta_corrigida = resposta
    urls_nos = [no["url"] for no in nos]
    urls_processadas = set()
    
    print("resposta foi: ")
    print(resposta)
    
    for i, url_match in enumerate(urls_resposta):
        url = url_match
        
        if url in urls_processadas:
            continue
        urls_processadas.add(url)
        
        no_encontrado = next((no for no in nos if no["url"] == url), None)
        
        if no_encontrado:
            if not any(r["url"] == no_encontrado["url"] for r in resultados):
                resultados.append({"url": no_encontrado["url"], "title": no_encontrado["title"]})
        else:
            url_pos = resposta.find(url_match)
            prev_url_pos = resposta.rfind('http', 0, url_pos) if i > 0 else 0
            contexto = resposta[prev_url_pos:url_pos]
            
            no_por_titulo = next((no for no in nos if no["title"] in contexto), None)
            
            if no_por_titulo:
                if not any(r["url"] == no_por_titulo["url"] for r in resultados):
                    print(f"Correção por título: {url} -> {no_por_titulo['url']} (título: {no_por_titulo['title']})")
                    resultados.append({"url": no_por_titulo["url"], "title": no_por_titulo["title"]})
                resposta_corrigida = resposta_corrigida.replace(url_match, no_por_titulo["url"])
            else:
                matches = get_close_matches(url, urls_nos, n=1, cutoff=0.6)
                if matches:
                    no_similar = next(no for no in nos if no["url"] == matches[0])
                    if not any(r["url"] == no_similar["url"] for r in resultados):
                        print(f"Correção por fuzzy matching: {url} -> {no_similar['url']}")
                        resultados.append({"url": no_similar["url"], "title": no_similar["title"]})
                    resposta_corrigida = resposta_corrigida.replace(url_match, no_similar["url"])
    
    return resposta_corrigida, resultados
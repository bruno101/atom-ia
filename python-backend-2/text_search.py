# -*- coding: utf-8 -*-
"""
Módulo para busca textual/lexical usando Oracle Text Search
Permite buscar documentos usando consultas textuais com recursos de fuzzy matching e relevância
"""
import os
import logging
import oracledb
from dotenv import load_dotenv

# Configurar logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD") 
DB_DSN = os.getenv("DB_DSN")

def create_text_index_if_needed():
    """Cria índices de texto Oracle se não existirem para melhorar performance de busca"""
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            with connection.cursor() as cursor:
                # Verificar se índice de texto já existe
                cursor.execute("""
                    SELECT COUNT(*) FROM user_indexes 
                    WHERE index_name = 'DOCUMENTS_TEXT_IDX'
                """)
                
                if cursor.fetchone()[0] == 0:
                    logger.info("Criando índice de texto Oracle...")
                    cursor.execute("""
                        CREATE INDEX documents_text_idx ON documents(text) 
                        INDEXTYPE IS CTXSYS.CONTEXT
                    """)
                    connection.commit()
                    logger.info("Índice de texto criado com sucesso")
                else:
                    logger.info("Índice de texto já existe")
                
                # Verificar se índice de título já existe
                cursor.execute("""
                    SELECT COUNT(*) FROM user_indexes 
                    WHERE index_name = 'DOCUMENTS_TITLE_IDX'
                """)
                
                if cursor.fetchone()[0] == 0:
                    logger.info("Criando índice de título Oracle...")
                    cursor.execute("""
                        CREATE INDEX documents_title_idx ON documents(title) 
                        INDEXTYPE IS CTXSYS.CONTEXT
                    """)
                    connection.commit()
                    logger.info("Índice de título criado com sucesso")
                else:
                    logger.info("Índice de título já existe")
                    
    except oracledb.Error as e:
        logger.warning(f"Não foi possível criar índices de texto: {e}")
        # Continua sem índice - busca ainda funcionará, mas mais lenta

def sync_text_index():
    """Reconstrói o índice Oracle Text para garantir sincronização após deleções"""
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            with connection.cursor() as cursor:
                logger.info("Reconstruindo índice Oracle Text...")
                cursor.execute("ALTER INDEX DOCUMENTS_TEXT_IDX REBUILD")
                connection.commit()
                logger.info("Índice reconstruído com sucesso")
    except oracledb.Error as e:
        logger.warning(f"Erro ao reconstruir índice: {e}")

def search_documents_by_text(queries, n_results_per_query=5):
    """Busca documentos usando consulta textual/lexical com fuzzy matching
    
    Args:
        queries (list[str]): Lista de consultas textuais
        n_results_per_query (int): Número de resultados por consulta (padrão: 5)
        
    Returns:
        list[dict]: Lista de documentos com campos 'text', 'url' e 'query_matched'
    """
    logger.info(f"Iniciando busca textual para {len(queries)} consultas")
    
    # Validar parâmetros
    if not queries or not isinstance(queries, list):
        logger.warning("Lista de consultas vazia ou inválida")
        return []
    
    if n_results_per_query <= 0:
        logger.warning("Número de resultados deve ser positivo")
        return []
    
    # Tentar criar índice se necessário
    create_text_index_if_needed()
    
    all_documents = []
    
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            logger.info("Conexão com Oracle estabelecida")
            
            with connection.cursor() as cursor:
                for query_idx, query in enumerate(queries):
                    if not query or not query.strip():
                        logger.warning(f"Consulta {query_idx + 1} está vazia, pulando...")
                        continue
                    
                    logger.info(f"Processando consulta {query_idx + 1}/{len(queries)}: '{query}'")
                    
                    # Preparar termos de busca - limpar e dividir em palavras
                    search_terms = [term.strip() for term in query.split() if term.strip()]
                    
                    if not search_terms:
                        logger.warning(f"Nenhum termo válido na consulta: '{query}'")
                        continue
                    
                    # Tentar busca com índice Oracle Text primeiro
                    results = _search_with_oracle_text(cursor, search_terms, n_results_per_query)
                    
                    
                    # Processar resultados
                    for text, url, title, score in results:
                        # Handle CLOB objects
                        text_content = text.read() if hasattr(text, 'read') else str(text)
                        
                        all_documents.append({
                            'text': text_content,
                            'url': url,
                            'title': title,
                            'query_matched': query,
                            'relevance_score': score
                        })
                        print("url: ", url)
                    
                    logger.info(f"Encontrados {len(results)} resultados para consulta: '{query}'")
        
        logger.info(f"Busca textual concluída. Total de {len(all_documents)} documentos encontrados")
        return all_documents
        
    except oracledb.Error as e:
        logger.error(f"Erro de banco de dados Oracle: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na busca textual: {e}")
        raise

def _search_with_oracle_text(cursor, search_terms, n_results):
    """Busca usando Oracle Text Search com sintaxe simplificada"""
    try:
        # Usar sintaxe mais simples do Oracle Text
        oracle_query_parts = []
        
        for term in search_terms:
            # Sintaxe mais simples - apenas wildcards
            oracle_query_parts.extend([
                term,  # Termo exato
                f"{term}%",  # Prefixo
            ])
        
        # Combinar termos com OR
        oracle_text_query = " OR ".join(oracle_query_parts)
        
        sql = """
        SELECT text, url, title, (SCORE(1) + SCORE(2)) as relevance
        FROM documents 
        WHERE CONTAINS(text, :1, 1) > 0 OR CONTAINS(title, :2, 2) > 0
        ORDER BY (SCORE(1) + SCORE(2)) DESC
        FETCH FIRST :3 ROWS ONLY
        """
        
        logger.debug(f"Oracle Text query: {oracle_text_query}")
        cursor.execute(sql, (oracle_text_query, oracle_text_query, n_results))
        
        return cursor.fetchall()
        
    except oracledb.Error as e:
        logger.warning(f"Oracle Text search falhou: {e}")
        return []

def _search_with_like_fuzzy(cursor, search_terms, n_results):
    """Busca usando LIKE com fuzzy matching robusto"""
    try:
        # Usar REGEXP_LIKE para busca mais robusta
        like_conditions = []
        score_conditions = []
        params = []
        
        for i, term in enumerate(search_terms):
            # Gerar padrões de busca mais robustos
            patterns = [
                f".*{term.lower()}.*",  # Substring básica
                f".*{term.lower()}s.*",  # Plural
                f".*{term.lower()[:-1]}.*" if term.lower().endswith('s') and len(term) > 2 else f".*{term.lower()}.*"
            ]
            
            # Remover duplicatas
            patterns = list(set(patterns))
            
            term_conditions = []
            for j, pattern in enumerate(patterns):
                param_name = f"term_{i}_{j}"
                # Usar REGEXP_LIKE para busca case-insensitive
                term_conditions.append(f"REGEXP_LIKE(text, :{param_name}, 'i')")
                score_conditions.append(f"CASE WHEN REGEXP_LIKE(text, :{param_name}, 'i') THEN 1 ELSE 0 END")
                params.append((param_name, pattern))
            
            like_conditions.append(f"({' OR '.join(term_conditions)})")
        
        where_clause = " OR ".join(like_conditions)
        score_calculation = " + ".join(score_conditions)
        
        # Construir SQL com parâmetros nomeados
        sql = f"""
        SELECT text, url, ({score_calculation}) as relevance
        FROM documents 
        WHERE {where_clause}
        ORDER BY ({score_calculation}) DESC, LENGTH(text) ASC
        FETCH FIRST {n_results} ROWS ONLY
        """
        
        # Criar dicionário de parâmetros
        param_dict = {name: value for name, value in params}
        
        logger.debug(f"REGEXP query com {len(params)} parâmetros")
        cursor.execute(sql, param_dict)
        
        return cursor.fetchall()
        
    except oracledb.Error as e:
        logger.error(f"REGEXP search falhou: {e}")
        # Fallback para LIKE simples
        return _search_with_simple_like(cursor, search_terms, n_results)

def _search_with_simple_like(cursor, search_terms, n_results):
    """Fallback com LIKE muito simples"""
    try:
        conditions = []
        params = {}
        
        for i, term in enumerate(search_terms):
            param_name = f"term_{i}"
            conditions.append(f"UPPER(text) LIKE UPPER(:{param_name})")
            params[param_name] = f"%{term}%"
        
        where_clause = " OR ".join(conditions)
        
        sql = f"""
        SELECT text, url, 1 as relevance
        FROM documents 
        WHERE {where_clause}
        FETCH FIRST {n_results} ROWS ONLY
        """
        
        logger.debug(f"Simple LIKE fallback com {len(params)} parâmetros")
        cursor.execute(sql, params)
        
        return cursor.fetchall()
        
    except oracledb.Error as e:
        logger.error(f"Simple LIKE search falhou: {e}")
        return []



def test_text_search():
    """Função de teste para verificar se a busca textual está funcionando"""
    logger.info("=== TESTE DA BUSCA TEXTUAL ===")

    try:
        # Teste com múltiplas consultas
        test_queries = [
            "Tocantins"
        ]
        
        results = search_documents_by_text(test_queries, n_results_per_query=10)
        
        logger.info(f"Teste executado com sucesso!")
        logger.info(f"Consultas: {test_queries}")
        logger.info(f"Total de resultados encontrados: {len(results)}")
        
        for i, doc in enumerate(results, 1):
            logger.info(f"\n--- Resultado {i} ---")
            logger.info(f"Consulta que gerou o match: '{doc['query_matched']}'")
            logger.info(f"Score de relevância: {doc['relevance_score']}")
            logger.info(f"URL: {doc['url']}")
            text_preview = doc['text'][:100] if doc['text'] else 'Sem texto'
            logger.info(f"Texto (primeiros 100 chars): {text_preview}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Teste falhou: {e}")
        return False

if __name__ == "__main__":
    # Executar teste quando script é rodado diretamente
    test_text_search()
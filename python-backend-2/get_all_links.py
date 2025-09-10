# -*- coding: utf-8 -*-
"""
Módulo para recuperar todos os links válidos do banco de dados Oracle
"""
import os
import logging
import oracledb
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD") 
DB_DSN = os.getenv("DB_DSN")

def get_all_valid_links():
    """Retorna todos os links válidos (não nulos e não vazios) do banco de dados
    
    Returns:
        list[str]: Lista de URLs válidas dos documentos
    """
    
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            with connection.cursor() as cursor:
                # Buscar URLs não nulas e não vazias
                sql = """
                SELECT DISTINCT url FROM documents
                """
                
                cursor.execute(sql)
                results = cursor.fetchall()
                                
                # Extrair URLs da tupla
                urls = [row[0] for row in results]
                
                return urls
                
    except oracledb.Error as e:
        logger.error(f"Erro de banco de dados Oracle: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise

def test_get_links():
    """Função de teste para verificar a recuperação de links"""
    logger.info("=== TESTE DE RECUPERAÇÃO DE LINKS ===")
    
    try:
        links = get_all_valid_links()
        
        logger.info(f"Total de links encontrados: {len(links)}")
        
        # Mostrar primeiros 10 links como exemplo
        for i, link in enumerate(links[:10], 1):
            logger.info(f"{i}. {link}")
        
        if len(links) > 10:
            logger.info(f"... e mais {len(links) - 10} links")
        
        return True
        
    except Exception as e:
        logger.error(f"Teste falhou: {e}")
        return False

if __name__ == "__main__":
    # Executar teste quando script é rodado diretamente
    test_get_links()
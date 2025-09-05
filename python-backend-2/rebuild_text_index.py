"""
Script para reconstruir o índice Oracle Text após mudanças no banco de dados
Execute este script sempre que deletar ou modificar documentos na tabela
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

def rebuild_text_index():
    """Reconstrói os índices Oracle Text para sincronizar com mudanças no banco"""
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            with connection.cursor() as cursor:
                logger.info("Reconstruindo índices Oracle Text...")
                
                # Rebuild text index
                try:
                    cursor.execute("ALTER INDEX DOCUMENTS_TEXT_IDX REBUILD")
                    logger.info("Índice de texto reconstruído")
                except oracledb.Error:
                    logger.warning("Índice de texto não encontrado")
                
                # Rebuild title index
                try:
                    cursor.execute("ALTER INDEX DOCUMENTS_TITLE_IDX REBUILD")
                    logger.info("Índice de título reconstruído")
                except oracledb.Error:
                    logger.warning("Índice de título não encontrado")
                
                connection.commit()
                logger.info("Índices reconstruídos com sucesso!")
                
    except oracledb.Error as e:
        logger.error(f"Erro ao reconstruir índices: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== RECONSTRUÇÃO DO ÍNDICE ORACLE TEXT ===")
    success = rebuild_text_index()
    if success:
        print("Índice reconstruído com sucesso! As buscas agora refletirão as mudanças no banco.")
    else:
        print("Falha ao reconstruir o índice. Verifique os logs para mais detalhes.")
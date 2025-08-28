# Utilitários para configuração de logging do sistema
# Fornece configuração padronizada para logs em todo o projeto
import logging

def setup_logging():
    """Configura o sistema de logging com formato padronizado
    
    Returns:
        logging.Logger: Logger configurado para o módulo atual
    """
    # Configura o nível e formato dos logs
    logging.basicConfig(
        level=logging.INFO,  # Nível mínimo de log (INFO, WARNING, ERROR)
        format='%(asctime)s - %(levelname)s - %(message)s'  # Formato: timestamp - nível - mensagem
    )
    return logging.getLogger(__name__)
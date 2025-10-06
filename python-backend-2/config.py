# Configuração da aplicação FastAPI
# Define middlewares, CORS e configurações de logging
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def configure_app(app):
    """Configura middlewares e settings da aplicação FastAPI
    
    Args:
        app: Instância da aplicação FastAPI
    """
    # Configura CORS para permitir requisições do frontend e sistema AtoM
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],     # Permite todas as origens temporariamente
        allow_credentials=False, # Desabilita credentials para debug
        allow_methods=["*"],     # Permite todos os métodos HTTP
        allow_headers=["*"],     # Permite todos os headers
    )
    
    # Configura logging básico para a aplicação
    logging.basicConfig(level=logging.INFO)
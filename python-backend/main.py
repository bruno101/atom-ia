# Arquivo principal da aplicação FastAPI
# Ponto de entrada do servidor web para o sistema de chatbot RAG

# Código de debug comentado - descomente para executar testes
"""from rag_models.model4.debug import debug_hyde
debug_hyde()"""

from fastapi import FastAPI
from api import routers
from config import configure_app

# Cria a instância principal da aplicação FastAPI
app = FastAPI(
    title="Chatbot ModestIA",
    description="API para responder consultas com RAG e LLM",
    version="1.1.0"
)

# Configura middlewares (CORS, logging, etc.)
configure_app(app)
# Inclui as rotas da API
app.include_router(routers.router)

# Executa o servidor se o arquivo for chamado diretamente
if __name__ == "__main__":
    import uvicorn
    # Inicia o servidor na porta 7860 com hot reload desabilitado
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=False)
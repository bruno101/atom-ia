from fastapi import FastAPI
from api import routers
from config import configure_app

app = FastAPI(
    title="Chatbot ModestIA",
    description="API para responder consultas com RAG e LLM",
    version="1.1.0"
)

configure_app(app)
app.include_router(routers.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=False)
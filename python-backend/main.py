# main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from rag_core import pipeline_completo

app = FastAPI()

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    consulta = data.get("consulta")

    if not consulta:
        return JSONResponse(content={"error": "Consulta não fornecida."}, status_code=400)

    try:
        resposta = pipeline_completo(consulta)
        return {"resposta": resposta}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860)

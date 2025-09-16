# 1. Base Image: Use uma imagem oficial do Python, a versão 'slim' é ótima para produção.
FROM python:3.11-slim

# 2. Set Working Directory: Defina um diretório de trabalho dentro do contêiner.
WORKDIR /app

# 3. Copy and Install Dependencies: Copie primeiro o requirements.txt para aproveitar o cache do Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir --proxy="http://10.0.220.11:3128" -r requirements.txt

# 4. Copy Application Code: Copie o resto do código da sua aplicação.
COPY . .

# 5. Expose Port: Informe ao Docker que o contêiner escutará na porta 8000.
EXPOSE 7860

# 6. Run Application: O comando para iniciar o servidor uvicorn.
#    O host 0.0.0.0 é essencial para que a aplicação seja acessível de fora do contêiner.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

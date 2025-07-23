FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV HF_HOME=/root/.cache/huggingface

ENV HTTP_PROXY=http://10.0.220.11:3128
ENV HTTPS_PROXY=http://10.0.220.11:3128
ENV http_proxy=http://10.0.220.11:3128
ENV https_proxy=http://10.0.220.11:3128
ENV NO_PROXY=localhost,127.0.0.1,elasticsearch

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-large')"

COPY . .

CMD ["tail", "-f", "/dev/null"]

#CMD ["python", "main.py"]

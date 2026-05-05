# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

WORKDIR /app

# Copiar requirements
COPY services/pesagem_service/requirements.txt .

# Instalar dependências
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copiar código da aplicação
COPY services/pesagem_service/app/ ./app/

# Expor porta
EXPOSE 8001

# Comando para rodar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

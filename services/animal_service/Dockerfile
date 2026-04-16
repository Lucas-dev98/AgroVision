FROM python:3.11-slim

WORKDIR /app

# Instalar dependências sistem
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY services/animal_service/requirements.txt .
COPY shared/requirements.txt shared-requirements.txt

# Instalar Python deps
RUN pip install --no-cache-dir -r shared-requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY services/animal_service/ .
COPY shared/ ./shared/

# Expor porta
EXPOSE 8001

# Rodar app
CMD ["python", "main.py"]

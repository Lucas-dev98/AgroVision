# 🐳 Docker Compose Setup

## Estrutura do docker-compose.yml

```yaml
version: '3.8'

services:
  # Banco de dados
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: agrovision
      POSTGRES_PASSWORD: agrovision_dev
      POSTGRES_DB: agrovision_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agrovision"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (cache e queue)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # API Gateway
  api-gateway:
    build:
      context: ./services/api-gateway
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://agrovision:agrovision_dev@postgres:5432/agrovision_db
      REDIS_URL: redis://redis:6379
      ENV: dev
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./services/api-gateway:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # animal-service
  animal-service:
    build:
      context: ./services/animal-service
    ports:
      - "8001:8000"
    environment:
      DATABASE_URL: postgresql://agrovision:agrovision_dev@postgres:5432/agrovision_db
      SERVICE_NAME: animal-service
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./services/animal-service:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # pesagem-service
  pesagem-service:
    build:
      context: ./services/pesagem-service
    ports:
      - "8002:8000"
    environment:
      DATABASE_URL: postgresql://agrovision:agrovision_dev@postgres:5432/agrovision_db
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./services/pesagem-service:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # alimentacao-service
  alimentacao-service:
    build:
      context: ./services/alimentacao-service
    ports:
      - "8003:8000"
    environment:
      DATABASE_URL: postgresql://agrovision:agrovision_dev@postgres:5432/agrovision_db
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./services/alimentacao-service:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # sanidade-service
  sanidade-service:
    build:
      context: ./services/sanidade-service
    ports:
      - "8004:8000"
    environment:
      DATABASE_URL: postgresql://agrovision:agrovision_dev@postgres:5432/agrovision_db
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./services/sanidade-service:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # cotacao-service
  cotacao-service:
    build:
      context: ./services/cotacao-service
    ports:
      - "8005:8000"
    environment:
      DATABASE_URL: postgresql://agrovision:agrovision_dev@postgres:5432/agrovision_db
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./services/cotacao-service:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # analytics-service
  analytics-service:
    build:
      context: ./services/analytics-service
    ports:
      - "8006:8000"
    environment:
      DATABASE_URL: postgresql://agrovision:agrovision_dev@postgres:5432/agrovision_db
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./services/analytics-service:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

## Comandos Principais

### Iniciar
```bash
docker-compose up -d
```

### Parar
```bash
docker-compose down
```

### Logs
```bash
docker-compose logs -f api-gateway
docker-compose logs api-gateway pesagem-service
```

### Reconstruir serviço
```bash
docker-compose up -d --build pesagem-service
```

### Executar migrations
```bash
docker-compose exec api-gateway alembic upgrade head
```

### Shell do PostgreSQL
```bash
docker-compose exec postgres psql -U agrovision -d agrovision_db
```

### Limpar volumes
```bash
docker-compose down -v
```

## Portas dos Serviços

| Serviço | Porta | URL |
|---------|-------|-----|
| API Gateway | 8000 | http://localhost:8000 |
| animal-service | 8001 | http://localhost:8001 |
| pesagem-service | 8002 | http://localhost:8002 |
| alimentacao-service | 8003 | http://localhost:8003 |
| sanidade-service | 8004 | http://localhost:8004 |
| cotacao-service | 8005 | http://localhost:8005 |
| analytics-service | 8006 | http://localhost:8006 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |

## Documentação da API

Cada serviço expõe Swagger automaticamente:

- http://localhost:8000/docs (API Gateway)
- http://localhost:8001/docs (animal-service)
- http://localhost:8002/docs (pesagem-service)
- Etc...

## Health Checks

Monitorar saúde dos serviços:

```bash
curl http://localhost:8000/health
curl http://localhost:5432 # PostgreSQL
```

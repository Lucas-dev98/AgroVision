# 🐳 Docker Compose - AgroVision Stack

Orquestração completa de todos os microserviços com PostgreSQL e Redis.

## 📋 Serviços

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **PostgreSQL 16** | 5432 | Banco de dados principal |
| **Redis 7** | 6379 | Cache distribuído |
| **animal-service** | 8000 | API de Animais (Swagger: `/docs`) |
| **pesagem-service** | 8001 | API de Pesagens (Swagger: `/docs`) |
| **cotacao-service** | 8002 | API de Cotações (Swagger: `/docs`) |
| **api-gateway** | 8080 | API Gateway (futuro) |

## 🚀 Quick Start

### 1. Clonar e configurar

```bash
cd /home/lucasbastos/AgroVision
cp .env.example .env
# Editar .env se necessário
```

### 2. Build das imagens

```bash
make build
# ou
docker-compose build
```

### 3. Iniciar stack

```bash
make up
# ou
docker-compose up -d
```

### 4. Verificar saúde

```bash
make health
# ou
docker-compose ps
```

### 5. Acessar serviços

- **Animal Service**: http://localhost:8000/docs
- **Pesagem Service**: http://localhost:8001/docs
- **Cotacao Service**: http://localhost:8002/docs
- **Database**: `psql -h localhost -U agrovision -d agrovision`
- **Redis**: `redis-cli -h localhost`

## 📖 Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar todos os serviços
make up

# Parar todos os serviços
make down

# Reiniciar todos os serviços
make restart

# Ver status
docker-compose ps

# Remover volumes (limpeza completa)
docker-compose down -v
```

### Logs

```bash
# Ver logs de todos os serviços
make logs

# Ver logs de um serviço específico
make logs-animal
make logs-pesagem
make logs-cotacao
make logs-db

# Seguir logs em tempo real
docker-compose logs -f animal-service
```

### Database

```bash
# Acessar PostgreSQL
make db-shell

# Fazer backup do banco
make db-dump
# Arquivo salvo em: backups/agrovision_YYYYMMDD_HHMMSS.sql

# Resetar banco de dados
make db-reset
```

### Testes

```bash
# Rodar todos os testes
make test-all

# Testar um serviço específico
make test-animal
make test-pesagem
make test-cotacao
```

### Shell

```bash
# Entrar no container de um serviço
make shell-animal
make shell-pesagem
make shell-cotacao
make shell-db

# Ou diretamente
docker-compose exec animal-service /bin/bash
```

## 🔧 Configuração (.env)

```bash
# Database
DB_USER=agrovision
DB_PASSWORD=agrovision123
DB_NAME=agrovision
DB_PORT=5432

# Redis
REDIS_PORT=6379

# Services
ANIMAL_SERVICE_PORT=8000
PESAGEM_SERVICE_PORT=8001
COTACAO_SERVICE_PORT=8002
GATEWAY_PORT=8080

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
```

## 🏥 Health Checks

Cada serviço tem um health check automático:

```bash
# Verificar saúde
make health

# Ou manualmente
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## 🗄️ Database Access

### Via psql

```bash
# Via container
docker-compose exec db psql -U agrovision -d agrovision

# Via host (se PostgreSQL instalado localmente)
psql -h localhost -U agrovision -d agrovision
```

### Via Python

```python
from sqlalchemy import create_engine
engine = create_engine("postgresql://agrovision:agrovision123@localhost:5432/agrovision")
```

## 🔄 Workflows Comuns

### Deploy completo

```bash
make clean      # Limpeza completa
make build      # Build das imagens
make up         # Iniciar stack
make health     # Verificar saúde
```

### Desenvolvimento

```bash
make up         # Iniciar stack
make test-all   # Rodar testes
make logs       # Ver logs
```

### Debugging

```bash
make logs-animal        # Ver logs do animal-service
make shell-animal       # Acessar shell do container
make db-shell           # Acessar banco de dados
```

### Backup & Recovery

```bash
# Backup
make db-dump

# Restore (manual)
docker-compose exec -T db psql -U agrovision -d agrovision < backups/agrovision_YYYYMMDD_HHMMSS.sql
```

## 📊 Monitoramento

### Ver containers em execução

```bash
docker-compose ps
```

### Ver uso de recursos

```bash
docker stats
```

### Ver network

```bash
docker network ls
docker network inspect agrovision_agrovision
```

## 🚨 Troubleshooting

### PostgreSQL não inicia

```bash
# Verificar logs
docker-compose logs db

# Resetar
make db-reset

# Ou
docker-compose down -v
docker-compose up -d db
```

### Serviço não responde

```bash
# Verificar logs
docker-compose logs animal-service

# Verificar health
docker-compose ps

# Reiniciar
docker-compose restart animal-service
```

### Porta já em uso

```bash
# Encontrar processo usando porta
lsof -i :8000

# Mudar porta no .env
# ANIMAL_SERVICE_PORT=8010
docker-compose down
docker-compose up -d
```

### Problemas de permissão

```bash
# Rodar como root
sudo docker-compose up -d

# Ou adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

## 🔐 Segurança

### Mudar senhas padrão

```bash
# .env
DB_USER=seu_usuario
DB_PASSWORD=sua_senha_forte
```

### Limitar acesso a portas

```yaml
# docker-compose.yml
ports:
  - "127.0.0.1:8000:8000"  # Apenas localhost
```

## 📦 Build de Imagens

### Build completo

```bash
make build          # Build com cache
make build-nocache  # Build sem cache
```

### Build individual

```bash
docker-compose build animal-service
docker-compose build pesagem-service
docker-compose build cotacao-service
```

## 🧹 Limpeza

```bash
# Parar containers sem remover volumes
make down

# Remover tudo (containers + volumes)
make clean

# Ou manualmente
docker-compose down -v
```

## 📚 Documentação

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Redis Docker](https://hub.docker.com/_/redis)
- [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/)

## ✅ Checklist de Deploy

- [ ] Clonar repositório
- [ ] Copiar `.env.example` para `.env`
- [ ] Editar variáveis de ambiente em `.env`
- [ ] Rodar `make build`
- [ ] Rodar `make up`
- [ ] Verificar `make health`
- [ ] Acessar Swagger docs em `http://localhost:8000/docs`
- [ ] Rodar `make test-all`
- [ ] Fazer backup inicial: `make db-dump`

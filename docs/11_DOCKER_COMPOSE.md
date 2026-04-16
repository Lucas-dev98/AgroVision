# Docker Compose - Orquestração de Microserviços

## 🐳 Arquitetura

```
┌─────────────────────────────────────────────────┐
│          Docker Compose Network                 │
│          (agrovision)                            │
│                                                  │
│  ┌────────────────┐  ┌────────────────┐        │
│  │ animal-service │  │pesagem-service │        │
│  │   (8000)       │  │   (8001)       │        │
│  │   FastAPI      │  │   FastAPI      │        │
│  └────────────────┘  └────────────────┘        │
│           │                 │                   │
│  ┌────────────────────────────────┐            │
│  │   cotacao-service (8002)       │            │
│  │   FastAPI                      │            │
│  └────────────────────────────────┘            │
│           │                                     │
│  ╔════════╩═════════════╗                      │
│  ║                      ║                       │
│  ▼                      ▼                       │
│ ┌──────────────┐  ┌──────────────┐             │
│ │   PostgreSQL │  │    Redis     │             │
│ │    (5432)    │  │   (6379)     │             │
│ │   Database   │  │   Cache      │             │
│ └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────┘
```

## 📋 Serviços

### 1. **PostgreSQL 16 (db)**
- **Porta**: 5432
- **Container**: agrovision-db
- **Volume**: db_data (permanente)
- **Health Check**: Ativo

### 2. **Redis 7 (redis)**
- **Porta**: 6379
- **Container**: agrovision-redis
- **Volume**: redis_data (persistência)
- **Health Check**: Ativo

### 3. **Animal Service (animal-service)**
- **Porta**: 8000
- **Container**: agrovision-animal-service
- **Dependências**: PostgreSQL + Redis
- **Health Check**: HTTP GET /health

### 4. **Pesagem Service (pesagem-service)**
- **Porta**: 8001
- **Container**: agrovision-pesagem-service
- **Dependências**: PostgreSQL + Redis
- **Health Check**: HTTP GET /health

### 5. **Cotacao Service (cotacao-service)**
- **Porta**: 8002
- **Container**: agrovision-cotacao-service
- **Dependências**: PostgreSQL + Redis
- **Health Check**: HTTP GET /health

## 🚀 Primeiros Passos

### 1. Preparar Environment

```bash
# Copiar configurações
cp .env.example .env

# (Opcionalmente editar .env para customização)
```

### 2. Build das Imagens

```bash
# Build de todas as imagens
make docker-build

# Ou com Docker Compose diretamente
docker-compose build
```

### 3. Iniciar Todos os Serviços

```bash
# Iniciar stack completo
make docker-up

# Verificar status
make docker-ps

# Health check
make docker-health
```

## 📍 Acessar Serviços

Uma vez que tudo está rodando:

- **Animal Service Swagger**: http://localhost:8000/docs
- **Pesagem Service Swagger**: http://localhost:8001/docs
- **Cotacao Service Swagger**: http://localhost:8002/docs
- **PostgreSQL**: localhost:5432 (user: agrovision)
- **Redis**: localhost:6379

## 🛠️ Comandos Úteis

### Visualizar Logs

```bash
# Logs de todos os serviços
make docker-logs

# Logs específicos
make docker-logs-service SERVICE=animal-service
make docker-logs-service SERVICE=pesagem-service
make docker-logs-service SERVICE=cotacao-service
make docker-logs-service SERVICE=db
```

### Acessar Containers

```bash
# Shell no container de um serviço
make docker-shell SERVICE=animal-service

# Acesso ao PostgreSQL
make docker-db-shell

# Acesso ao Redis
make docker-redis-shell
```

### Executar Operações

```bash
# Rodar migrations Alembic
make docker-migrate

# Rodar testes dentro dos containers
make docker-test

# Parar todos os serviços
make docker-down

# Limpar e resetar tudo (CUIDADO!)
make docker-clean
```

### Rebuild Completo

```bash
# Reconstruir sem cache e reiniciar
make docker-rebuild
```

## 📊 Variáveis de Ambiente

Editáveis no `.env`:

```bash
# Database
DB_USER=agrovision
DB_PASSWORD=agrovision
DB_NAME=agrovision
DB_PORT=5432

# Redis
REDIS_PORT=6379

# Microserviços (portas expostas)
ANIMAL_SERVICE_PORT=8000
PESAGEM_SERVICE_PORT=8001
COTACAO_SERVICE_PORT=8002

# Logging
LOG_LEVEL=INFO
SQL_ECHO=false
```

## 🔄 Workflow Típico de Desenvolvimento

```bash
# 1. Iniciar a stack
make docker-up

# 2. Verificar os logs
make docker-logs

# 3. Fazer alterações no código (containers auto-rebuild se necessário)

# 4. Rodar testes
make docker-test

# 5. Para debug
make docker-shell SERVICE=animal-service

# 6. Parar quando terminar
make docker-down
```

## 🗂️ Estrutura de Arquivos

```
AgroVision/
├── docker-compose.yml       # Orquestração
├── .env.example             # Template de variáveis
├── .dockerignore            # Ignore para builds
├── Makefile                 # Commandos úteis
├── infra/
│   ├── alembic/            # Migrations PostgreSQL
│   ├── postgres/
│   │   └── init.sql        # Schema inicial
│   └── test_migrations.py
├── services/
│   ├── animal_service/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   ├── pesagem_service/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   └── cotacao_service/
│       ├── Dockerfile
│       └── .dockerignore
└── shared/
    ├── database.py         # Config compartilhada
    └── requirements.txt
```

## 🐛 Troubleshooting

### "Port already in use"

Alterar a porta no `.env`:
```bash
ANIMAL_SERVICE_PORT=8010  # ao invés de 8000
```

### Containers não iniciam

Verificar logs:
```bash
docker-compose logs db
docker-compose logs redis
```

### "Connection refused" ao acessar serviços

Aguardar initialização completa:
```bash
# Verificar health
make docker-health

# Aguardar se show "starting"
```

### PostgreSQL não cria tabelas

Rodar migrations manualmente:
```bash
make docker-migrate
```

## 📚 Referências

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Redis Docker](https://hub.docker.com/_/redis)
- [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/)

## 🚨 Importante

- **Nunca** commitar `.env` com senhas reais
- Usar `.env.example` como template
- Senhas deste exemplo são apenas para desenvolvimento
- Para produção, usar secrets gerenciados (Docker Secrets, Kubernetes, AWS Secrets Manager, etc.)

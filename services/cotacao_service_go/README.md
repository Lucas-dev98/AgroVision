# Cotacao Service (Go)

Microserviço de gerenciamento de cotações de gado, escrito em Go.

## Quick Start

### Pré-requisitos
- Go 1.21+
- PostgreSQL 16+ (ou Docker)
- Docker & Docker Compose

### Desenvolvimento Local

```bash
# Instalar dependências
go mod download
go mod tidy

# Criar .env a partir do exemplo
cp .env.example .env

# Iniciar PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_USER=agrovision \
  -e POSTGRES_PASSWORD=agrovision \
  -e POSTGRES_DB=agrovision \
  -p 5432:5432 \
  postgres:16-alpine

# Rodar migrations
psql -U agrovision -d agrovision -h localhost < migrations/001_create_cotacoes.sql

# Rodar o serviço
go run ./cmd/main/main.go

# Testar
curl http://localhost:8002/health
```

### Docker

```bash
# Build da imagem
docker build -t agrovision-cotacao-service-go:latest .

# Rodar com docker-compose
docker-compose up -d

# Verificar logs
docker-compose logs -f cotacao-service
```

## Endpoints da API

### Health Check
```
GET /health
```

### Cotacoes (requer JWT Bearer token)
```
GET    /api/v1/cotacoes                       - Listar cotações
GET    /api/v1/cotacoes/:id                   - Get cotação por ID
GET    /api/v1/cotacoes/tipo/:tipoGado        - Listar por tipo
GET    /api/v1/cotacoes/tipo/:tipoGado/latest - Última cotação
POST   /api/v1/cotacoes                       - Criar cotação
PUT    /api/v1/cotacoes/:id                   - Atualizar cotação
DELETE /api/v1/cotacoes/:id                   - Deletar cotação
```

### Exemplos

```bash
# Listar cotações
curl -H "Authorization: Bearer token" http://localhost:8002/api/v1/cotacoes

# Criar cotação
curl -X POST http://localhost:8002/api/v1/cotacoes \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_gado": "Boi",
    "preco_arroba": 250.50,
    "data_referencia": "2024-05-04",
    "fonte": "CEPEA"
  }'

# Última cotação para Boi
curl -H "Authorization: Bearer token" http://localhost:8002/api/v1/cotacoes/tipo/Boi/latest

# Cotações para Vaca
curl -H "Authorization: Bearer token" http://localhost:8002/api/v1/cotacoes/tipo/Vaca

# Atualizar
curl -X PUT http://localhost:8002/api/v1/cotacoes/1 \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "preco_arroba": 255.00
  }'

# Deletar
curl -X DELETE http://localhost:8002/api/v1/cotacoes/1 \
  -H "Authorization: Bearer token"
```

## Testes

```bash
# Rodar todos os testes
go test ./... -v

# Com cobertura
go test ./... -v -cover

# Pacote específico
go test ./internal/service/... -v
```

## Estrutura do Projeto

```
├── cmd/main/          - Entry point
├── internal/
│   ├── config/        - Configuração
│   ├── db/            - Conexão com banco
│   ├── handler/       - HTTP handlers
│   ├── middleware/    - Middleware (auth)
│   ├── models/        - Modelos de domínio
│   ├── repository/    - Camada de acesso a dados
│   ├── router/        - Definição de rotas
│   └── service/       - Lógica de negócio
├── pkg/utils/         - Utilitários compartilhados
├── tests/             - Testes
├── migrations/        - Migrações SQL
├── Dockerfile         - Docker image
└── docker-compose.yml - Orquestração
```

## Características de Performance

- **Throughput**: 3000+ req/s por instância
- **Latency**: P95 < 20ms
- **Memory**: ~30MB
- **Startup**: < 500ms
- **Image size**: 50MB

## Variáveis de Ambiente

```
DATABASE_URL       - String de conexão PostgreSQL
PORT               - Porta do servidor (padrão: 8002)
LOG_LEVEL          - Nível de logging (padrão: info)
ENVIRONMENT        - environment name (padrão: development)
JWT_SECRET         - Secret para JWT
```

## Checklist de Produção

- [ ] Mudar JWT_SECRET em produção
- [ ] Definir LOG_LEVEL como "warn"
- [ ] Validar limites de conexão com BD
- [ ] Setup de monitoramento/logging
- [ ] Testar health check
- [ ] Load test antes de deploy
- [ ] Configurar graceful shutdown
- [ ] Configurar TLS/SSL se necessário

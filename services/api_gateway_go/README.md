# AgroVision API Gateway

API Gateway em Go para roteamento de requisições entre os microsserviços da plataforma AgroVision.

## Funcionalidades

- ✅ Roteamento de requisições para múltiplos serviços upstream
- ✅ Rate limiting com janela deslizante
- ✅ CORS configurado
- ✅ Tratamento de erros centralizado
- ✅ Logging estruturado com Zap
- ✅ Headers de segurança
- ✅ Health check endpoint

## Arquitetura

```
┌─────────────────┐
│   Client        │
└────────┬────────┘
         │
┌────────▼──────────┐
│  API Gateway      │
│  (Port 8000)      │
├───────────────────┤
│ Rate Limiter      │
│ CORS Handler      │
│ Error Handler     │
└────────┬──────────┘
         │
    ┌────┴─────┬────────┬────────┬────────┐
    │           │        │        │        │
┌───▼──┐ ┌──────▼┐ ┌────▼──┐ ┌──▼────┐ ┌─▼──────┐
│Anim  │ │Pesag │ │Cotac  │ │Vision │ │ML      │
│Port  │ │Port  │ │Port   │ │Port   │ │Port    │
│9000  │ │8001  │ │8002   │ │8003   │ │8004    │
└──────┘ └──────┘ └───────┘ └───────┘ └────────┘
```

## Configuração

### Variáveis de Ambiente

```bash
PORT=8000                              # Porta do gateway
ENVIRONMENT=development                # Ambiente (development/production)
LOG_LEVEL=debug                        # Nível de log

# URLs dos serviços upstream
ANIMAL_SERVICE_URL=http://localhost:9000
PESAGEM_SERVICE_URL=http://localhost:8001
COTACAO_SERVICE_URL=http://localhost:8002
VISION_SERVICE_URL=http://localhost:8003
ML_SERVICE_URL=http://localhost:8004

# Rate Limiting
RATE_LIMIT_REQUESTS=100               # Requisições por janela
RATE_LIMIT_WINDOW=1m                  # Duração da janela

JWT_SECRET=your-secret-key-here       # Chave para JWT
```

## Rotas

### Health Check
```
GET /health
```

### Animals
```
GET    /api/v1/animals
GET    /api/v1/animals/:id
POST   /api/v1/animals
PUT    /api/v1/animals/:id
DELETE /api/v1/animals/:id
```

### Pesagens (Pesos)
```
GET    /api/v1/pesagens
GET    /api/v1/pesagens/:id
POST   /api/v1/pesagens
PUT    /api/v1/pesagens/:id
DELETE /api/v1/pesagens/:id
```

### Cotações (Preços)
```
GET    /api/v1/cotacoes
GET    /api/v1/cotacoes/:id
POST   /api/v1/cotacoes
PUT    /api/v1/cotacoes/:id
DELETE /api/v1/cotacoes/:id
```

### Vision
```
POST   /api/v1/vision/detect
GET    /api/v1/vision/results/:id
```

### ML
```
GET    /api/v1/ml/models
GET    /api/v1/ml/models/:id
POST   /api/v1/ml/predict
POST   /api/v1/ml/train
```

## Rate Limiting

O API Gateway implementa rate limiting por IP com janela deslizante.

- **Limite padrão**: 100 requisições por minuto
- **Configurável via**: Variáveis de ambiente RATE_LIMIT_REQUESTS e RATE_LIMIT_WINDOW

Quando o limite é excedido, a resposta é:
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

## Executar

### Localmente

```bash
# Instalar dependências
go mod download

# Executar
go run ./cmd/main/main.go
```

### Docker

```bash
# Build
docker build -t agrovision/api-gateway:latest .

# Run
docker run -p 8000:8000 \
  -e ANIMAL_SERVICE_URL=http://host.docker.internal:9000 \
  -e PESAGEM_SERVICE_URL=http://host.docker.internal:8001 \
  -e COTACAO_SERVICE_URL=http://host.docker.internal:8002 \
  agrovision/api-gateway:latest
```

### Docker Compose

```bash
docker-compose up
```

## Testes

```bash
go test ./... -v
```

## Estrutura do Projeto

```
api_gateway_go/
├── cmd/
│   └── main/
│       └── main.go              # Ponto de entrada
├── internal/
│   ├── config/
│   │   └── config.go            # Configuração da aplicação
│   ├── middleware/
│   │   └── ratelimit.go         # Rate limiting e outros middlewares
│   ├── proxy/
│   │   └── proxy.go             # Lógica de roteamento
│   └── router/
│       └── router.go            # Definição de rotas
├── tests/
│   └── integration_test.go      # Testes integrados
├── go.mod                        # Dependências
├── Dockerfile                    # Build Docker
└── docker-compose.yml            # Composição de serviços
```

## Desenvolvimento

### Adicionar nova rota

1. Adicione a rota em `internal/router/router.go`
2. Configure a URL do serviço em `internal/config/config.go`
3. Teste com curl ou Postman

### Adicionar novo middleware

1. Crie a função em `internal/middleware/ratelimit.go` ou novo arquivo
2. Registre em `internal/router/router.go`

## Performance

- **Rate Limiting**: Usa map de requests por IP com limpeza automática
- **Proxy**: Forward HTTP com reuso de conexões
- **Memory**: Cleanup automático a cada minuto

## Segurança

- ✅ Remoção de hop-by-hop headers
- ✅ CORS configurado
- ✅ Content-Security-Policy
- ✅ X-Frame-Options: DENY
- ✅ X-XSS-Protection
- ✅ X-Content-Type-Options: nosniff

## TODO

- [ ] Authentication/JWT validation
- [ ] Request/Response logging
- [ ] Circuit breaker pattern
- [ ] Request timeout handling
- [ ] Service health checks
- [ ] Metrics collection (Prometheus)
- [ ] Distributed tracing

## Autor

AgroVision Team

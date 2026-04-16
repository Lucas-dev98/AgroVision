# 🔐 API Gateway - AgroVision

Central de autenticação, roteamento e agregação de serviços para o ecossistema AgroVision.

## 📋 Objetivo

O API Gateway fornece:
- **Autenticação Centralizada**: JWT (JSON Web Tokens)
- **Roteamento Inteligente**: Redirecionamento de requisições para serviços
- **Rate Limiting**: Proteção contra abuso
- **CORS Unificado**: Configuração centralizada
- **Agregação de Dados**: Combinar respostas de múltiplos serviços

## 🏗️ Arquitetura

```
┌────────────────────────────────────────┐
│   Cliente (Web/Mobile/Desktop)         │
└──────────────┬─────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│   API Gateway (Porta 8080)              │
│  ├─ Autenticação JWT                   │
│  ├─ Rate Limiting                      │
│  ├─ CORS Middleware                    │
│  └─ Health Check                       │
└────────────────────────────────────────┘
    │          │          │
    ▼          ▼          ▼
┌───────────┐ ┌──────────┐ ┌──────────┐
│ Animal    │ │ Pesagem  │ │ Cotação  │
│ Service   │ │ Service  │ │ Service  │
│ (8000)    │ │ (8001)   │ │ (8002)   │
└───────────┘ └──────────┘ └──────────┘
```

## 🔑 Autenticação JWT

### Fluxo de Login

```
1. Cliente envia credenciais (username + password)
2. Gateway verifica credenciais
3. Gateway gera token JWT com expiração
4. Cliente recebe token
5. Cliente inclui token em requisições subsequentes
6. Gateway valida token antes de rotear
```

### Estrutura do Token

```json
{
  "sub": "username",
  "scopes": ["read", "write"],
  "exp": 1234567890
}
```

## 🛣️ Roteamento de Requisições

### Prefixos de Rota

```
/api/v1/animais/*       → animal-service
/api/v1/pesagens/*      → pesagem-service
/api/v1/cotacoes/*      → cotacao-service
/auth/*                 → Gateway (autenticação)
/health                 → Gateway (health check)
```

## ⚡ Rate Limiting

- **100 requisições** por **60 segundos** por IP
- Configurável via variáveis de ambiente
- Retorna HTTP 429 quando excedido

## 🧪 Testes (31 Testes ✅)

### Estrutura de Testes

```
tests/
├── test_api.py         (11 testes) - Health check, root endpoint, CORS
├── test_auth.py        (13 testes) - JWT, passwords, tokens
└── test_config.py      (7 testes)  - Configurações
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=app

# Um arquivo específico
pytest tests/test_auth.py -v

# Uma classe específica
pytest tests/test_auth.py::TestJWTToken -v
```

## 📊 Testes Inclusos

### Health Check (3 testes)
- ✅ Retorna status "healthy"
- ✅ Estrutura de resposta correta
- ✅ Inclui versão do serviço

### Endpoints Raiz (3 testes)
- ✅ Retorna informações do gateway
- ✅ Inclui URLs dos serviços
- ✅ Link para documentação

### Autenticação JWT (13 testes)

**Password Hashing:**
- ✅ Cria hash da senha
- ✅ Verifica senha correta
- ✅ Rejeita senha incorreta
- ✅ Mesmo password gera hashes diferentes

**Token Creation:**
- ✅ Retorna string de token
- ✅ Suporta expiração customizada
- ✅ Valida token válido
- ✅ Rejeita token inválido
- ✅ Inclui scopes no token
- ✅ Inclui username no token

**Token Data:**
- ✅ Cria TokenData corretamente
- ✅ Username é opcional
- ✅ Scopes têm valor padrão

### Configuração (7 testes)
- ✅ URLs dos serviços
- ✅ Animal-service URL padrão
- ✅ Pesagem-service URL padrão
- ✅ Cotacao-service URL padrão
- ✅ Configuração JWT presente
- ✅ Rate limiting configurado
- ✅ Valores padrão corretos

## 🚀 Endpoints

### Health Check

```bash
GET /health

Response 200:
{
  "status": "healthy",
  "service": "api-gateway",
  "version": "1.0.0"
}
```

### Root Endpoint

```bash
GET /

Response 200:
{
  "name": "AgroVision API Gateway",
  "version": "1.0.0",
  "documentation": "/docs",
  "services": {
    "animal": "http://localhost:8000/docs",
    "pesagem": "http://localhost:8001/docs",
    "cotacao": "http://localhost:8002/docs"
  }
}
```

## 🔐 Segurança

### Recomendações

1. **Change SECRET_KEY**: Alterar chave secreta em produção
   ```
   SECRET_KEY="seu-segredo-super-seguro-aqui-com-32-caracteres-ou-mais"
   ```

2. **HTTPS Obrigatório**: Em produção, sempre usar HTTPS
   ```
   https://api.example.com/health
   ```

3. **Tokens Curtos**: Manter expiração de tokens curta
   ```
   ACCESS_TOKEN_EXPIRE_MINUTES=15  # Máximo 15 minutos
   ```

4. **Rate Limiting Ativo**: Sempre ativar rate limiting
   ```
   RATE_LIMIT_ENABLED=true
   ```

## 📦 Dependências

```
fastapi==0.104.1           # Framework web
uvicorn==0.24.0            # ASGI server
python-jose==3.3.0         # JWT handling
passlib==1.7.4             # Password hashing
bcrypt==4.1.2              # Bcrypt hashing
python-multipart==0.0.6    # Form data parsing
```

## 🔧 Configuração

### .env

```bash
# URLs dos Serviços
ANIMAL_SERVICE_URL=http://animal-service:8000
PESAGEM_SERVICE_URL=http://pesagem-service:8001
COTACAO_SERVICE_URL=http://cotacao-service:8002

# JWT
SECRET_KEY=sua-chave-secreta-super-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Gateway
PORT=8080
HOST=0.0.0.0
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_SECONDS=60
```

## 🐳 Docker

### Build

```bash
docker build -t api-gateway .
```

### Run

```bash
docker run -p 8080:8080 \
  -e ANIMAL_SERVICE_URL=http://animal-service:8000 \
  -e PESAGEM_SERVICE_URL=http://pesagem-service:8001 \
  -e COTACAO_SERVICE_URL=http://cotacao-service:8002 \
  api-gateway
```

### Docker Compose

```yaml
api-gateway:
  build: ./services/api_gateway
  ports:
    - "${GATEWAY_PORT:-8080}:8080"
  environment:
    - ANIMAL_SERVICE_URL=http://animal-service:8000
    - PESAGEM_SERVICE_URL=http://pesagem-service:8001
    - COTACAO_SERVICE_URL=http://cotacao-service:8002
  depends_on:
    - animal-service
    - pesagem-service
    - cotacao-service
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 10s
```

## 📚 Documentação Interativa

Acesse a documentação Swagger em:
```
http://localhost:8080/docs
```

Ou ReDoc:
```
http://localhost:8080/redoc
```

## 🧩 Próximos Passos

1. **Implementar Roteamento Proxy**: Rotear requisições para serviços
2. **Validar Tokens**: Decorator para validar tokens em rotas
3. **Rate Limiter Middleware**: Implementar rate limiting por IP
4. **Agregação de Dados**: Combinar respostas de múltiplos serviços
5. **Logging Centralizado**: Logs estruturados para auditoria
6. **Métricas**: Prometheus para monitoramento

## 📝 Exemplo de Uso

### Com cURL

```bash
# Health check
curl http://localhost:8080/health

# Root endpoint
curl http://localhost:8080/

# Com token (após implementar auth endpoint)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8080/api/v1/animais
```

### Com Python

```python
import requests

# Health check
response = requests.get("http://localhost:8080/health")
print(response.json())

# Root
response = requests.get("http://localhost:8080/")
print(response.json())
```

## ✅ Checklist

- [x] Estrutura de pastas
- [x] Autenticação JWT
- [x] Health check
- [x] CORS configurado
- [x] 31 testes passing
- [ ] Roteamento proxy (próximo)
- [ ] Rate limiting middleware (próximo)
- [ ] Agregação de dados (futuro)
- [ ] Logging centralizado (futuro)
- [ ] Métricas Prometheus (futuro)

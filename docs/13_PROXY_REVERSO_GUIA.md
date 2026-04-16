# 🔄 Proxy Reverso & Roteamento - API Gateway

Implementação de proxy reverso para rotear requisições para os microserviços.

## 📋 Visão Geral

O API Gateway agora funciona como um proxy reverso, roteando requisições para os serviços apropriados:

```
Cliente HTTP
    │
    └─→ GET /api/v1/animais
           │
           └─→ API Gateway
                  │
                  └─→ GET http://animal-service:8000/api/v1/animais
                      │
                      └─→ Resposta
```

## 🛣️ Rotas de Proxy

### Animal Service
```
GET    /api/v1/animais              → animal-service /api/v1/animais
GET    /api/v1/animais/{id}         → animal-service /api/v1/animais/{id}
POST   /api/v1/animais              → animal-service /api/v1/animais
PUT    /api/v1/animais/{id}         → animal-service /api/v1/animais/{id}
DELETE /api/v1/animais/{id}         → animal-service /api/v1/animais/{id}
```

### Pesagem Service
```
GET    /api/v1/pesagens              → pesagem-service /api/v1/pesagens
GET    /api/v1/pesagens/{id}         → pesagem-service /api/v1/pesagens/{id}
POST   /api/v1/pesagens              → pesagem-service /api/v1/pesagens
PUT    /api/v1/pesagens/{id}         → pesagem-service /api/v1/pesagens/{id}
DELETE /api/v1/pesagens/{id}         → pesagem-service /api/v1/pesagens/{id}
```

### Cotação Service
```
GET    /api/v1/cotacoes              → cotacao-service /api/v1/cotacoes
GET    /api/v1/cotacoes/{id}         → cotacao-service /api/v1/cotacoes/{id}
POST   /api/v1/cotacoes              → cotacao-service /api/v1/cotacoes
PUT    /api/v1/cotacoes/{id}         → cotacao-service /api/v1/cotacoes/{id}
DELETE /api/v1/cotacoes/{id}         → cotacao-service /api/v1/cotacoes/{id}
```

## 🏥 Status dos Serviços

### Verificar Saúde de Todos os Serviços

```bash
GET /api/status/services

Response 200:
{
  "gateway_status": "healthy",
  "services": {
    "animal": true,
    "pesagem": true,
    "cotacao": true
  },
  "all_healthy": true
}
```

### Resposta Quando Serviço Indisponível

```json
{
  "gateway_status": "healthy",
  "services": {
    "animal": false,
    "pesagem": true,
    "cotacao": true
  },
  "all_healthy": false
}
```

## 🔍 Exemplos de Uso

### Listar Todos os Animais

```bash
curl http://localhost:8080/api/v1/animais

# Equivalente a:
curl http://localhost:8000/api/v1/animais
```

### Criar Novo Animal

```bash
curl -X POST http://localhost:8080/api/v1/animais \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Bessie",
    "raca": "Nelore",
    "rfid": "RF001"
  }'
```

### Obter Pesagens do Animal

```bash
curl http://localhost:8080/api/v1/pesagens?animal_id=1
```

### Listar Cotações Recentes

```bash
curl http://localhost:8080/api/v1/cotacoes?limit=10
```

## 🏗️ Arquitetura do Proxy

### ProxyService (`app/services/__init__.py`)

Classe responsável por forwardar requisições:

```python
class ProxyService:
    @staticmethod
    async def forward_request(
        path: str,           # Caminho da requisição
        method: str,         # Método HTTP
        body: dict,          # Corpo JSON
        headers: dict,       # Headers HTTP
        service: str         # Serviço destino
    ) -> dict:
        """Roteia requisição e retorna resposta"""
```

**Features:**
- ✅ Suporte para todos os métodos HTTP (GET, POST, PUT, DELETE)
- ✅ Forwarding de headers (exceto host)
- ✅ Tratamento de erros (connection, timeout)
- ✅ Health check por serviço

### Tratamento de Erros

| Erro | Status | Descrição |
|------|--------|-----------|
| Connection Error | 503 | Serviço indisponível |
| Timeout | 504 | Serviço respondendo lentamente |
| Erro Genérico | 500 | Erro desconhecido |

## 🧪 Testes (45 Testes ✅)

### Estrutura de Testes

```
tests/
├── test_api.py              (11 testes)
├── test_auth.py             (13 testes)
├── test_config.py           (7 testes)
└── test_proxy.py            (14 testes) ← NOVO!
```

### Testes de Proxy

**ProxyService:**
- ✅ Forward request com sucesso
- ✅ Health check service disponível
- ✅ Health check service indisponível
- ✅ Health check serviço inválido
- ✅ Health check todos os serviços

**Error Handling:**
- ✅ Connection error (503)
- ✅ Timeout error (504)
- ✅ Generic error (500)
- ✅ Invalid service

**POST Requests:**
- ✅ Forward POST com body

**Proxy Routes:**
- ✅ Animals proxy route
- ✅ Pesagens proxy route
- ✅ Cotacoes proxy route

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# URLs dos Serviços
ANIMAL_SERVICE_URL=http://animal-service:8000
PESAGEM_SERVICE_URL=http://pesagem-service:8001
COTACAO_SERVICE_URL=http://cotacao-service:8002
```

### Docker Compose

```yaml
api-gateway:
  environment:
    - ANIMAL_SERVICE_URL=http://animal-service:8000
    - PESAGEM_SERVICE_URL=http://pesagem-service:8001
    - COTACAO_SERVICE_URL=http://cotacao-service:8002
```

## 📊 Performance

### Timeouts
- Connection timeout: 30 segundos
- Request timeout: 30 segundos

### Retry Policy
- Sem retry automático (pode ser adicionado)

## 🚀 Como Testar

### 1. Iniciar Stack Completa

```bash
make build
make up
```

### 2. Verificar Saúde dos Serviços

```bash
curl http://localhost:8080/api/status/services
```

### 3. Testar Roteamento

```bash
# Criar animal via gateway
curl -X POST http://localhost:8080/api/v1/animais \
  -H "Content-Type: application/json" \
  -d '{"nome":"Test","raca":"Nelore"}'

# Listar via gateway
curl http://localhost:8080/api/v1/animais

# Comparar com serviço direto
curl http://localhost:8000/api/v1/animais
```

### 4. Rodar Testes

```bash
cd services/api_gateway
pytest tests/test_proxy.py -v
```

## 🔐 Segurança

### Headers Removidos

Os seguintes headers NÃO são forwardados:
- `host` - Será o host do serviço backend

### Headers Preservados

- `authorization` - Tokens JWT
- `content-type` - Tipo do corpo
- `user-agent` - Informações do cliente
- Outros headers customizados

## 📈 Próximos Passos

1. **Autenticação JWT**: Validar token antes de rotear
   ```python
   @router.api_route("/api/v1/...")
   async def protected_route(authorization: str = Header()):
       if not validate_token(authorization):
           raise HTTPException(status_code=401)
   ```

2. **Rate Limiting**: Limitar requisições por IP
   ```python
   @limiter.limit("100/minute")
   async def proxy_route(...):
   ```

3. **Logging Centralizado**: Log de todas as requisições
   ```python
   logger.info(f"Proxy: {method} {path} → {service}")
   ```

4. **Circuit Breaker**: Detectar serviços fora
   ```python
   if consecutive_errors > 3:
       circuit_breaker.open()  # Não rotear mais
   ```

5. **Caching**: Cache de respostas GET
   ```python
   @cached(ttl=300)  # 5 minutos
   async def cached_request(path):
   ```

## 📚 Arquivos Modificados

- ✅ `app/services/__init__.py` - ProxyService
- ✅ `app/api/proxy.py` - Rotas de proxy
- ✅ `app/__init__.py` - Include proxy router
- ✅ `tests/test_proxy.py` - Testes de proxy
- ✅ `requirements.txt` - pytest-asyncio

## ✅ Checklist

- [x] ProxyService para forward de requisições
- [x] Rotas proxy para cada serviço
- [x] Health check por serviço
- [x] Tratamento de erros (503, 504, 500)
- [x] 14 testes de proxy
- [x] Documentação completa
- [ ] Autenticação JWT obrigatória (próximo)
- [ ] Rate limiting (próximo)
- [ ] Logging centralizado (próximo)
- [ ] Circuit breaker (próximo)
- [ ] Caching (próximo)

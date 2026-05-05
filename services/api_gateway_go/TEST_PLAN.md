# AgroVision API Gateway - Test Plan & Validation

## 📋 Visão Geral

Este documento descreve o plano completo de testes para validação do API Gateway Go da AgroVision, incluindo:
- **Testes Unitários (Go)** - Validação de componentes individuais
- **Testes E2E (End-to-End)** - Fluxos completos de requisição
- **Testes de Rate Limiting** - Validação de proteção contra abuso
- **Testes de Carga** - Performance e throughput
- **Testes de Integração** - Interação com serviços upstream

---

## 🎯 Objetivos de Teste

### Objetivos Funcionais
✅ Verificar roteamento correto de requisições  
✅ Validar tratamento de CORS  
✅ Confirmar implementação de rate limiting  
✅ Testar propagação de headers  
✅ Validar resposta em 404 e erros  

### Objetivos Não-Funcionais
✅ Performance: > 100 req/s  
✅ Latência p95: < 100ms  
✅ Disponibilidade: 99.9%  
✅ Throughput em carga sustentada  
✅ Comportamento sob concorrência  

---

## 🧪 Suite de Testes

### 1. Testes Unitários (Go)

**Arquivo**: `tests/integration_test.go`, `tests/router_test.go`, `tests/middleware_test.go`

**Testes**: 45+

**Cobertura**:
- Health check endpoint
- CORS headers
- Security headers
- Rate limiting logic
- Router configuration
- Middleware stack
- Concurrent requests
- Response formats

**Executar**:
```bash
# Todos os testes
go test ./tests -v

# Com coverage
go test ./tests -v -cover

# Teste específico
go test -run TestRateLimitExceeded -v

# Benchmarks
go test -bench=. -benchmem ./tests
```

**Resultado esperado**: ✅ 45/45 testes passando

---

### 2. Testes E2E (End-to-End)

**Arquivo**: `tests/e2e_tests.sh`

**Duração**: ~5 minutos

**Cobertura** (15 testes):

| ID | Teste | Validação |
|---|---|---|
| 1 | Health Check | GET /health retorna 200 |
| 2 | CORS Headers | Access-Control-Allow-Origin presente |
| 3 | Security Headers | X-Frame-Options, X-Content-Type-Options, etc |
| 4 | Roteamento | Requisições roteadas para endpoints corretos |
| 5 | 404 Handling | Rotas inválidas retornam 404 |
| 6 | CORS Preflight | OPTIONS requests retornam 204/200 |
| 7 | HTTP Methods | GET, POST, PUT, DELETE funcionam |
| 8 | Rate Limiting | Rate limit funciona após múltiplas requisições |
| 9 | Response Headers | Content-Type correto |
| 10 | Response Format | JSON válido e estruturado |
| 11 | Concorrência | 10 requisições simultâneas bem-sucedidas |
| 12 | Request Headers | Headers customizados são aceitos |
| 13 | Large Payloads | Payloads de 1MB são processadas |
| 14 | Slow Requests | Requisições lentas são tratadas |
| 15 | Error Responses | Formato correto de erro |

**Executar**:
```bash
# Iniciar serviços
docker-compose -f docker-compose.test.yml up -d

# Aguardar ~5 segundos para os serviços iniciarem
sleep 5

# Executar testes
bash tests/e2e_tests.sh
```

**Resultado esperado**: ✅ 15/15 testes passando

---

### 3. Testes de Rate Limiting

**Arquivo**: `tests/rate_limit_tests.sh`

**Duração**: ~2-3 minutos (configurável)

**Cenários** (6 testes):

| ID | Cenário | Validação |
|---|---|---|
| 1 | Taxa Constante | 100 req/min limit é respeitado |
| 2 | Recuperação | Após aguardar window, requisições são permitidas |
| 3 | Taxa Constante (20 req) | Padrão de requisições consistentes |
| 4 | Múltiplos IPs | Cada IP tem limite separado |
| 5 | Retry-After Header | Header presente quando rate-limited |
| 6 | Stress Test (30s) | Taxa constante sob carga sustentada |

**Configuração**:
- **Limite padrão**: 100 requisições por minuto
- **Janela**: 1 minuto (60 segundos)
- **Resposta 429**: Quando limite é atingido

**Executar**:
```bash
# Com valores padrão (100 req/min)
bash tests/rate_limit_tests.sh

# Com configuração customizada (50 req/30s)
bash tests/rate_limit_tests.sh 50 30
```

**Resultado esperado**:
- ✅ Taxa limiting funciona
- ✅ Requisições bloqueadas quando limite atingido
- ✅ Recuperação após expiração da janela
- ✅ Isolamento por IP

---

### 4. Testes de Carga (Load Testing)

**Arquivo**: `tests/load_tests.sh`

**Ferramenta**: Apache Bench (ab)

**Duração**: ~15-30 minutos (dependendo da opção)

**Cenários** (9 testes):

| ID | Teste | Descrição |
|---|---|---|
| 1 | Health Check Load | 100 req, 10 concorrentes |
| 2 | Routing Load | 50 req, 5 concorrentes |
| 3 | Escalada | 100 req em 1, 5, 10, 20 concorrentes |
| 4 | Long Duration | 500 req, 20 concorrentes |
| 5 | POST Load | POST com payload JSON |
| 6 | Timing Distribution | Análise de distribuição de latência |
| 7 | Different Endpoints | Teste todos endpoints principais |
| 8 | Sustained Load | 2000 req, 50 concorrentes (stress test) |
| 9 | Percentile Analysis | Análise de p95, p99 |

**Instalação de dependência**:
```bash
# Ubuntu/Debian
sudo apt-get install apache2-utils

# macOS
brew install httpd

# Ou usar Makefile
make install-deps
```

**Executar**:
```bash
# Menu interativo
bash tests/load_tests.sh

# Ou executar teste específico
# Exemplo: Health Check Load
ab -n 100 -c 10 http://localhost:8000/health
```

**Métricas importantes**:
```
Requests per second:    [valor] #/sec
Time per request:       [valor] ms
Failed requests:        [valor]
Longest request:        [valor] ms
```

**Resultado esperado**:
- ✅ Requests per second: > 100
- ✅ Time per request p95: < 100ms
- ✅ Failed requests: 0
- ✅ Zero timeout errors

---

## 🚀 Como Executar Testes

### Opção 1: Usando Makefile (Recomendado)

```bash
# Fazer build da imagem
make build-compose

# Iniciar todos os serviços
make up

# Opção A: Executar testes individuais
make test-go              # Testes Go
make test-e2e            # Testes E2E
make test-rate-limit     # Rate limiting
make test-load           # Load tests

# Opção B: Executar tudo de uma vez
make test-all
```

### Opção 2: Manualmente com Docker Compose

```bash
# 1. Iniciar serviços
docker-compose -f docker-compose.test.yml up -d

# 2. Aguardar inicialização
sleep 10

# 3. Executar testes
bash tests/e2e_tests.sh
bash tests/rate_limit_tests.sh
bash tests/load_tests.sh

# 4. Ver logs
docker-compose -f docker-compose.test.yml logs -f api_gateway

# 5. Parar serviços
docker-compose -f docker-compose.test.yml down
```

### Opção 3: Testes Locais (sem Docker)

```bash
# 1. Instalar dependências Go
go mod download

# 2. Executar gateway localmente
go run ./cmd/main/main.go

# 3. Em outro terminal, executar testes
bash tests/e2e_tests.sh
```

---

## 📊 Matriz de Testes

```
┌─────────────────────┬──────────┬──────────┬──────────┬──────────┐
│ Componente          │ Unitário │ E2E      │ Carga    │ Segurança│
├─────────────────────┼──────────┼──────────┼──────────┼──────────┤
│ Health Check        │ ✅       │ ✅       │ ✅       │ ✅       │
│ Roteamento          │ ✅       │ ✅       │ ✅       │ ✅       │
│ Rate Limiting       │ ✅       │ ✅       │ ✅       │ ✅       │
│ CORS                │ ✅       │ ✅       │ ✅       │ ✅       │
│ Security Headers    │ ✅       │ ✅       │ -        │ ✅       │
│ Error Handling      │ ✅       │ ✅       │ ✅       │ ✅       │
│ Concorrência        │ ✅       │ ✅       │ ✅       │ -        │
│ Response Format     │ ✅       │ ✅       │ -        │ -        │
└─────────────────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## ✅ Critérios de Aceitação

### Testes Go Unitários
- [ ] 45/45 testes devem passar
- [ ] Coverage >= 80%
- [ ] Zero panics
- [ ] Zero race conditions

### Testes E2E
- [ ] 15/15 testes devem passar
- [ ] Todos endpoints respondem
- [ ] Rate limiting ativo
- [ ] CORS configurado
- [ ] Headers de segurança presentes

### Testes de Rate Limiting
- [ ] Taxa limiting funciona (429 retornado)
- [ ] Recuperação após janela de expiração
- [ ] Isolamento por IP
- [ ] Retry-After header presente

### Testes de Carga
- [ ] Throughput >= 100 req/s
- [ ] Latência p95 < 100ms
- [ ] Zero erros sob carga sustentada
- [ ] Comportamento previsível com concorrência

---

## 🔍 Interpretação de Resultados

### Teste GO
```
ok      github.com/agrovision/api-gateway/tests    0.125s
PASS
```
✅ Todos os 45 testes passaram em 125ms

### Teste E2E
```
========================================
AgroVision E2E Test Suite
========================================
[PASS] 1. Health Check
[PASS] 2. CORS Headers
...
[PASS] 15. Error Response Format

Sucessos: 15
Falhas: 0
✅ TODOS OS TESTES PASSARAM!
```
✅ Todos os 15 testes passaram

### Teste Rate Limit
```
Rate limit atingido na requisição #105
Rate limited: 5 requisições
[PASS] Requisição bem-sucedida após recuperação
```
✅ Rate limiting funciona corretamente

### Teste Load
```
Requests per second:    245 #/sec
Time per request:       40.82 ms
Failed requests:        0
```
✅ Performance aceitável

---

## 🐛 Troubleshooting

### Problema: "Connection refused"
```bash
# Verificar se os serviços estão rodando
docker-compose -f docker-compose.test.yml ps

# Se não estão rodando:
docker-compose -f docker-compose.test.yml up -d
sleep 10
```

### Problema: "Apache Bench not found"
```bash
make install-deps
# ou
sudo apt-get install apache2-utils
```

### Problema: Rate limit tests falhando
```bash
# Verificar configuração de rate limit
grep RATE_LIMIT .env

# Resetar os dados de rate limiting (reiniciar o gateway)
docker-compose -f docker-compose.test.yml restart api_gateway
sleep 5
```

### Problema: "Port already in use"
```bash
# Parar containers que usam a porta
docker-compose -f docker-compose.test.yml down -v

# Ou usar porta diferente
docker run -p 8001:8000 agrovision/api-gateway:latest
```

---

## 📈 Performance Targets

| Métrica | Target | Aceitável | Crítico |
|---------|--------|-----------|---------|
| Throughput (req/s) | > 200 | > 100 | < 50 |
| Latência p50 (ms) | < 20 | < 50 | > 100 |
| Latência p95 (ms) | < 100 | < 150 | > 300 |
| Latência p99 (ms) | < 200 | < 300 | > 500 |
| Taxa de erro | 0% | < 0.1% | > 1% |
| Uptime | 99.9% | 99% | < 99% |

---

## 🔄 Ciclo de Teste Recomendado

### Fase 1: Desenvolvimento (Local)
```bash
make test-go              # Rodar após cada mudança
make quick-test          # Quick validation
```

### Fase 2: Validação (Docker)
```bash
make build-compose
make test-e2e            # Validar integração
```

### Fase 3: Teste de Performance (Staging)
```bash
make test-load           # Validar throughput e latência
make test-rate-limit     # Validar proteção
```

### Fase 4: Produção (Monitoring)
```bash
# Logs contínuos
make logs-all

# Health check periodic
make health-check

# Load testing ocasional
make test-load
```

---

## 📝 Logging e Diagnostics

### Ver logs do API Gateway
```bash
docker-compose -f docker-compose.test.yml logs -f api_gateway
```

### Ver logs de um serviço específico
```bash
docker-compose -f docker-compose.test.yml logs -f pesagem_service
```

### Coletar logs para debug
```bash
docker-compose -f docker-compose.test.yml logs > /tmp/test_logs.txt
```

---

## 🎓 Casos de Uso de Teste

### Caso 1: Validar Nova Feature
1. Escrever teste unitário
2. Implementar feature
3. Executar `make test-go`
4. Executar `make test-e2e`

### Caso 2: Validar Performance
1. Executar `make test-load` com load base
2. Fazer otimização
3. Executar novamente
4. Comparar resultados

### Caso 3: Validar Segurança
1. Executar `make test-e2e` (verifica headers)
2. Executar `make test-rate-limit` (verifica proteção)
3. Verificar logs para ataques potenciais

---

## 📞 Suporte e Issues

### Reportar problema de teste
1. Executar com flag `-v` (verbose)
2. Coletar logs: `docker-compose ... logs > logs.txt`
3. Incluir output do comando que falhou

### Exemplo de good bug report
```
## Problema: Rate limit test falhando

### Steps to reproduce:
1. docker-compose -f docker-compose.test.yml up -d
2. bash tests/rate_limit_tests.sh

### Esperado:
✅ 6/6 testes passando

### Obtido:
❌ Teste 3 falhando - taxa constante

### Logs:
[Cole relevantes]
```

---

## ✨ Conclusão

A suite de testes é abrangente e cobre:
- ✅ Funcionalidade core (roteamento, CORS)
- ✅ Proteção (rate limiting)
- ✅ Performance (throughput, latência)
- ✅ Confiabilidade (concorrência, recuperação)

**Status: Pronto para produção!**

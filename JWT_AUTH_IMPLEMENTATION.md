# JWT Authentication Implementation - Phase 6.1

## 📋 Overview

JWT (JSON Web Token) authentication middleware para proteger endpoints nos microserviços.

## 🔐 Middleware Implementado

### AuthMiddleware
- Valida JWT token obrigatório
- Extrai claims (user_id, email, role)
- Armazena em contexto do Gin
- Bloqueia requisição sem token

### OptionalAuthMiddleware
- Valida JWT token se presente
- Permite requisição sem token
- Útil para endpoints públicos/semi-públicos

### RoleMiddleware
- Verifica role do usuário
- Suporta múltiplos roles
- Nega acesso sem role correto

## 🎯 JWT Claims Structure

```json
{
  "user_id": "uuid-of-user",
  "email": "user@example.com",
  "role": "user|admin|analyst",
  "exp": 1234567890,
  "iat": 1234567800
}
```

## 🛣️ Rotas Protegidas (Vision Service)

### Público (sem auth)
- `GET /health`

### Opcional Auth
- `GET /vision/results/:id`
- `GET /vision/results`

### Protegido (JWT required)
- `POST /vision/detect` - Cria nova detecção
- `GET /vision/history` - Lista histórico
- `GET /vision/history/:id` - Obtém detecção
- `DELETE /vision/history/:id` - Deleta detecção
- `GET /vision/search?class=cow` - Busca por classe
- `GET /vision/statistics` - Estatísticas

## 🔑 Como Usar

### Com Bearer Token

```bash
curl -X GET http://localhost:8003/vision/history \
  -H "Authorization: Bearer eyJhbGc..."
```

### Sem Token (endpoints públicos)

```bash
curl -X GET http://localhost:8003/health
```

## 💾 JWT Secret Configuration

Via environment variable:

```bash
export JWT_SECRET="your-super-secret-key"
```

Default (não usar em produção):

```bash
JWT_SECRET="default-secret-key"
```

## 🚀 Frontend Integration

### AuthContext (já implementado)

```typescript
// JWT token é salvo automaticamente após login
localStorage.setItem("token", token);

// Interceptor de API adiciona header
apiService.defaults.headers.Authorization = `Bearer ${token}`;
```

### Detecção de Animais com Auth

```typescript
const result = await apiService.detectAnimals(formData);
// Erro 401 se token expirado → redireciona para login
```

## 🔄 Token Lifecycle

1. **Login** → Backend gera JWT com 24h expiration
2. **Armazenamento** → Frontend salva em localStorage
3. **Requisições** → Bearer token no header Authorization
4. **Expiração** → 401 Unauthorized
5. **Refresh** → Faz novo login (ou implementar refresh tokens)

## 🛡️ Best Practices

✅ **Implementado**:
- HMAC signature validation
- Expiration checks
- Role-based access control
- Claims extraction

❌ **TODO**:
- Implementar refresh tokens
- Rate limiting por usuário
- Token blacklist para logout
- Audit logging de acessos

## 📊 Services com JWT (Ordem)

1. ✅ **Vision Service** - Completo
2. ⏳ **ML Service** - Próximo
3. ⏳ **Animal Service** - Depois
4. ⏳ **Pesagem Service** - Depois
5. ⏳ **Cotacao Service** - Depois

## 🧪 Testing

### Sem Token

```bash
curl http://localhost:8003/vision/detect
# 401 Unauthorized: Missing authorization header
```

### Com Token Inválido

```bash
curl -H "Authorization: Bearer invalid" http://localhost:8003/vision/detect
# 401 Unauthorized: Invalid token
```

### Com Token Válido

```bash
curl -H "Authorization: Bearer <valid_jwt>" http://localhost:8003/vision/detect
# Sucesso! Processado com user_id do token
```

## 🔧 Troubleshooting

### Token Expirado
- Frontend: Redirecionar para login
- Backend: Retorna 401, frontend intercepta

### Token Inválido
- Verifique JWT_SECRET é igual no backend
- Verificar formato: `Bearer <token>`
- Token não pode ter espaços

### User ID not in context
- Middleware não foi aplicado à rota
- Token não contém user_id claim
- Middleware falhou silenciosamente

## 📚 Documentação

- JWT Spec: https://tools.ietf.org/html/rfc7519
- go-jwt: https://github.com/golang-jwt/jwt
- Gin Middleware: https://github.com/gin-gonic/gin

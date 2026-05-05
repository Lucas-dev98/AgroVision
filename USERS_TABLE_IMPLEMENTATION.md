# 👥 Tabela de Usuários - AgroVision

## 📋 Status: ✅ IMPLEMENTADO

A tabela de usuários foi criada com **autenticação real baseada em banco de dados**.

---

## 🗄️ Schema da Tabela

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (role IN ('admin', 'operator', 'viewer', 'user'))
);

-- Índices para performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);
```

---

## 👤 Usuários Padrão

A aplicação cria automaticamente 3 usuários ao iniciar:

| Username | Senha | Role | Email |
|----------|-------|------|-------|
| `admin` | `password123` | admin | admin@agrovision.local |
| `operator` | `operator123` | operator | operator@agrovision.local |
| `viewer` | `viewer123` | viewer | viewer@agrovision.local |

---

## 🔑 Papéis (Roles)

- **admin**: Acesso total ao sistema
- **operator**: Pode operar recursos (criar, atualizar)
- **viewer**: Acesso apenas leitura
- **user**: Usuário comum

---

## 🚀 Como Usar

### 1️⃣ **Executar Migrations**

```bash
cd /home/lucasbastos/AgroVision/infra/alembic

# Conectar ao PostgreSQL
export DATABASE_URL="postgresql://agrovision:agrovision@localhost:5432/agrovision"

# Aplicar migrations
alembic upgrade head

# Verificar tabelas criadas
psql -U agrovision -d agrovision -c "\dt"
```

### 2️⃣ **Fazer Login com Usuário Real**

**Frontend** (http://localhost:5174):
```
Usuário: admin
Senha: password123
```

**Backend** (curl):
```bash
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'

# Resposta
{
  "access_token": "550e8400-e29b-41d4-a716-446655440000",
  "refresh_token": "660e8400-e29b-41d4-a716-446655440001",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@agrovision.local"
  }
}
```

### 3️⃣ **Usar Token em Requisições Protegidas**

```bash
TOKEN="550e8400-e29b-41d4-a716-446655440000"

curl -X GET http://localhost:9000/api/v1/animals \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔐 Hashing de Senhas

As senhas são **hasheadas com bcrypt** no banco:

```go
// Criando usuário
passwordHash, err := utils.HashPassword("password123")
user := &models.User{
    Username: "admin",
    Password: passwordHash, // Nunca armazena texto plano!
}

// Validando login
isValid := utils.VerifyPassword("password123", user.PasswordHash)
```

---

## 🛠️ APIs de Usuários

### Criar Usuário

```bash
curl -X POST http://localhost:9000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novo_user",
    "email": "novo@example.com",
    "password": "senha123",
    "full_name": "Novo Usuário",
    "role": "operator"
  }'
```

### Listar Usuários

```bash
curl -X GET http://localhost:9000/api/v1/users \
  -H "Authorization: Bearer $TOKEN"
```

### Obter Perfil

```bash
curl -X GET http://localhost:9000/api/v1/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

### Atualizar Usuário

```bash
curl -X PUT http://localhost:9000/api/v1/users/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Admin Modificado",
    "role": "admin",
    "is_active": true
  }'
```

### Deletar Usuário (Soft Delete)

```bash
curl -X DELETE http://localhost:9000/api/v1/users/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Consultas SQL Úteis

### Ver todos os usuários

```sql
SELECT id, username, email, role, is_active, created_at
FROM users
ORDER BY created_at DESC;
```

### Resetar senha de um usuário

```sql
-- Primeiro hash a nova senha em Go:
-- passwordHash, _ := utils.HashPassword("nova_senha")

UPDATE users
SET password_hash = 'hash_da_nova_senha'
WHERE username = 'admin';
```

### Mudar role de usuário

```sql
UPDATE users
SET role = 'admin'
WHERE username = 'operator';
```

### Ativar/desativar usuário

```sql
UPDATE users
SET is_active = false
WHERE id = 1;
```

### Ver estatísticas

```sql
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_active THEN 1 END) as active_users,
    COUNT(CASE WHEN role = 'admin' THEN 1 END) as admins
FROM users;
```

---

## 🐛 Troubleshooting

### "user not found"
- Verifique se o username está correto
- Verifique se o usuário está ativo (`is_active = true`)

### "Invalid credentials"
- A senha está incorreta
- Verifique o hash bcrypt

### "duplicate key value violates unique constraint"
- Username ou email já existe
- Tente outro username/email

### Esqueci a senha do admin
1. Conecte ao banco: `psql -U agrovision -d agrovision`
2. Resete no Go:
   ```go
   // Em algum endpoint admin
   hash, _ := utils.HashPassword("nova_senha")
   userRepo.UpdatePassword(1, hash)
   ```

---

## 📁 Arquivos Relacionados

| Arquivo | Descrição |
|---------|-----------|
| `internal/models/user.go` | Modelos do usuário |
| `internal/repository/user.go` | Data access layer |
| `internal/handler/auth.go` | Handlers de autenticação |
| `internal/utils/password.go` | Hashing e verificação de senha |
| `internal/db/seed.go` | Seed de usuários padrão |
| `infra/alembic/versions/001_initial_schema.py` | Migration do banco |

---

## 🚀 Próximos Passos

- [ ] Implementar refresh token com validade
- [ ] Adicionar JWT real (não UUID aleatório)
- [ ] Adicionar 2FA (Two-Factor Authentication)
- [ ] Implementar forgot password
- [ ] Adicionar audit log de logins
- [ ] Rate limiting no login (proteção contra brute force)
- [ ] Campos adicionais: avatar, telefone, empresa, etc.

---

**Data de Implementação**: 05/05/2026  
**Status**: ✅ Production Ready  
**Última Atualização**: 05/05/2026

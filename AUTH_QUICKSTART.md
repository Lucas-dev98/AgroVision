# Guia Rápido de Autenticação - AgroVision

## 🚀 Quick Start

### 1. Integrar Rotas no index.tsx

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import AppRoutes from '@/routes/AppRoutes'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  </React.StrictMode>
)
```

### 2. Usar o Hook useAuth em Componentes

```tsx
import { useAuth } from '@auth'

export default function Dashboard() {
  const { isAuthenticated, user, logout } = useAuth()

  return (
    <div>
      {isAuthenticated && (
        <>
          <p>Bem-vindo, {user?.nome}</p>
          <button onClick={() => logout()}>Sair</button>
        </>
      )}
    </div>
  )
}
```

### 3. Criar Componentes Protegidos

```tsx
import PrivateRoute from '@/routes/AppRoutes'
import MyComponent from './MyComponent'

<Routes>
  <Route
    path="/my-page"
    element={
      <PrivateRoute>
        <MyComponent />
      </PrivateRoute>
    }
  />
</Routes>
```

## 📋 Funcionalidades

### AuthService

```typescript
// Login
await authService.login('12345678901234', 'senha123')

// Registro
await authService.register({
  nome: 'João Silva',
  cpf_cnpj: '12345678901234',
  email: 'joao@email.com',
  senha: 'senha123'
})

// Logout
await authService.logout(accessToken)

// Validação de token
const isValid = authService.isTokenValid(token)

// Renovar token
await authService.refreshToken(refreshToken)

// Recuperação de senha
await authService.forgotPassword('12345678901234')

// Reset de senha
await authService.resetPassword(resetToken, 'novaSenha123')
```

### useAuth Hook

```typescript
const {
  isAuthenticated,      // boolean - Usuário autenticado
  user,                 // AuthUser | null - Dados do usuário
  loading,              // boolean - Carregando
  error,                // string | null - Mensagem de erro
  login,                // Promise - Fazer login
  register,             // Promise - Registrar
  logout,               // Promise - Logout
  refreshAccessToken,   // Promise - Renovar token
  forgotPassword,       // Promise - Recuperar senha
  resetPassword,        // Promise - Redefinir senha
  clearError            // () => void - Limpar erro
} = useAuth()
```

## 🎨 Componentes

### LoginForm
Componente completo de login com:
- Validação de CPF/CNPJ
- Validação de campos obrigatórios
- Indicador de carregamento
- Mensagens de erro
- Links para cadastro e recuperação de senha

```tsx
import { LoginForm } from '@auth'

export default function LoginPage() {
  return <LoginForm />
}
```

### RegisterForm
Componente completo de cadastro com:
- Validação de todos os campos
- Validação de força de senha
- Confirmação de senha
- Indicador de carregamento
- Link para login

```tsx
import { RegisterForm } from '@auth'

export default function RegisterPage() {
  return <RegisterForm />
}
```

## 🧪 Testes

### Executar Todos os Testes
```bash
npm test
```

### Testes Específicos
```bash
# Testes de autenticação
npm test -- src/services/authService.test.ts

# Testes de login
npm test -- src/components/organisms/LoginForm.test.tsx

# Testes de cadastro
npm test -- src/components/organisms/RegisterForm.test.tsx

# Testes do hook
npm test -- src/hooks/useAuth.test.ts
```

### Coverage
```bash
npm test -- --coverage
```

## 🔒 Segurança

### Tokens Armazenados
- `access_token` - Token de curta duração (30 min)
- `refresh_token` - Token de longa duração (7 dias)

### Validações Implementadas
- CPF: 11 dígitos
- CNPJ: 14 dígitos
- Email: Formato válido
- Senha: Mínimo 8 caracteres
- Campos obrigatórios

### Headers de Requisição
Todas as requisições autenticadas incluem:
```
Authorization: Bearer {access_token}
```

## 📱 Endpoints da API

### Login
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "12345678901234",
  "password": "senha123"
}
```

### Registro
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "nome": "João Silva",
  "cpf_cnpj": "12345678901234",
  "email": "joao@email.com",
  "password": "senha123"
}
```

### Refresh Token
```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAi..."
}
```

### Logout
```
POST /api/v1/auth/logout
Authorization: Bearer {token}
```

## 🐛 Troubleshooting

### "Credenciais inválidas"
- Verificar se CPF/CNPJ está correto
- Verificar se senha está correta
- Certifique-se que o usuário existe

### "Token expirado"
- O hook `useAuth` tenta renovar automaticamente
- Se falhar, o usuário será redirecionado para login

### "Email já cadastrado"
- O email já foi registrado
- Use outro email ou faça login

## 📚 Estrutura de Arquivos

```
frontend/src/
├── services/
│   ├── authService.ts
│   └── authService.test.ts
├── components/
│   └── organisms/
│       ├── LoginForm.tsx
│       ├── LoginForm.test.tsx
│       ├── LoginForm.css
│       ├── RegisterForm.tsx
│       ├── RegisterForm.test.tsx
│       └── RegisterForm.css
├── hooks/
│   ├── useAuth.ts
│   └── useAuth.test.ts
├── routes/
│   └── AppRoutes.tsx
└── auth/
    └── index.ts
```

## 🔗 Referências

- [Documentação de Autenticação JWT](../docs/authentication.md)
- [Documentação de API](../docs/api.md)
- [Guia de Testes](../frontend/TESTING_GUIDE.md)

## 📞 Suporte

Para dúvidas ou problemas, consulte:
1. [IMPLEMENTATION_AUTH_TDD.md](../IMPLEMENTATION_AUTH_TDD.md) - Documentação completa
2. Testes unitários nos arquivos `.test.ts`
3. Comentários no código-fonte

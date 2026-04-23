# MFA (Multi-Factor Authentication) - Quick Start

## O que é MFA?

Multi-Factor Authentication é uma camada adicional de segurança que requer que o usuário forneça um código após fazer login com CPF/CNPJ e senha.

## Fluxo Rápido

1. **Login**: Usuário entra CPF/CNPJ e senha
2. **MFA Required**: Backend retorna `requires_mfa: true`
3. **Send Code**: Sistema envia código por email/SMS/app
4. **Verify**: Usuário insere código de 6 dígitos
5. **Access**: Sistema gera tokens finais e acessa dashboard

## Usando MFA

### Como usuário final:
```
1. Ir para /login
2. Digitar CPF/CNPJ: 12345678901234
3. Digitar Senha: SenhaForte123
4. Clicar "Entrar"
5. Aguardar email com código (ou SMS/app)
6. Digitar 6 dígitos do código
7. Será redirecionado ao dashboard
```

### Opções na tela MFA:
- **Reenviar código**: Envia novo código (máximo 3 vezes, a cada 60 segundos)
- **Usar outro método**: Volta ao login e permite escolher SMS ou email
- **Backspace**: Limpa campo anterior
- **Setas**: Navega entre campos

## Implementação (Para Desenvolvedor)

### 1. Importar componentes
```typescript
import { useMFA, MFAVerification } from '@auth'
```

### 2. Usar hook MFA em componente
```typescript
function MinhaComponente() {
  const mfa = useMFA()

  return (
    <>
      {mfa.mfaRequired ? (
        <MFAVerification
          sessionToken={mfa.sessionToken!}
          method={mfa.mfaMethod!}
          onSuccess={() => console.log('MFA success')}
        />
      ) : (
        <MinhaFormulaario />
      )}
    </>
  )
}
```

### 3. Requisitar MFA
```typescript
// Quando usuário fizer login
const response = await authService.login(cpf, senha)

if (response.requires_mfa) {
  // Requisitar código
  await mfa.requestMFA(response.user_id, 'email')
}
```

### 4. Verificar código
```typescript
// Quando usuário digitar código
const tokens = await mfa.verifyMFA('123456')
// Tokens estão em localStorage
```

## Métodos Disponíveis

### Hook useMFA

```typescript
const mfa = useMFA()

// Estado
mfa.mfaRequired        // boolean - MFA está ativo?
mfa.sessionToken       // string - Token da sessão MFA
mfa.mfaMethod         // 'email' | 'sms' | 'authenticator'
mfa.mfaLoading        // boolean - Operação em progresso?
mfa.mfaError          // string - Mensagem de erro

// Métodos
mfa.requestMFA(userId, method)    // Requisitar código
mfa.verifyMFA(code)               // Verificar código
mfa.resendMFA()                   // Reenviar código
mfa.clearMFA()                    // Limpar estado
```

### Componente MFAVerification

```typescript
<MFAVerification
  sessionToken="token123"
  method="email"
  email="user@example.com"
  phone="+5511987654321"
  onSuccess={(tokens) => { /* sucesso */ }}
  onChangeMethod={() => { /* trocar método */ }}
/>
```

## Backend Integration

### Endpoints necessários

```
POST /api/v1/auth/login
- Input: {username, password}
- Output com MFA: {requires_mfa: true, session_token, ...}

POST /api/v1/auth/mfa/send
- Input: {user_id, method}
- Output: {session_token, method, message}

POST /api/v1/auth/mfa/verify
- Input: {session_token, code}
- Output: {access_token, refresh_token, token_type}

POST /api/v1/auth/mfa/resend
- Input: {session_token}
- Output: {message}
```

## Testes

### Rodar testes de MFA

```bash
# Testes do AuthService
npm test -- src/services/authService.test.ts

# Testes do componente
npm test -- src/components/organisms/MFAVerification.test.tsx

# Testes do hook
npm test -- src/hooks/useMFA.test.ts

# Testes integrados
npm test -- src/components/organisms/LoginForm.mfa.test.tsx

# Testes backend
pytest services/api_gateway/tests/test_mfa_endpoints.py
```

## Troubleshooting

### "Código MFA inválido"
- Verificar se código tem 6 dígitos
- Verificar se código não expirou (válido por 10 minutos)
- Tentar "Reenviar código"

### "Session expirada"
- MFA session é válida por 10 minutos
- Comece novo login

### "Muitas tentativas"
- Limite: 5 tentativas em 10 minutos
- Aguarde 10 minutos ou comece novo login
- Ou clique "Reenviar código"

### Email não chega
- Verificar pasta de spam
- Aguardar 60 segundos
- Clicar "Reenviar código" (máximo 3 vezes)

## Segurança

- ✅ Código válido por 10 minutos
- ✅ Session token válida por 10 minutos
- ✅ Máximo 5 tentativas de código por 10 minutos
- ✅ Máximo 3 reenvios por 5 minutos
- ✅ Rate limiting por IP
- ✅ Nunca armazenar código no cliente
- ✅ Session token é JWT com assinatura

## FAQ

**P: Como desabilitar MFA?**
A: No backend, em `/auth/login`, set `requires_mfa = false`

**P: Como forçar MFA para todos?**
A: No backend, em `/auth/login`, sempre set `requires_mfa = true`

**P: Suporta TOTP (Google Authenticator)?**
A: Sim! Use `method: 'authenticator'` em `requestMFA()`

**P: Posso usar MFA em outras rotas?**
A: Sim! Importe `useMFA` e `MFAVerification` em qualquer componente

**P: Como resetar MFA de um usuário?**
A: No admin panel (ainda não implementado), ou via backend direto

## Próximas Features

- [ ] Backup codes para MFA
- [ ] Trusted devices (30 dias)
- [ ] Setup de MFA na conta do usuário
- [ ] Admin dashboard para MFA
- [ ] Verificação de força de MFA

## Referências

- [IMPLEMENTATION_MFA_TDD.md](./IMPLEMENTATION_MFA_TDD.md) - Documentação técnica completa
- [RFC 4226 HOTP](https://datatracker.ietf.org/doc/html/rfc4226)
- [RFC 6238 TOTP](https://datatracker.ietf.org/doc/html/rfc6238)

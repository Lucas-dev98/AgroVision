# Implementação MFA (Multi-Factor Authentication) - TDD

## Visão Geral

Este documento descreve a implementação completa de autenticação multi-fator (MFA) no fluxo de login do AgroVision, seguindo metodologia TDD (Test-Driven Development).

## Arquitetura MFA

### Fluxo de Login com MFA

```
1. Usuário digita CPF/CNPJ e Senha
   ↓
2. LoginForm valida campos
   ↓
3. AuthService.login() enviado para backend
   ↓
4. Backend valida credenciais
   ├─ Se inválido: Erro 401
   └─ Se válido com MFA: {requires_mfa: true, session_token, mfa_methods, ...}
   ↓
5. LoginForm detecta requires_mfa=true
   ↓
6. Chama useMFA.requestMFA(userId, method)
   ↓
7. AuthService.requestMFA() envia POST /auth/mfa/send
   ↓
8. Backend gera código e envia por email/SMS
   ↓
9. MFAVerification component renderiza (tela de 6 dígitos)
   ↓
10. Usuário digita código
   ↓
11. MFAVerification chama verifyMFA(sessionToken, code)
   ↓
12. AuthService.verifyMFA() envia POST /auth/mfa/verify
   ↓
13. Backend valida código
   ├─ Se inválido: Erro 400
   └─ Se válido: {access_token, refresh_token}
   ↓
14. Tokens armazenados em localStorage
   ↓
15. Navegar para dashboard
```

## Componentes Implementados

### 1. AuthService - Métodos MFA

**Arquivo:** `src/services/authService.ts`

#### `requestMFA(userId: string, method: 'email' | 'sms' | 'authenticator')`
- Requisita envio de código MFA
- Retorna: `{session_token, method, message}`
- Endpoint: `POST /auth/mfa/send`

#### `verifyMFA(sessionToken: string, code: string)`
- Verifica código MFA
- Retorna: `{access_token, refresh_token, token_type}`
- Armazena tokens em localStorage
- Endpoint: `POST /auth/mfa/verify`

#### `resendMFACode(sessionToken: string)`
- Reenvia código MFA
- Retorna: `{message}`
- Endpoint: `POST /auth/mfa/resend`
- Rate limit: máximo 3 reenvios por 5 minutos

#### `login() - Modificação**
- Retorna agora: `LoginResponse | LoginResponseWithMFA`
- Se MFA necessário: `{requires_mfa: true, session_token, user_id, mfa_methods, email, phone}`
- Se sem MFA: `{access_token, refresh_token, token_type}`

### 2. Hook useMFA

**Arquivo:** `src/hooks/useMFA.ts`

```typescript
interface MFAState {
  mfaRequired: boolean
  sessionToken: string | null
  mfaMethod: 'email' | 'sms' | 'authenticator' | null
  mfaLoading: boolean
  mfaError: string | null
}

// Métodos
requestMFA(userId, method)    // Requisitar código
verifyMFA(code)                // Verificar código
resendMFA()                    // Reenviar código
clearMFA()                     // Limpar estado MFA
setMFAState(state)             // Atualizar estado
```

### 3. Componente MFAVerification

**Arquivo:** `src/components/organisms/MFAVerification.tsx`

**Features:**
- 6 campos de entrada para dígitos
- Auto-focus entre campos
- Navegação com setas (←→)
- Backspace para voltar
- Validação de formato (apenas dígitos)
- Timer de reenvio (60s)
- Opção "Reenviar código"
- Opção "Usar outro método"
- Mascaramento de email/telefone
- Loading state
- Error display

**Props:**
```typescript
interface MFAVerificationProps {
  sessionToken: string
  method: 'email' | 'sms' | 'authenticator'
  email?: string
  phone?: string
  onSuccess: (tokens) => void
  onChangeMethod?: () => void
}
```

### 4. LoginForm - Integração MFA

**Arquivo:** `src/components/organisms/LoginForm.tsx`

**Mudanças:**
- Importa `useMFA` hook
- Importa `MFAVerification` component
- No handleSubmit: detecta `requires_mfa` na resposta
- Se MFA necessário: chama `mfa.requestMFA()`
- Renderiza `MFAVerification` quando `mfa.mfaRequired === true`
- Button "Usar outro método" limpa MFA e volta ao login
- handleMFASuccess navega para dashboard

## Backend Endpoints

### 1. POST /auth/mfa/send

**Request:**
```json
{
  "user_id": 1,
  "method": "email"
}
```

**Response (200):**
```json
{
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "method": "email",
  "message": "Código enviado para seu email"
}
```

**Errors:**
- 400: Método inválido ou usuário não tem este método configurado
- 404: Usuário não encontrado
- 401: Não autenticado

### 2. POST /auth/mfa/verify

**Request:**
```json
{
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "code": "123456"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Errors:**
- 400: Código inválido ou formato incorreto
- 401: Session expirada ou inválida
- 429: Muitas tentativas (máximo 5 por 10 minutos)

### 3. POST /auth/mfa/resend

**Request:**
```json
{
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "message": "Código reenviado com sucesso"
}
```

**Errors:**
- 401: Session inválida
- 429: Rate limit (máximo 3 reenvios por 5 minutos)

### 4. POST /auth/login - Modificação

**Response com MFA (200):**
```json
{
  "requires_mfa": true,
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "mfa_methods": ["email", "sms"],
  "email": "usuario@example.com",
  "phone": "+55 (11) 98765-4321"
}
```

**Response sem MFA (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Testes Implementados

### Frontend Tests

#### authService.test.ts
- ✅ `verifyMFA` com código válido
- ✅ `verifyMFA` com código inválido
- ✅ `verifyMFA` com session expirada
- ✅ `verifyMFA` armazena tokens em localStorage
- ✅ `resendMFACode` com sucesso
- ✅ `resendMFACode` com session inválida
- ✅ `resendMFACode` rate limit
- ✅ `requestMFA` com diferentes métodos
- ✅ Login retorna MFA required
- ✅ Login retorna tokens diretos

#### MFAVerification.test.tsx
- ✅ Renderiza formulário de verificação
- ✅ Aceita entrada de 6 dígitos
- ✅ Valida todos os dígitos inseridos
- ✅ Chama authService.verifyMFA com código correto
- ✅ Exibe erro quando código é inválido
- ✅ Mostra spinner durante verificação
- ✅ Permite reenvio de código
- ✅ Exibe email/telefone mascarado
- ✅ Opção de trocar método
- ✅ Limpa erro ao inserir novo código
- ✅ Auto-focus entre campos
- ✅ Navegação com backspace
- ✅ Timer de reenvio

#### useMFA.test.ts
- ✅ Inicializa com estado correto
- ✅ Requisita MFA com sucesso
- ✅ Exibe erro ao requisitar MFA
- ✅ Verifica código MFA com sucesso
- ✅ Exibe erro ao verificar código inválido
- ✅ Reenvia código MFA
- ✅ Limpa estado MFA
- ✅ Suporta diferentes métodos
- ✅ Exibe loading durante operações

#### LoginForm.mfa.test.tsx
- ✅ Renderiza formulário normalmente
- ✅ Requisita MFA após login bem-sucedido
- ✅ Mostra tela de MFA quando necessário
- ✅ Volta para login se clicar em "voltar"
- ✅ Navega para dashboard após MFA bem-sucedido
- ✅ Exibe erro quando MFA falha
- ✅ Mostra loading enquanto processa MFA
- ✅ Permite trocar método de MFA
- ✅ Desabilita login form enquanto MFA está ativo

### Backend Tests

#### test_mfa_endpoints.py
- ✅ Enviar código MFA por email
- ✅ Enviar código MFA por SMS
- ✅ Preparar verificação com authenticator
- ✅ Rejeitar método MFA inválido
- ✅ Erro quando usuário não existe
- ✅ Requer autenticação
- ✅ Verificar código MFA válido
- ✅ Rejeitar código inválido
- ✅ Rejeitar session expirada
- ✅ Validar campos obrigatórios
- ✅ Validar formato do código (6 dígitos)
- ✅ Reenviar código com sucesso
- ✅ Rejeitar reenvio com session inválida
- ✅ Limitar tentativas de reenvio
- ✅ Limitar tentativas de verificação
- ✅ Retornar formato correto
- ✅ Gerar session tokens únicos

## Fluxos de Uso

### Caso 1: Login Bem-Sucedido com MFA (Email)

```typescript
// 1. Usuário entra CPF/CNPJ e senha
// 2. LoginForm submete
const response = await authService.login('12345678901234', 'senha123')
// Response: {requires_mfa: true, session_token: '...', ...}

// 3. LoginForm detecta MFA necessário
await mfa.requestMFA(response.user_id, 'email')

// 4. Backend envia email com código
// 5. Usuário digita código na MFAVerification
// 6. MFAVerification submete
const tokens = await authService.verifyMFA(sessionToken, '123456')
// Response: {access_token: '...', refresh_token: '...'}

// 7. Navega para dashboard
navigate('/dashboard')
```

### Caso 2: Mudança de Método MFA

```typescript
// Usuário clica "Usar outro método"
mfa.clearMFA()  // Limpa estado MFA

// Volta ao formulário de login
// Pode reenviar código ou tentar com novo método

// Requisitar novo método
await mfa.requestMFA(userId, 'sms')
```

### Caso 3: Reenviar Código

```typescript
// Usuário não recebeu código
// Clica "Reenviar código" (após 60s)

await authService.resendMFACode(sessionToken)
// Novo código é enviado
```

## Segurança

### Session Token
- JWT com expiration de 10 minutos
- Válido apenas para o fluxo MFA específico
- Contém user_id e método de MFA

### Código MFA
- 6 dígitos aleatórios
- Válido por 10 minutos
- Máximo 5 tentativas por 10 minutos
- Inválida após 3 reenvios

### Rate Limiting
- Reenvio: máximo 3 por 5 minutos
- Verificação: máximo 5 tentativas por 10 minutos
- IP-based tracking

### Armazenamento
- Session token: transmitido em cada requisição MFA
- Tokens finais: armazenados em localStorage
- Nunca armazenar código MFA no cliente

## Próximas Melhorias

1. **2FA com Authenticator App**
   - QR code para escanear
   - Suporte a TOTP (Time-based One-Time Password)

2. **Trusted Devices**
   - Opção "Lembrar deste dispositivo"
   - Skip MFA para dispositivos confiáveis (30 dias)

3. **Backup Codes**
   - Gerar códigos de backup durante setup
   - Usar para casos de perda do device

4. **MFA Obrigatório**
   - Forçar setup de MFA ao primeiro login
   - Admin pode forçar para todos os usuários

5. **Analytics**
   - Log de tentativas de login
   - Dashboard de atividades de segurança

## Troubleshooting

### Código inválido
- Verifique o time no servidor
- Verifique se código não expirou (10 minutos)
- Clique "Reenviar código" se não recebeu

### Session expirada
- Código MFA válido por apenas 10 minutos
- Comece novo login

### Muitas tentativas
- Rate limit: máximo 5 tentativas por 10 minutos
- Aguarde 10 minutos ou comece novo login

### Email não recebido
- Verificar spam
- Clique "Reenviar código" (após 60s)
- Máximo 3 reenvios

## Referências

- [RFC 4226 - HOTP](https://datatracker.ietf.org/doc/html/rfc4226)
- [RFC 6238 - TOTP](https://datatracker.ietf.org/doc/html/rfc6238)
- [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html)

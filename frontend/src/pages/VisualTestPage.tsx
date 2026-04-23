import React from 'react'
import LoginForm from '@components/organisms/LoginForm'
import ForgotPasswordForm from '@components/organisms/ForgotPasswordForm'
import ResetPasswordForm from '@components/organisms/ResetPasswordForm'

/**
 * Página de teste visual dos formulários de autenticação
 * Permite visualizar os formulários sem estar autenticado
 */
const VisualTestPage: React.FC = () => {
  const [currentTab, setCurrentTab] = React.useState<'login' | 'forgot' | 'reset'>('login')

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <h1>Testes Visuais - Fluxo de Autenticação</h1>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <button
            onClick={() => setCurrentTab('login')}
            style={{
              padding: '10px 20px',
              backgroundColor: currentTab === 'login' ? '#4CAF50' : '#ccc',
              color: currentTab === 'login' ? 'white' : 'black',
              border: 'none',
              cursor: 'pointer',
              borderRadius: '4px',
            }}
          >
            Teste Login
          </button>
          <button
            onClick={() => setCurrentTab('forgot')}
            style={{
              padding: '10px 20px',
              backgroundColor: currentTab === 'forgot' ? '#4CAF50' : '#ccc',
              color: currentTab === 'forgot' ? 'white' : 'black',
              border: 'none',
              cursor: 'pointer',
              borderRadius: '4px',
            }}
          >
            Teste Esqueci Senha
          </button>
          <button
            onClick={() => setCurrentTab('reset')}
            style={{
              padding: '10px 20px',
              backgroundColor: currentTab === 'reset' ? '#4CAF50' : '#ccc',
              color: currentTab === 'reset' ? 'white' : 'black',
              border: 'none',
              cursor: 'pointer',
              borderRadius: '4px',
            }}
          >
            Teste Reset Senha
          </button>
        </div>
      </div>

      <div style={{
        maxWidth: '500px',
        margin: '0 auto',
        padding: '20px',
        border: '1px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#f9f9f9',
      }}>
        {currentTab === 'login' && <LoginForm />}
        {currentTab === 'forgot' && <ForgotPasswordForm />}
        {currentTab === 'reset' && <ResetPasswordForm />}
      </div>

      <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
        <h2>Instruções de Teste</h2>
        <p><strong>Test User:</strong></p>
        <ul>
          <li>CPF/CNPJ: <code>12345678901234</code></li>
          <li>Email: <code>reset@example.com</code></li>
            <li>Senha: <code>Senha123!</code></li>
          </ul>
          
          <p><strong>Teste de Login:</strong></p>
          <ol>
            <li>Insira o CPF: 12345678901234</li>
            <li>Insira a senha: Senha123!</li>
            <li>Clique em Login</li>
            <li>Esperado: Sucesso e redirecionamento para dashboard</li>
          </ol>

          <p><strong>Teste de Esqueci Senha:</strong></p>
          <ol>
            <li>Insira o CPF/CNPJ: 12345678901234</li>
            <li>Clique em Solicitar Redefinição</li>
            <li>Esperado: Mensagem de sucesso com email mascarado (r****@example.com)</li>
          </ol>

          <p><strong>Teste de Reset Senha:</strong></p>
          <ol>
            <li>Um token é gerado automaticamente no backend (válido por 1 hora)</li>
            <li>Insira a nova senha (mín. 8 caracteres, com letra maiúscula e número)</li>
            <li>Exemplo: <code>NovaSenha123!</code></li>
            <li>Esperado: Sucesso e redirecionamento para login</li>
          </ol>
        </div>
      </div>
  )
}

export default VisualTestPage

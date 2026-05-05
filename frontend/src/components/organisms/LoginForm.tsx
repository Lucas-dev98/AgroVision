import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import authService from '@services/authService'
import useMFA from '@hooks/useMFA'
import Button from '@components/atoms/Button'
import Input from '@components/atoms/Input'
import MFAVerification from './MFAVerification'
import logoImg from '@/assets/agrovision-logo.jpg'
import './LoginForm.css'

interface FormErrors {
  cpf_cnpj?: string
  password?: string
  general?: string
}

const LoginForm: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [cpfCnpj, setCpfCnpj] = useState('')
  const [password, setPassword] = useState('')
  const [userEmail, setUserEmail] = useState<string | undefined>()
  const [userPhone, setUserPhone] = useState<string | undefined>()

  // Hook de MFA
  const mfa = useMFA()

  /**
   * Validar CPF/CNPJ
   */
  const validateCpfCnpj = (value: string): boolean => {
    // Remover caracteres não numéricos
    const cleaned = value.replace(/\D/g, '')

    // CPF tem 11 dígitos, CNPJ tem 14
    return cleaned.length === 11 || cleaned.length === 14
  }

  /**
   * Validar formulário
   */
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!cpfCnpj.trim()) {
      newErrors.cpf_cnpj = 'CPF/CNPJ é obrigatório'
    } else if (!validateCpfCnpj(cpfCnpj)) {
      newErrors.cpf_cnpj = 'CPF/CNPJ deve ter 11 ou 14 dígitos'
    }

    if (!password.trim()) {
      newErrors.password = 'Senha é obrigatória'
    } else if (password.length < 6) {
      newErrors.password = 'Senha deve ter no mínimo 6 caracteres'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  /**
   * Limpar erros quando usuário começa a digitar
   */
  const handleInputChange = (field: 'cpf_cnpj' | 'password', value: string) => {
    if (field === 'cpf_cnpj') {
      setCpfCnpj(value)
    } else {
      setPassword(value)
    }

    // Remover erro do campo que o usuário está digitando
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined,
      }))
    }

    // Remover erro geral se houver
    if (errors.general) {
      setErrors(prev => ({
        ...prev,
        general: undefined,
      }))
    }
  }

  /**
   * Lidar com submissão do formulário
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      // Tentar fazer login
      const response = await authService.login(cpfCnpj, password)

      // Verificar se MFA é necessário
      if (response.requires_mfa) {
        // MFA necessário - requisitar código
        setUserEmail(response.email)
        setUserPhone(response.phone)

        // Requisitar MFA (padrão: email)
        const mfaMethod = (response.mfa_methods?.[0] || 'email') as
          | 'email'
          | 'sms'
          | 'authenticator'

        await mfa.requestMFA(response.user_id, mfaMethod)
      } else {
        // Login bem-sucedido sem MFA
        navigate('/dashboard')
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Erro desconhecido'
      setErrors(prev => ({
        ...prev,
        general: message,
      }))
    } finally {
      setLoading(false)
    }
  }

  /**
   * Lidar com sucesso de MFA
   */
  const handleMFASuccess = () => {
    // Navegar para dashboard após MFA bem-sucedido
    navigate('/dashboard')
  }

  /**
   * Voltar de MFA para login
   */
  const handleBackToLogin = () => {
    mfa.clearMFA()
    setErrors({})
    setCpfCnpj('')
    setPassword('')
  }

  // Se MFA é necessário, mostrar tela de verificação
  if (mfa.mfaRequired && mfa.sessionToken) {
    return (
      <MFAVerification
        sessionToken={mfa.sessionToken}
        method={mfa.mfaMethod || 'email'}
        email={userEmail}
        phone={userPhone}
        onSuccess={handleMFASuccess}
        onChangeMethod={handleBackToLogin}
      />
    )
  }

  return (
    <div className="login-form-container">
      <div className="login-form-card">
        <div className="login-form__header">
          <img 
            src={logoImg} 
            alt="AgroVision Logo" 
            className="login-form__logo"
          />
          <h1>LOGIN</h1>
        </div>

        {errors.general && (
          <div className="login-form__error-banner" role="alert">
            {errors.general}
          </div>
        )}

        {mfa.mfaError && (
          <div className="login-form__error-banner" role="alert">
            {mfa.mfaError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-form__field">
            <label htmlFor="cpf_cnpj" className="login-form__label">
              CPF/CNPJ
            </label>
            <Input
              id="cpf_cnpj"
              type="text"
              placeholder="Ex: 123.456.789-01"
              value={cpfCnpj}
              onChange={e => handleInputChange('cpf_cnpj', e.target.value)}
              error={errors.cpf_cnpj}
              disabled={loading || mfa.mfaLoading}
            />
          </div>

          <div className="login-form__field">
            <label htmlFor="password" className="login-form__label">
              Senha
            </label>
            <Input
              id="password"
              type="password"
              placeholder="Digite sua senha"
              value={password}
              onChange={e => handleInputChange('password', e.target.value)}
              error={errors.password}
              disabled={loading || mfa.mfaLoading}
            />
          </div>

          <div className="login-form__forgot-password">
            <Link to="/esqueci-senha">Esqueci minha senha</Link>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={loading || mfa.mfaLoading}
            fullWidth
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </Button>
        </form>

        <div className="login-form__footer">
          <p>
            Não tem uma conta?{' '}
            <Link to="/cadastro" className="login-form__signup-link">
              Cadastre-se
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginForm

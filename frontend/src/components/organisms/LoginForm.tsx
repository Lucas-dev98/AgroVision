import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '@context/AuthContext'
import Button from '@components/atoms/Button'
import Input from '@components/atoms/Input'
import logoImg from '@/assets/agrovision-logo.jpg'
import './LoginForm.css'

interface FormErrors {
  cpf_cnpj?: string
  password?: string
  general?: string
}

const LoginForm: React.FC = () => {
  const navigate = useNavigate()
  const { login: authLogin } = useAuth()
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [cpfCnpj, setCpfCnpj] = useState('')
  const [password, setPassword] = useState('')

  /**
   * Validar identificador de acesso
   */
  const validateUsername = (value: string): boolean => {
    return value.trim().length >= 3
  }

  /**
   * Validar formulário
   */
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!cpfCnpj.trim()) {
      newErrors.cpf_cnpj = 'Usuário é obrigatório'
    } else if (!validateUsername(cpfCnpj)) {
      newErrors.cpf_cnpj = 'Usuário deve ter ao menos 3 caracteres'
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
      await authLogin(cpfCnpj, password)
      navigate('/dashboard')
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

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-form__field">
            <label htmlFor="cpf_cnpj" className="login-form__label">
              Usuário
            </label>
            <Input
              id="cpf_cnpj"
              type="text"
              placeholder="Ex: admin ou 123.456.789-01"
              value={cpfCnpj}
              onChange={e => handleInputChange('cpf_cnpj', e.target.value)}
              error={errors.cpf_cnpj}
              disabled={loading}
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
              disabled={loading}
            />
          </div>

          <div className="login-form__forgot-password">
            <Link to="/esqueci-senha">Esqueci minha senha</Link>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={loading}
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

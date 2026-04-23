import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import authService from '@services/authService'
import Button from '@components/atoms/Button'
import Input from '@components/atoms/Input'
import logoImg from '@/assets/agrovision-logo.jpg'
import './ForgotPasswordForm.css'

interface FormErrors {
  cpf_email?: string
  general?: string
}

const ForgotPasswordForm: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [cpfEmail, setCpfEmail] = useState('')
  const [success, setSuccess] = useState(false)

  /**
   * Validar CPF/CNPJ/Email
   */
  const validateCpfEmailCnpj = (value: string): boolean => {
    // Se contém @ é email
    if (value.includes('@')) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value)
    }

    // Remover caracteres não numéricos
    const cleaned = value.replace(/\D/g, '')

    // Se não tem @, deve ter apenas dígitos e ter 11 ou 14
    if (cleaned.length !== 11 && cleaned.length !== 14) {
      return false
    }

    // Se tem caracteres não numéricos (além de separadores), não é válido
    const hasNonNumericCharacters = /[^\d.\-\/]/.test(value)
    if (hasNonNumericCharacters) {
      return false
    }

    return true
  }

  /**
   * Validar formulário
   */
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!cpfEmail.trim()) {
      newErrors.cpf_email = 'Campo obrigatório'
    } else if (!validateCpfEmailCnpj(cpfEmail)) {
      if (cpfEmail.includes('@')) {
        newErrors.cpf_email = 'Email inválido'
      } else {
        const cleaned = cpfEmail.replace(/\D/g, '')
        if (cleaned.length === 0) {
          newErrors.cpf_email = 'CPF/CNPJ deve ter 11 ou 14 dígitos'
        } else if (cleaned.length < 11) {
          newErrors.cpf_email = 'CPF/CNPJ deve ter 11 ou 14 dígitos'
        } else if (cleaned.length > 11 && cleaned.length < 14) {
          newErrors.cpf_email = 'CPF/CNPJ deve ter 11 ou 14 dígitos'
        } else {
          newErrors.cpf_email = 'CPF/CNPJ inválido'
        }
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  /**
   * Limpar erros quando usuário começa a digitar
   */
  const handleInputChange = (value: string) => {
    setCpfEmail(value)

    // Remover erro do campo que o usuário está digitando
    if (errors.cpf_email) {
      setErrors(prev => ({
        ...prev,
        cpf_email: undefined,
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
    setSuccess(false)

    try {
      // Se for email, passa como email; caso contrário como cpf_cnpj
      await authService.forgotPassword(cpfEmail)

      setSuccess(true)
      setCpfEmail('')

      // Mostrar mensagem de sucesso por 5 segundos antes de redirecionar
      setTimeout(() => {
        navigate('/login')
      }, 3000)
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

  if (success) {
    return (
      <div className="forgot-password-container">
        <div className="forgot-password-card">
          <div className="forgot-password-success">
            <div className="success-icon">✓</div>
            <h2>Email de Recuperação Enviado!</h2>
            <p>
              Verifique seu email para obter as instruções de redefinição de
              senha.
            </p>
            <p className="success-note">
              Se não receber em 5 minutos, verifique sua pasta de spam.
            </p>
            <Button
              variant="primary"
              fullWidth
              onClick={() => navigate('/login')}
              className="forgot-password-button"
            >
              Voltar ao Login
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="forgot-password-container">
      <div className="forgot-password-card">
        <div className="forgot-password__header">
          <img 
            src={logoImg} 
            alt="AgroVision Logo" 
            className="forgot-password__logo"
          />
          <h1>ESQUECI MINHA SENHA</h1>
          <p className="forgot-password__subtitle">
            Insira seu CPF/CNPJ ou email para receber instruções de recuperação
          </p>
        </div>

        {errors.general && (
          <div className="forgot-password__error-banner" role="alert">
            {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="forgot-password-form">
          <div className="forgot-password__field">
            <label htmlFor="cpf_email" className="forgot-password__label">
              CPF/CNPJ ou Email
            </label>
            <Input
              id="cpf_email"
              type="text"
              placeholder="Ex: 123.456.789-01 ou usuario@email.com"
              value={cpfEmail}
              onChange={e => handleInputChange(e.target.value)}
              error={errors.cpf_email}
              disabled={loading}
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={loading}
            fullWidth
          >
            {loading ? 'Enviando...' : 'Enviar'}
          </Button>
        </form>

        <div className="forgot-password__footer">
          <p>
            <Link to="/login" className="forgot-password__link">
              Voltar ao login
            </Link>
          </p>
          <p>
            Não tem uma conta?{' '}
            <Link to="/cadastro" className="forgot-password__link">
              Cadastre-se
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default ForgotPasswordForm

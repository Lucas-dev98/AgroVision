import React, { useState, useEffect } from 'react'
import { useNavigate, Link, useSearchParams } from 'react-router-dom'
import authService from '@services/authService'
import Button from '@components/atoms/Button'
import Input from '@components/atoms/Input'
import './ResetPasswordForm.css'

interface FormErrors {
  password?: string
  confirmPassword?: string
  general?: string
}

/**
 * Calcular força da senha
 * 0 = Nenhuma, 1 = Fraca, 2 = Média, 3 = Forte
 */
const calculatePasswordStrength = (password: string): number => {
  if (!password) return 0

  let strength = 0

  // Tamanho
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++

  // Tipos de caracteres
  const hasLowercase = /[a-z]/.test(password)
  const hasUppercase = /[A-Z]/.test(password)
  const hasNumbers = /\d/.test(password)
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)

  const typesCount = [
    hasLowercase,
    hasUppercase,
    hasNumbers,
    hasSpecial,
  ].filter(Boolean).length

  if (typesCount >= 2) strength++
  if (typesCount >= 3) strength++

  return Math.min(strength, 3)
}

/**
 * Obter label de força da senha
 */
const getStrengthLabel = (strength: number): string => {
  const labels = ['', 'Fraca', 'Média', 'Forte']
  return labels[strength] || ''
}

/**
 * Obter cor de força da senha
 */
const getStrengthColor = (strength: number): string => {
  const colors = ['', '#dc2626', '#eab308', '#22c55e']
  return colors[strength] || '#d1d5db'
}

const ResetPasswordForm: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const resetToken = searchParams.get('token') || ''

  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [success, setSuccess] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState(0)

  // Verificar se token existe
  useEffect(() => {
    if (!resetToken) {
      setErrors(prev => ({
        ...prev,
        general: 'Token de reset inválido. Verifique o link.',
      }))
    }
  }, [resetToken])

  /**
   * Validar formulário
   */
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!password.trim()) {
      newErrors.password = 'Senha é obrigatória'
    } else if (password.length < 8) {
      newErrors.password = 'Senha deve ter no mínimo 8 caracteres'
    }

    if (!confirmPassword.trim()) {
      newErrors.confirmPassword = 'Confirmação de senha é obrigatória'
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'As senhas não correspondem'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  /**
   * Limpar erros quando usuário começa a digitar
   */
  const handlePasswordChange = (value: string) => {
    setPassword(value)
    setPasswordStrength(calculatePasswordStrength(value))

    // Remover erro do campo
    if (errors.password) {
      setErrors(prev => ({
        ...prev,
        password: undefined,
      }))
    }

    // Remover erro de confirmação se senhas agora são iguais
    if (errors.confirmPassword && confirmPassword === value) {
      setErrors(prev => ({
        ...prev,
        confirmPassword: undefined,
      }))
    }

    // Remover erro geral
    if (errors.general) {
      setErrors(prev => ({
        ...prev,
        general: undefined,
      }))
    }
  }

  /**
   * Lidar com mudança de confirmação de senha
   */
  const handleConfirmPasswordChange = (value: string) => {
    setConfirmPassword(value)

    // Remover erro de confirmação se senhas agora são iguais
    if (errors.confirmPassword && password === value) {
      setErrors(prev => ({
        ...prev,
        confirmPassword: undefined,
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
      await authService.resetPassword(resetToken, password)

      setSuccess(true)
      setPassword('')
      setConfirmPassword('')

      // Redirecionar para login após 3 segundos
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
      <div className="reset-password-container">
        <div className="reset-password-card">
          <div className="reset-password-success">
            <div className="success-icon">✓</div>
            <h2>Senha Alterada com Sucesso!</h2>
            <p>Você pode fazer login com sua nova senha.</p>
            <p className="success-note">
              Redirecionando para o login em alguns segundos...
            </p>
            <Button
              variant="primary"
              fullWidth
              onClick={() => navigate('/login')}
              className="reset-password-button"
            >
              Ir ao Login
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="reset-password-container">
      <div className="reset-password-card">
        <div className="reset-password__header">
          <h1>Redefinir Senha</h1>
          <p className="reset-password__subtitle">
            Digite sua nova senha abaixo
          </p>
        </div>

        {errors.general && (
          <div className="reset-password__error-banner" role="alert">
            {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="reset-password-form">
          <div className="reset-password__field">
            <label htmlFor="password" className="reset-password__label">
              Nova Senha
            </label>
            <Input
              id="password"
              type="password"
              placeholder="Digite sua nova senha"
              value={password}
              onChange={e => handlePasswordChange(e.target.value)}
              error={errors.password}
              disabled={loading}
            />

            {/* Indicador de força de senha */}
            {password && (
              <div className="password-strength">
                <div className="strength-bar">
                  <div
                    className={`strength-bar-fill strength-${passwordStrength}`}
                    style={{
                      width: `${(passwordStrength / 3) * 100}%`,
                      backgroundColor: getStrengthColor(passwordStrength),
                    }}
                  />
                </div>
                <span
                  className="strength-label"
                  style={{
                    color: getStrengthColor(passwordStrength),
                  }}
                >
                  {getStrengthLabel(passwordStrength)}
                </span>
              </div>
            )}
          </div>

          <div className="reset-password__field">
            <label htmlFor="confirmPassword" className="reset-password__label">
              Confirmar Senha
            </label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="Confirme sua nova senha"
              value={confirmPassword}
              onChange={e => handleConfirmPasswordChange(e.target.value)}
              error={errors.confirmPassword}
              disabled={loading}
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={loading || !resetToken}
            fullWidth
          >
            {loading ? 'Redefinindo...' : 'Redefinir'}
          </Button>
        </form>

        <div className="reset-password__footer">
          <p>
            <Link to="/login" className="reset-password__link">
              Voltar ao login
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default ResetPasswordForm

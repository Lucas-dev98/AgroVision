import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import authService from '@services/authService'
import Button from '@components/atoms/Button'
import Input from '@components/atoms/Input'
import './RegisterForm.css'

interface FormErrors {
  nome?: string
  cpf_cnpj?: string
  email?: string
  senha?: string
  confirmarSenha?: string
  general?: string
}

const RegisterForm: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [formData, setFormData] = useState({
    nome: '',
    cpf_cnpj: '',
    email: '',
    senha: '',
    confirmarSenha: '',
  })

  /**
   * Validar CPF/CNPJ
   */
  const validateCpfCnpj = (value: string): boolean => {
    const cleaned = value.replace(/\D/g, '')
    return cleaned.length === 11 || cleaned.length === 14
  }

  /**
   * Validar email
   */
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  /**
   * Validar força da senha
   */
  const validatePassword = (password: string): boolean => {
    return password.length >= 8
  }

  /**
   * Validar formulário
   */
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório'
    } else if (formData.nome.trim().length < 3) {
      newErrors.nome = 'Nome deve ter no mínimo 3 caracteres'
    }

    if (!formData.cpf_cnpj.trim()) {
      newErrors.cpf_cnpj = 'CPF/CNPJ é obrigatório'
    } else if (!validateCpfCnpj(formData.cpf_cnpj)) {
      newErrors.cpf_cnpj = 'CPF/CNPJ deve ter 11 ou 14 dígitos'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email é obrigatório'
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Email inválido'
    }

    if (!formData.senha.trim()) {
      newErrors.senha = 'Senha é obrigatória'
    } else if (!validatePassword(formData.senha)) {
      newErrors.senha = 'Senha deve ter no mínimo 8 caracteres'
    }

    if (!formData.confirmarSenha.trim()) {
      newErrors.confirmarSenha = 'Confirmar senha é obrigatório'
    } else if (formData.senha !== formData.confirmarSenha) {
      newErrors.confirmarSenha = 'Senhas não correspondem'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  /**
   * Lidar com mudança de input
   */
  const handleInputChange = (
    field: keyof typeof formData,
    value: string
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }))

    // Remover erro do campo que o usuário está digitando
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined,
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
   * Lidar com submissão do formulário
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      await authService.register({
        nome: formData.nome,
        cpf_cnpj: formData.cpf_cnpj,
        email: formData.email,
        senha: formData.senha,
      })

      // Redirecionar para login após cadastro bem-sucedido
      navigate('/login')
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
    <div className="register-form-container">
      <div className="register-form-card">
        <div className="register-form__header">
          <h1>CADASTRO</h1>
        </div>

        {errors.general && (
          <div className="register-form__error-banner" role="alert">
            {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="register-form">
          <div className="register-form__field">
            <label htmlFor="nome" className="register-form__label">
              Nome Completo
            </label>
            <Input
              id="nome"
              type="text"
              placeholder="Ex: João Silva"
              value={formData.nome}
              onChange={e => handleInputChange('nome', e.target.value)}
              error={!!errors.nome}
              errorMessage={errors.nome}
              disabled={loading}
            />
          </div>

          <div className="register-form__field">
            <label htmlFor="cpf_cnpj" className="register-form__label">
              CPF/CNPJ
            </label>
            <Input
              id="cpf_cnpj"
              type="text"
              placeholder="Ex: 123.456.789-01"
              value={formData.cpf_cnpj}
              onChange={e => handleInputChange('cpf_cnpj', e.target.value)}
              error={!!errors.cpf_cnpj}
              errorMessage={errors.cpf_cnpj}
              disabled={loading}
            />
          </div>

          <div className="register-form__field">
            <label htmlFor="email" className="register-form__label">
              Email
            </label>
            <Input
              id="email"
              type="email"
              placeholder="Ex: joao@email.com"
              value={formData.email}
              onChange={e => handleInputChange('email', e.target.value)}
              error={!!errors.email}
              errorMessage={errors.email}
              disabled={loading}
            />
          </div>

          <div className="register-form__field">
            <label htmlFor="senha" className="register-form__label">
              Senha
            </label>
            <Input
              id="senha"
              type="password"
              placeholder="Mínimo 8 caracteres"
              value={formData.senha}
              onChange={e => handleInputChange('senha', e.target.value)}
              error={!!errors.senha}
              errorMessage={errors.senha}
              disabled={loading}
            />
          </div>

          <div className="register-form__field">
            <label htmlFor="confirmarSenha" className="register-form__label">
              Confirmar Senha
            </label>
            <Input
              id="confirmarSenha"
              type="password"
              placeholder="Digite a senha novamente"
              value={formData.confirmarSenha}
              onChange={e =>
                handleInputChange('confirmarSenha', e.target.value)
              }
              error={!!errors.confirmarSenha}
              errorMessage={errors.confirmarSenha}
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
            {loading ? 'Cadastrando...' : 'Cadastrar'}
          </Button>
        </form>

        <div className="register-form__footer">
          <p>
            Já tem uma conta?{' '}
            <Link to="/login" className="register-form__login-link">
              Faça login
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterForm

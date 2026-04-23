import { useState, useEffect, useCallback } from 'react'
import authService, { RegisterData } from '@services/authService'

export interface AuthUser {
  cpf_cnpj: string
  email: string
  nome: string
  user_id: number
}

interface UseAuthReturn {
  isAuthenticated: boolean
  user: AuthUser | null
  loading: boolean
  error: string | null
  login: (cpfCnpj: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshAccessToken: () => Promise<void>
  forgotPassword: (cpfCnpj: string) => Promise<void>
  resetPassword: (token: string, newPassword: string) => Promise<void>
  clearError: () => void
}

/**
 * Hook para gerenciar estado de autenticação
 * Fornece métodos para login, registro, logout e renovação de token
 */
const useAuth = (): UseAuthReturn => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /**
   * Verificar se existe token válido ao montar o componente
   */
  useEffect(() => {
    const checkAuth = async () => {
      const tokens = authService.getStoredTokens()

      if (tokens.access_token && authService.isTokenValid(tokens.access_token)) {
        setIsAuthenticated(true)
      } else if (tokens.refresh_token) {
        try {
          await authService.refreshToken(tokens.refresh_token)
          setIsAuthenticated(true)
        } catch (err) {
          console.error('Erro ao renovar token:', err)
          setIsAuthenticated(false)
          setUser(null)
        }
      } else {
        setIsAuthenticated(false)
      }
    }

    checkAuth()
  }, [])

  /**
   * Fazer login
   */
  const login = useCallback(async (cpfCnpj: string, password: string) => {
    setLoading(true)
    setError(null)

    try {
      await authService.login(cpfCnpj, password)
      setIsAuthenticated(true)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao fazer login'
      setError(message)
      setIsAuthenticated(false)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Registrar novo usuário
   */
  const register = useCallback(async (data: RegisterData) => {
    setLoading(true)
    setError(null)

    try {
      await authService.register(data)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Erro ao registrar usuário'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Fazer logout
   */
  const logout = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const tokens = authService.getStoredTokens()
      if (tokens.access_token) {
        await authService.logout(tokens.access_token)
      }
    } catch (err) {
      console.error('Erro ao fazer logout:', err)
    } finally {
      setIsAuthenticated(false)
      setUser(null)
      setLoading(false)
    }
  }, [])

  /**
   * Renovar token de acesso
   */
  const refreshAccessToken = useCallback(async () => {
    try {
      const tokens = authService.getStoredTokens()

      if (!tokens.refresh_token) {
        throw new Error('Sem refresh token disponível')
      }

      await authService.refreshToken(tokens.refresh_token)
      setIsAuthenticated(true)
    } catch (err) {
      console.error('Erro ao renovar token:', err)
      setIsAuthenticated(false)
      setUser(null)
    }
  }, [])

  /**
   * Requisitar recuperação de senha
   */
  const forgotPassword = useCallback(async (cpfCnpj: string) => {
    setLoading(true)
    setError(null)

    try {
      await authService.forgotPassword(cpfCnpj)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Erro ao requisitar recuperação'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Redefinir senha com token
   */
  const resetPassword = useCallback(
    async (token: string, newPassword: string) => {
      setLoading(true)
      setError(null)

      try {
        await authService.resetPassword(token, newPassword)
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Erro ao redefinir senha'
        setError(message)
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  /**
   * Limpar erro
   */
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    isAuthenticated,
    user,
    loading,
    error,
    login,
    register,
    logout,
    refreshAccessToken,
    forgotPassword,
    resetPassword,
    clearError,
  }
}

export default useAuth

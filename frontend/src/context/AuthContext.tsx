import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import authService, { RegisterData, ProfileUser } from '@services/authService'

export interface AuthUser {
  cpf_cnpj: string
  email: string
  nome: string
  user_id: number
}

const mapProfileToAuthUser = (profile: ProfileUser): AuthUser => ({
  cpf_cnpj: profile.username,
  email: profile.email,
  nome: profile.username,
  user_id: profile.id,
})

interface AuthContextType {
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

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [authInitialized, setAuthInitialized] = useState(false)

  // Verificar autenticação apenas uma vez ao montar
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const tokens = authService.getStoredTokens()

        if (tokens.access_token && authService.isTokenValid(tokens.access_token)) {
          try {
            const profile = await authService.getProfile()
            setUser(mapProfileToAuthUser(profile))
          } catch (err) {
            console.error('Erro ao carregar perfil:', err)
          }
          setIsAuthenticated(true)
        } else if (tokens.refresh_token) {
          try {
            await authService.refreshToken(tokens.refresh_token)
            const profile = await authService.getProfile()
            setUser(mapProfileToAuthUser(profile))
            setIsAuthenticated(true)
          } catch (err) {
            console.error('Erro ao renovar token:', err)
            setIsAuthenticated(false)
            setUser(null)
          }
        } else {
          setIsAuthenticated(false)
        }
      } finally {
        setAuthInitialized(true)
        setLoading(false)
      }
    }

    checkAuth()
  }, []) // Executar apenas uma vez ao montar

  const login = useCallback(async (cpfCnpj: string, password: string) => {
    setLoading(true)
    setError(null)

    try {
      await authService.login(cpfCnpj, password)
      const profile = await authService.getProfile()
      setUser(mapProfileToAuthUser(profile))
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

  const register = useCallback(async (data: RegisterData) => {
    setLoading(true)
    setError(null)

    try {
      await authService.register(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao registrar usuário'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

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

  const refreshAccessToken = useCallback(async () => {
    try {
      const tokens = authService.getStoredTokens()

      if (!tokens.refresh_token) {
        throw new Error('Sem refresh token disponível')
      }

      await authService.refreshToken(tokens.refresh_token)
      const profile = await authService.getProfile()
      setUser(mapProfileToAuthUser(profile))
      setIsAuthenticated(true)
    } catch (err) {
      console.error('Erro ao renovar token:', err)
      setIsAuthenticated(false)
      setUser(null)
    }
  }, [])

  const forgotPassword = useCallback(async (cpfCnpj: string) => {
    setLoading(true)
    setError(null)

    try {
      await authService.forgotPassword(cpfCnpj)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro na recuperação de senha'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const resetPassword = useCallback(async (token: string, newPassword: string) => {
    setLoading(true)
    setError(null)

    try {
      await authService.resetPassword(token, newPassword)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao redefinir senha'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        loading: !authInitialized ? true : loading,
        error,
        login,
        register,
        logout,
        refreshAccessToken,
        forgotPassword,
        resetPassword,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

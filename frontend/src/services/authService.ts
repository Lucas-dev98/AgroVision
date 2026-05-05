import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginResponseWithMFA {
  requires_mfa: boolean
  session_token?: string
  user_id?: number
  mfa_methods?: ('email' | 'sms' | 'authenticator')[]
  email?: string
  phone?: string
}

export interface RegisterData {
  cpf_cnpj: string
  email: string
  senha: string
  nome: string
}

export interface RegisterResponse {
  user_id: number
  cpf_cnpj: string
  email: string
  nome: string
}

export interface TokensData {
  access_token: string | null
  refresh_token: string | null
}

class AuthService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  /**
   * Fazer login com CPF/CNPJ e senha
   * @param cpfCnpj CPF ou CNPJ do usuário
   * @param password Senha do usuário
   * @returns Tokens de acesso e refresh, ou resposta de MFA necessária
   */
  async login(
    cpfCnpj: string,
    password: string
  ): Promise<LoginResponse | LoginResponseWithMFA> {
    try {
      const response = await this.client.post<
        LoginResponse | LoginResponseWithMFA
      >('/auth/login', {
        username: cpfCnpj,
        password: password,
      })

      // Se MFA não é necessário, armazenar tokens
      const data = response.data
      if ('access_token' in data && !('requires_mfa' in data)) {
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
      }

      return data
    } catch (error) {
      this.handleError(error)
      throw error
    }
  }

  /**
   * Registrar novo usuário
   * @param data Dados do novo usuário
   * @returns Dados do usuário criado
   */
  async register(data: RegisterData): Promise<RegisterResponse> {
    try {
      const response = await this.client.post<RegisterResponse>(
        '/auth/register',
        {
          cpf_cnpj: data.cpf_cnpj,
          email: data.email,
          password: data.senha,
          nome: data.nome,
        }
      )

      return response.data
    } catch (error) {
      this.handleError(error)
      throw error
    }
  }

  /**
   * Renovar token de acesso usando refresh token
   * @param refreshToken Token de refresh
   * @returns Novos tokens
   */
  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    try {
      const response = await this.client.post<LoginResponse>(
        '/auth/refresh',
        {
          refresh_token: refreshToken,
        }
      )

      // Atualizar tokens
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)

      return response.data
    } catch (error) {
      this.handleError(error)
      throw error
    }
  }

  /**
   * Fazer logout
   * @param accessToken Token de acesso
   */
  async logout(accessToken: string): Promise<void> {
    try {
      await this.client.post('/auth/logout', {
        access_token: accessToken,
      })
    } catch (error) {
      console.warn('Erro ao fazer logout no servidor:', error)
    } finally {
      // Sempre limpar tokens localmente
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  /**
   * Obter tokens armazenados no localStorage
   * @returns Tokens armazenados
   */
  getStoredTokens(): TokensData {
    return {
      access_token: localStorage.getItem('access_token'),
      refresh_token: localStorage.getItem('refresh_token'),
    }
  }

  /**
   * Verificar se token é válido
   * @param token Token JWT
   * @returns true se válido, false caso contrário
   */
  isTokenValid(token: string): boolean {
    try {
      // Decodificar token JWT
      const parts = token.split('.')
      if (parts.length !== 3) return false

      const decoded = JSON.parse(atob(parts[1]))

      // Verificar expiration
      if (!decoded.exp) return false

      // Verificar se ainda não expirou (com margem de 5 minutos)
      const expirationTime = decoded.exp * 1000 // Converter para ms
      const currentTime = Date.now()
      const marginMs = 5 * 60 * 1000 // 5 minutos

      return currentTime < expirationTime - marginMs
    } catch (error) {
      return false
    }
  }

  /**
   * Requisitar recuperação de senha
   * @param cpfCnpj CPF ou CNPJ
   */
  async forgotPassword(cpfCnpj: string): Promise<void> {
    try {
      await this.client.post('/auth/forgot-password', {
        cpf_cnpj: cpfCnpj,
      })
    } catch (error) {
      this.handleError(error)
      throw error
    }
  }

  /**
   * Redefinir senha com token
   * @param resetToken Token de reset
   * @param newPassword Nova senha
   */
  async resetPassword(resetToken: string, newPassword: string): Promise<void> {
    try {
      await this.client.post('/auth/reset-password', {
        reset_token: resetToken,
        new_password: newPassword,
      })
    } catch (error) {
      this.handleError(error)
      throw error
    }
  }

  /**
   * Requisitar código MFA (Multi-Factor Authentication)
   * @param userId ID do usuário
   * @param method Método de MFA (email, sms, authenticator)
   * @returns Session token e detalhes da requisição
   */
  async requestMFA(userId: string, method: 'email' | 'sms' | 'authenticator') {
    try {
      const response = await this.client.post('/auth/mfa/send', {
        user_id: userId,
        method: method,
      })

      return response.data
    } catch (error) {
      this.handleError(error)
      throw error
    }
  }

  /**
   * Verificar código MFA
   * @param sessionToken Token temporário da sessão MFA
   * @param code Código MFA de 6 dígitos
   * @returns Tokens de acesso e refresh
   */
  async verifyMFA(sessionToken: string, code: string): Promise<LoginResponse> {
    try {
      const response = await this.client.post<LoginResponse>('/auth/mfa/verify', {
        session_token: sessionToken,
        code: code,
      })

      // Armazenar tokens
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)

      return response.data
    } catch (error) {
      this.handleError(error)
      throw error
    }
  }

  /**
   * Reenviar código MFA
   * @param sessionToken Token temporário da sessão MFA
   * @returns Resposta do servidor
   */
  async resendMFACode(sessionToken: string) {
    try {
      const response = await this.client.post('/auth/mfa/resend', {
        session_token: sessionToken,
      })

      return response.data
    } catch (error) {
      this.handleError(error)
      throw error
    }
  }

  /**
   * Tratador centralizado de erros
   * @param error Erro da requisição
   */
  private handleError(error: any): void {
    if (error.response) {
      // Erro de resposta do servidor
      const status = error.response.status
      const message = error.response.data?.detail || 'Erro desconhecido'

      if (status === 401) {
        // Token expirado - limpar localStorage
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }

      throw new Error(message)
    } else if (error.request) {
      // Erro de requisição (sem resposta)
      throw new Error('Erro de conexão com o servidor')
    } else {
      // Outro erro
      throw error
    }
  }
}

export default new AuthService()

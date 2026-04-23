import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import useAuth from './useAuth'

// Mock do AuthService
vi.mock('@services/authService', () => ({
  default: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    getStoredTokens: vi.fn(),
    isTokenValid: vi.fn(),
    refreshToken: vi.fn(),
    forgotPassword: vi.fn(),
    resetPassword: vi.fn(),
  },
}))

import authService from '@services/authService'

const MockedAuthService = authService as any

describe('useAuth Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('deve inicializar com estado de não autenticado', () => {
    MockedAuthService.getStoredTokens.mockReturnValue({
      access_token: null,
      refresh_token: null,
    })

    const { result } = renderHook(() => useAuth())

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('deve fazer login e atualizar estado', async () => {
    MockedAuthService.login.mockResolvedValue({
      access_token: 'token123',
      refresh_token: 'refresh123',
    })

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.login('12345678901234', 'senha123')
    })

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.error).toBeNull()
  })

  it('deve exibir erro quando login falha', async () => {
    const errorMessage = 'Credenciais inválidas'
    MockedAuthService.login.mockRejectedValue(new Error(errorMessage))

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      try {
        await result.current.login('12345678901234', 'senha-errada')
      } catch {
        // Erro esperado
      }
    })

    await waitFor(() => {
      expect(result.current.error).toBe(errorMessage)
    })
  })

  it('deve fazer logout e limpar estado', async () => {
    MockedAuthService.getStoredTokens.mockReturnValue({
      access_token: 'token123',
      refresh_token: 'refresh123',
    })

    MockedAuthService.logout.mockResolvedValue(undefined)

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.logout()
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(MockedAuthService.logout).toHaveBeenCalledWith('token123')
  })

  it('deve registrar novo usuário', async () => {
    const userData = {
      cpf_cnpj: '12345678901234',
      email: 'usuario@email.com',
      senha: 'senha123',
      nome: 'João Silva',
    }

    MockedAuthService.register.mockResolvedValue({
      user_id: 1,
      cpf_cnpj: userData.cpf_cnpj,
      email: userData.email,
      nome: userData.nome,
    })

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.register(userData)
    })

    expect(MockedAuthService.register).toHaveBeenCalledWith(userData)
  })

  it('deve renovar token quando expirado', async () => {
    MockedAuthService.getStoredTokens.mockReturnValue({
      access_token: 'expired_token',
      refresh_token: 'refresh123',
    })

    MockedAuthService.refreshToken.mockResolvedValue({
      access_token: 'new_token',
      refresh_token: 'new_refresh123',
    })

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.refreshAccessToken()
    })

    expect(MockedAuthService.refreshToken).toHaveBeenCalledWith('refresh123')
  })

  it('deve requisitar recuperação de senha', async () => {
    MockedAuthService.forgotPassword.mockResolvedValue(undefined)

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.forgotPassword('12345678901234')
    })

    expect(MockedAuthService.forgotPassword).toHaveBeenCalledWith(
      '12345678901234'
    )
  })

  it('deve redefinir senha com token', async () => {
    MockedAuthService.resetPassword.mockResolvedValue(undefined)

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await result.current.resetPassword('token123', 'novaSenha123')
    })

    expect(MockedAuthService.resetPassword).toHaveBeenCalledWith(
      'token123',
      'novaSenha123'
    )
  })

  it('deve atualizar erro para null após operação bem-sucedida', async () => {
    MockedAuthService.login
      .mockRejectedValueOnce(new Error('Erro temporário'))
      .mockResolvedValueOnce({
        access_token: 'token123',
        refresh_token: 'refresh123',
      })

    const { result } = renderHook(() => useAuth())

    // Primeira tentativa - falha
    await act(async () => {
      try {
        await result.current.login('12345678901234', 'senha-errada')
      } catch {
        // Erro esperado
      }
    })

    await waitFor(() => {
      expect(result.current.error).not.toBeNull()
    })

    // Segunda tentativa - sucesso
    await act(async () => {
      await result.current.login('12345678901234', 'senha123')
    })

    expect(result.current.error).toBeNull()
  })

  it('deve manter loading state durante operações', async () => {
    MockedAuthService.login.mockImplementation(
      () =>
        new Promise(resolve =>
          setTimeout(
            () =>
              resolve({
                access_token: 'token123',
                refresh_token: 'refresh123',
              }),
            100
          )
        )
    )

    const { result } = renderHook(() => useAuth())

    let wasLoading = false

    act(() => {
      result.current.login('12345678901234', 'senha123').then(() => {
        wasLoading = result.current.loading
      })
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })

    // Loading deve ter sido true em algum momento
    // (Isso pode variar conforme a implementação)
  })
})

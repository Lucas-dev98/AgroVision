import { useState } from 'react'
import authService from '@services/authService'

export interface MFAState {
  mfaRequired: boolean
  sessionToken: string | null
  mfaMethod: 'email' | 'sms' | 'authenticator' | null
  mfaLoading: boolean
  mfaError: string | null
}

/**
 * Hook para gerenciar autenticação multi-fator (MFA)
 * Fornece métodos para requisitar, verificar e reenviar códigos MFA
 */
function useMFA() {
  const [mfaState, setMFAStateInternal] = useState<MFAState>({
    mfaRequired: false,
    sessionToken: null,
    mfaMethod: null,
    mfaLoading: false,
    mfaError: null,
  })

  /**
   * Atualizar estado de MFA
   */
  const setMFAState = (state: Partial<MFAState>) => {
    setMFAStateInternal((prev) => ({ ...prev, ...state }))
  }

  /**
   * Requisitar MFA para um usuário
   */
  const requestMFA = async (
    userId: string,
    method: 'email' | 'sms' | 'authenticator'
  ) => {
    setMFAState({ mfaLoading: true, mfaError: null })

    try {
      const response = await authService.requestMFA(userId, method)

      setMFAState({
        mfaRequired: true,
        sessionToken: response.session_token,
        mfaMethod: method,
        mfaLoading: false,
        mfaError: null,
      })

      return response
    } catch (error: any) {
      const errorMessage =
        error.message || 'Erro ao requisitar código MFA. Tente novamente.'

      setMFAState({
        mfaLoading: false,
        mfaError: errorMessage,
      })

      throw error
    }
  }

  /**
   * Verificar código MFA
   */
  const verifyMFA = async (code: string) => {
    if (!mfaState.sessionToken) {
      throw new Error('Session token não disponível')
    }

    setMFAState({ mfaLoading: true, mfaError: null })

    try {
      const tokens = await authService.verifyMFA(mfaState.sessionToken, code)

      // Limpar estado MFA após sucesso
      setMFAState({
        mfaRequired: false,
        sessionToken: null,
        mfaMethod: null,
        mfaLoading: false,
        mfaError: null,
      })

      return tokens
    } catch (error: any) {
      const errorMessage =
        error.message || 'Código inválido. Tente novamente.'

      setMFAState({
        mfaLoading: false,
        mfaError: errorMessage,
      })

      throw error
    }
  }

  /**
   * Reenviar código MFA
   */
  const resendMFA = async () => {
    if (!mfaState.sessionToken) {
      throw new Error('Session token não disponível')
    }

    setMFAState({ mfaLoading: true, mfaError: null })

    try {
      const response = await authService.resendMFACode(mfaState.sessionToken)

      setMFAState({
        mfaLoading: false,
        mfaError: null,
      })

      return response
    } catch (error: any) {
      const errorMessage =
        error.message || 'Erro ao reenviar código. Tente novamente.'

      setMFAState({
        mfaLoading: false,
        mfaError: errorMessage,
      })

      throw error
    }
  }

  /**
   * Limpar estado de MFA
   */
  const clearMFA = () => {
    setMFAState({
      mfaRequired: false,
      sessionToken: null,
      mfaMethod: null,
      mfaLoading: false,
      mfaError: null,
    })
  }

  return {
    ...mfaState,
    requestMFA,
    verifyMFA,
    resendMFA,
    clearMFA,
    setMFAState,
  }
}

export default useMFA

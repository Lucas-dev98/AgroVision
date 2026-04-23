import React, { useState, useRef, useEffect } from 'react'
import authService from '@services/authService'
import Button from '@atoms/Button'
import '@styles/MFAVerification.css'

interface MFAVerificationProps {
  sessionToken: string
  method: 'email' | 'sms' | 'authenticator'
  email?: string
  phone?: string
  onSuccess: (tokens: { access_token: string; refresh_token: string }) => void
  onChangeMethod?: () => void
}

const MFAVerification: React.FC<MFAVerificationProps> = ({
  sessionToken,
  method,
  email,
  phone,
  onSuccess,
  onChangeMethod,
}) => {
  const [code, setCode] = useState<string[]>(['', '', '', '', '', ''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resendCountdown, setResendCountdown] = useState(0)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  // Configurar countdown de reenvio
  useEffect(() => {
    let timer: NodeJS.Timeout
    if (resendCountdown > 0) {
      timer = setTimeout(() => setResendCountdown(resendCountdown - 1), 1000)
    }
    return () => clearTimeout(timer)
  }, [resendCountdown])

  // Inicia o countdown ao montar
  useEffect(() => {
    setResendCountdown(60)
  }, [])

  /**
   * Atualizar valor do dígito
   */
  const handleDigitChange = (index: number, value: string) => {
    // Apenas aceitar dígitos
    if (!/^\d*$/.test(value)) return

    // Limitar a um único dígito
    const digit = value.slice(-1)

    // Atualizar array de código
    const newCode = [...code]
    newCode[index] = digit
    setCode(newCode)

    // Limpar erro ao digitar
    if (error) {
      setError(null)
    }

    // Auto-focar no próximo campo
    if (digit && index < 5) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  /**
   * Lidar com backspace
   */
  const handleKeyDown = (
    index: number,
    e: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (e.key === 'Backspace') {
      const newCode = [...code]

      // Se campo atual está vazio, focar no anterior
      if (!code[index] && index > 0) {
        inputRefs.current[index - 1]?.focus()
      } else {
        // Limpar campo atual
        newCode[index] = ''
        setCode(newCode)
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus()
    } else if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  /**
   * Verificar código MFA
   */
  const handleVerify = async () => {
    const codeString = code.join('')

    // Validar que todos os dígitos foram inseridos
    if (codeString.length !== 6) {
      setError('Digite todos os 6 dígitos')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const tokens = await authService.verifyMFA(sessionToken, codeString)
      onSuccess(tokens)
    } catch (err: any) {
      setError(err.message || 'Código inválido. Tente novamente.')
      // Limpar código
      setCode(['', '', '', '', '', ''])
      inputRefs.current[0]?.focus()
    } finally {
      setLoading(false)
    }
  }

  /**
   * Reenviar código MFA
   */
  const handleResend = async () => {
    if (resendCountdown > 0) return

    try {
      await authService.resendMFACode(sessionToken)
      setResendCountdown(60)
      setError(null)
      setCode(['', '', '', '', '', ''])
      inputRefs.current[0]?.focus()
    } catch (err: any) {
      setError(err.message || 'Erro ao reenviar código')
    }
  }

  /**
   * Mascarar email/telefone
   */
  const maskContact = (): string => {
    if (method === 'email' && email) {
      const parts = email.split('@')
      const masked = parts[0].substring(0, 3) + '*'.repeat(parts[0].length - 3)
      return `${masked}@${parts[1]}`
    } else if (method === 'sms' && phone) {
      return `****${phone.slice(-2)}`
    }
    return ''
  }

  return (
    <div className="mfa-verification-container">
      <div className="mfa-card">
        <div className="mfa-header">
          <h1>Verificação de Segurança</h1>
          <p className="mfa-subtitle">Autenticação Multi-Fator (MFA)</p>
        </div>

        <div className="mfa-content">
          {/* Mensagem inicial */}
          <div className="mfa-message">
            {method === 'email' && (
              <p>
                Enviamos um código de segurança para <strong>{maskContact()}</strong>
              </p>
            )}
            {method === 'sms' && (
              <p>
                Enviamos um código de segurança para o seu telefone{' '}
                <strong>{maskContact()}</strong>
              </p>
            )}
            {method === 'authenticator' && (
              <p>
                Digite o código de 6 dígitos do seu aplicativo authenticator
              </p>
            )}
          </div>

          {/* Erro */}
          {error && <div className="mfa-error">{error}</div>}

          {/* Inputs de código */}
          <div className="mfa-code-inputs">
            {code.map((digit, index) => (
              <input
                key={index}
                ref={(el) => {
                  inputRefs.current[index] = el
                }}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleDigitChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                className="mfa-code-input"
                disabled={loading}
                autoFocus={index === 0}
              />
            ))}
          </div>

          {/* Botão de verificação */}
          <Button
            variant="primary"
            fullWidth
            disabled={loading || code.join('').length !== 6}
            onClick={handleVerify}
            className="mfa-verify-button"
          >
            {loading ? 'Verificando...' : 'Verificar'}
          </Button>

          {/* Reenviar código */}
          <div className="mfa-footer">
            <p className="mfa-resend">
              {resendCountdown > 0 ? (
                <>
                  Reenviar em <strong>{resendCountdown}s</strong>
                </>
              ) : (
                <>
                  Não recebeu o código?{' '}
                  <button
                    className="mfa-link"
                    onClick={handleResend}
                    disabled={loading}
                  >
                    Reenviar código
                  </button>
                </>
              )}
            </p>

            {onChangeMethod && (
              <p className="mfa-change-method">
                <button
                  className="mfa-link"
                  onClick={onChangeMethod}
                  disabled={loading}
                >
                  Usar outro método
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default MFAVerification

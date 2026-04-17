import React, { useEffect, useRef, useCallback } from 'react'
import './Alert.css'

type AlertType = 'success' | 'error' | 'warning' | 'info'
type AlertPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'

interface AlertProps {
  isOpen: boolean
  message: string
  title?: string
  type?: AlertType
  dismissible?: boolean
  autoDismissMs?: number
  onClose?: () => void
  position?: AlertPosition
  ariaLabel?: string
  showIcon?: boolean
}

const Alert: React.FC<AlertProps> = ({
  isOpen,
  message,
  title,
  type = 'info',
  dismissible = true,
  autoDismissMs = 5000,
  onClose,
  position = 'top-right',
  ariaLabel,
  showIcon = true,
}) => {
  const dismissTimerRef = useRef<NodeJS.Timeout>()
  const alertRef = useRef<HTMLDivElement>(null)

  const resetDismissTimer = useCallback(() => {
    if (dismissTimerRef.current) {
      clearTimeout(dismissTimerRef.current)
    }

    if (autoDismissMs && autoDismissMs > 0) {
      dismissTimerRef.current = setTimeout(() => {
        onClose?.()
      }, autoDismissMs)
    }
  }, [autoDismissMs, onClose])

  useEffect(() => {
    if (isOpen) {
      resetDismissTimer()
    }

    return () => {
      if (dismissTimerRef.current) {
        clearTimeout(dismissTimerRef.current)
      }
    }
  }, [isOpen, resetDismissTimer])

  const handleMouseEnter = () => {
    if (dismissTimerRef.current) {
      clearTimeout(dismissTimerRef.current)
    }
  }

  const handleMouseLeave = () => {
    resetDismissTimer()
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return (
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
          </svg>
        )
      case 'error':
        return (
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
        )
      case 'warning':
        return (
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
          </svg>
        )
      case 'info':
        return (
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
          </svg>
        )
      default:
        return null
    }
  }

  if (!isOpen) return null

  return (
    <div className={`alert__container alert__container--${position}`}>
      <div
        ref={alertRef}
        className={`alert alert--${type}`}
        role="status"
        aria-live={type === 'error' ? 'assertive' : 'polite'}
        aria-label={ariaLabel}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {/* Icon */}
        {showIcon && (
          <div className="alert__icon">
            {getIcon()}
          </div>
        )}

        {/* Content */}
        <div className="alert__content">
          {title && <div className="alert__title">{title}</div>}
          <div className="alert__message">{message}</div>
        </div>

        {/* Close Button */}
        {dismissible && (
          <button
            className="alert__close"
            onClick={onClose}
            aria-label="Fechar notificação"
            type="button"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
}

export default Alert

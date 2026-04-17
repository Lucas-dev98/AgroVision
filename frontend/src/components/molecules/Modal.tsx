import React, { useEffect, useRef, useCallback } from 'react'
import './Modal.css'

interface ModalProps {
  isOpen: boolean
  title: string
  children: React.ReactNode
  onClose?: () => void
  onConfirm?: () => void
  onCancel?: () => void
  variant?: 'default' | 'confirmation'
  size?: 'small' | 'medium' | 'large'
  isDanger?: boolean
  closeOnBackdrop?: boolean
  closeOnEscape?: boolean
  confirmText?: string
  cancelText?: string
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  title,
  children,
  onClose,
  onConfirm,
  onCancel,
  variant = 'default',
  size = 'medium',
  isDanger = false,
  closeOnBackdrop = true,
  closeOnEscape = true,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
}) => {
  const modalRef = useRef<HTMLDivElement>(null)
  const previousActiveElement = useRef<HTMLElement | null>(null)

  // Handle opening
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
      previousActiveElement.current?.focus()
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  // Handle keyboard events
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && closeOnEscape) {
        onClose?.()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, closeOnEscape, onClose])

  const handleBackdropClick = useCallback(() => {
    if (closeOnBackdrop) {
      onClose?.()
    }
  }, [closeOnBackdrop, onClose])

  const handleContentClick = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  if (!isOpen) return null

  const isConfirmation = variant === 'confirmation'

  return (
    <div className="modal__overlay">
      <div
        className="modal__backdrop"
        onClick={handleBackdropClick}
        aria-hidden="true"
      />
      <div
        className={`modal__content modal__content--${size} ${isDanger ? 'modal--danger' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        aria-describedby="modal-content"
        ref={modalRef}
        onClick={handleContentClick}
      >
        {/* Header */}
        <div className="modal__header">
          <h2 id="modal-title" className="modal__title">
            {title}
          </h2>
          {!isConfirmation && (
            <button
              className="modal__close"
              onClick={onClose}
              aria-label="Fechar modal"
              type="button"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          )}
        </div>

        {/* Content */}
        <div id="modal-content" className="modal__body">
          {children}
        </div>

        {/* Footer - Confirmation Mode */}
        {isConfirmation && (
          <div className="modal__footer">
            <button
              className="modal__button modal__button--cancel"
              onClick={onCancel}
              type="button"
            >
              {cancelText}
            </button>
            <button
              className={`modal__button modal__button--confirm ${isDanger ? 'modal__button--danger' : ''}`}
              onClick={onConfirm}
              type="button"
            >
              {confirmText}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Modal

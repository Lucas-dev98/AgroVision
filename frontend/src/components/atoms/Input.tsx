import React from 'react'
import './Input.css'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  fullWidth?: boolean
}

/**
 * Input Component - Atomic Design
 * 
 * @component
 * @example
 * <Input 
 *   label="Email" 
 *   type="email" 
 *   placeholder="user@example.com"
 * />
 */
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, fullWidth = false, className = '', ...props }, ref) => {
    const errorClass = error ? 'input--error' : ''
    const finalClassName = `input ${errorClass} ${className}`.trim()

    return (
      <div className={fullWidth ? 'input-wrapper' : ''}>
        {label && (
          <label className="input-label">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={finalClassName}
          {...props}
        />
        {error && (
          <p className="input-message input-error">{error}</p>
        )}
        {helperText && !error && (
          <p className="input-message input-helper">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input

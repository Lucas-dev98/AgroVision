import React from 'react'

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
    const baseStyles = 'border rounded px-3 py-2 text-base transition-colors duration-200'
    const borderStyles = error
      ? 'border-red-500 focus:border-red-600 focus:ring-red-200'
      : 'border-gray-300 focus:border-blue-600 focus:ring-blue-200'
    const focusStyles = 'focus:outline-none focus:ring-2'
    const widthStyles = fullWidth ? 'w-full' : ''

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label className="block mb-2 font-semibold text-gray-700">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`${baseStyles} ${borderStyles} ${focusStyles} ${widthStyles} ${className}`}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input

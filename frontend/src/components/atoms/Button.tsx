import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  children: React.ReactNode
}

/**
 * Button Component - Atomic Design
 * 
 * @component
 * @example
 * <Button variant="primary" onClick={() => console.log('clicked')}>
 *   Click me
 * </Button>
 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', loading = false, children, className = '', ...props }, ref) => {
    const baseStyles = 'font-semibold rounded transition-colors duration-200'
    
    const variantStyles = {
      primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400',
      secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-400',
      danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-gray-400',
    }

    const sizeStyles = {
      sm: 'px-3 py-1 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    }

    const finalClassName = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`

    return (
      <button
        ref={ref}
        className={finalClassName}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading ? '...' : children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button

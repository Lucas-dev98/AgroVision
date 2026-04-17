import React from 'react'
import './Button.css'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  fullWidth?: boolean
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
  ({ 
    variant = 'primary', 
    size = 'md', 
    loading = false,
    fullWidth = false,
    children, 
    className = '', 
    ...props 
  }, ref) => {
    const variantClass = `button--${variant}`
    const sizeClass = `button--${size}`
    const fullWidthClass = fullWidth ? 'button--full' : ''
    const loadingClass = loading ? 'button--loading' : ''
    
    const finalClassName = `button ${variantClass} ${sizeClass} ${fullWidthClass} ${loadingClass} ${className}`.trim()

    return (
      <button
        ref={ref}
        className={finalClassName}
        disabled={loading || props.disabled}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button

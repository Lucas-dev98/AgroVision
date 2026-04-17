import React from 'react'
import './Card.css'

interface CardProps {
  title?: string
  children: React.ReactNode
  className?: string
  onClick?: () => void
}

/**
 * Card Component - Atomic Design
 * 
 * @component
 * @example
 * <Card title="Animal Info">
 *   <p>Details here</p>
 * </Card>
 */
const Card: React.FC<CardProps> = ({ title, children, className = '', onClick }) => {
  const clickableClass = onClick ? 'card--clickable' : ''
  const finalClassName = `card ${clickableClass} ${className}`.trim()

  return (
    <div
      className={finalClassName}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyPress={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
    >
      {title && (
        <h3 className="card__title">
          {title}
        </h3>
      )}
      <div className="card__content">
        {children}
      </div>
    </div>
  )
}

export default Card

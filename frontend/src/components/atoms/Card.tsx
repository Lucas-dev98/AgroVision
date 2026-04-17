import React from 'react'

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
  return (
    <div
      className={`bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow duration-200 ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyPress={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
    >
      {title && (
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          {title}
        </h3>
      )}
      {children}
    </div>
  )
}

export default Card

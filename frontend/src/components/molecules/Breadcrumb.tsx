import React from 'react'
import { Link } from 'react-router-dom'
import './Breadcrumb.css'

export interface BreadcrumbItem {
  label: string
  path?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
  separator?: string
  className?: string
}

const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  separator = '/',
  className = '',
}) => {
  if (!items || items.length === 0) {
    return null
  }

  return (
    <nav
      className={`breadcrumb ${className}`}
      aria-label="Breadcrumb"
    >
      <ol className="breadcrumb__list">
        {items.map((item, index) => {
          const isLast = index === items.length - 1
          const isFirst = index === 0

          return (
            <li
              key={`${item.label}-${index}`}
              className={`breadcrumb__item ${isLast ? 'breadcrumb__item--current' : ''}`}
              aria-current={isLast ? 'page' : undefined}
            >
              {item.path && !isLast ? (
                <Link
                  to={item.path}
                  className="breadcrumb__link"
                  aria-label={`Navigate to ${item.label}`}
                >
                  {item.label}
                </Link>
              ) : (
                <span className="breadcrumb__text">{item.label}</span>
              )}

              {!isLast && (
                <span className="breadcrumb__separator" aria-hidden="true">
                  {separator}
                </span>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

export default Breadcrumb

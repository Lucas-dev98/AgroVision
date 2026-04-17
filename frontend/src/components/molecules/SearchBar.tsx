import React, { useState, useCallback, useEffect } from 'react'
import './SearchBar.css'

interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  disabled?: boolean
  error?: string
  loading?: boolean
  minLength?: number
  debounceMs?: number
}

const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = 'Buscar...',
  disabled = false,
  error = '',
  loading = false,
  minLength = 1,
  debounceMs = 300,
}) => {
  const [value, setValue] = useState('')
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null)

  useEffect(() => {
    // Cleanup timer on unmount
    return () => {
      if (debounceTimer) {
        clearTimeout(debounceTimer)
      }
    }
  }, [debounceTimer])

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value
      setValue(newValue)

      // Clear existing timer
      if (debounceTimer) {
        clearTimeout(debounceTimer)
      }

      // Skip if disabled
      if (disabled || loading) {
        return
      }

      // Set new timer for debounced search
      const timer = setTimeout(() => {
        if (newValue.length >= minLength) {
          onSearch(newValue)
        } else if (newValue.length === 0) {
          // Always search on empty input
          onSearch('')
        }
      }, debounceMs)

      setDebounceTimer(timer)
    },
    [debounceMs, minLength, disabled, loading, onSearch, debounceTimer]
  )

  const handleClear = useCallback(() => {
    setValue('')
    // Clear any pending timer
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    onSearch('')
  }, [onSearch, debounceTimer])

  const containerClass = [
    'search-bar',
    error && 'search-bar--error',
    loading && 'search-bar--loading',
  ]
    .filter(Boolean)
    .join(' ')

  const inputClass = [
    'search-input',
    error && 'search-input--error',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={containerClass}>
      <div className="search-bar__wrapper">
        {/* Search Icon */}
        <svg
          className="search-bar__icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>

        {/* Input */}
        <input
          type="search"
          className={inputClass}
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          disabled={disabled || loading}
          aria-label="Search"
        />

        {/* Loading Spinner */}
        {loading && (
          <div className="search-bar__spinner" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" fill="none" strokeWidth="2" />
            </svg>
          </div>
        )}

        {/* Clear Button */}
        {value && !loading && (
          <button
            className="search-bar__clear"
            onClick={handleClear}
            type="button"
            aria-label="Clear search"
            title="Limpar busca"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" />
            </svg>
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && <div className="search-bar__error">{error}</div>}
    </div>
  )
}

export default SearchBar

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SearchBar from './SearchBar'

describe('SearchBar Component', () => {
  let mockOnSearch: ReturnType<typeof vi.fn>

  beforeEach(() => {
    mockOnSearch = vi.fn()
  })

  describe('Rendering', () => {
    it('should render search input', () => {
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox')
      expect(input).toBeInTheDocument()
    })

    it('should render with placeholder text', () => {
      render(<SearchBar onSearch={mockOnSearch} placeholder="Buscar animais..." />)
      const input = screen.getByPlaceholderText('Buscar animais...')
      expect(input).toBeInTheDocument()
    })

    it('should render with default placeholder if not provided', () => {
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox') as HTMLInputElement
      expect(input.placeholder).toBe('Buscar...')
    })

    it('should render search icon', () => {
      render(<SearchBar onSearch={mockOnSearch} />)
      const icon = screen.getByRole('img', { hidden: true })
      expect(icon).toBeInTheDocument()
    })

    it('should render clear button when has input value', async () => {
      const user = userEvent.setup()
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox')
      
      await user.type(input, 'test')
      const clearBtn = screen.getByRole('button', { name: /clear/i })
      expect(clearBtn).toBeInTheDocument()
    })
  })

  describe('Input Behavior', () => {
    it('should update input value on typing', async () => {
      const user = userEvent.setup()
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox') as HTMLInputElement
      
      await user.type(input, 'gado')
      expect(input.value).toBe('gado')
    })

    it('should call onSearch with debounce after typing', async () => {
      const user = userEvent.setup()
      vi.useFakeTimers()
      
      render(<SearchBar onSearch={mockOnSearch} debounceMs={300} />)
      const input = screen.getByRole('searchbox')
      
      await user.type(input, 'test')
      
      // Não deve chamar imediatamente
      expect(mockOnSearch).not.toHaveBeenCalled()
      
      // Avança o tempo
      vi.advanceTimersByTime(300)
      expect(mockOnSearch).toHaveBeenCalledWith('test')
      
      vi.useRealTimers()
    })

    it('should not call onSearch if value is less than minLength', async () => {
      const user = userEvent.setup()
      vi.useFakeTimers()
      
      render(<SearchBar onSearch={mockOnSearch} minLength={3} debounceMs={300} />)
      const input = screen.getByRole('searchbox')
      
      await user.type(input, 'ab')
      vi.advanceTimersByTime(300)
      
      expect(mockOnSearch).not.toHaveBeenCalled()
      
      vi.useRealTimers()
    })

    it('should call onSearch with correct value when minLength is met', async () => {
      const user = userEvent.setup()
      vi.useFakeTimers()
      
      render(<SearchBar onSearch={mockOnSearch} minLength={2} debounceMs={300} />)
      const input = screen.getByRole('searchbox')
      
      await user.type(input, 'abc')
      vi.advanceTimersByTime(300)
      
      expect(mockOnSearch).toHaveBeenCalledWith('abc')
      
      vi.useRealTimers()
    })
  })

  describe('Clear Button', () => {
    it('should clear input when clear button is clicked', async () => {
      const user = userEvent.setup()
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox') as HTMLInputElement
      
      await user.type(input, 'test')
      expect(input.value).toBe('test')
      
      const clearBtn = screen.getByRole('button', { name: /clear/i })
      await user.click(clearBtn)
      
      expect(input.value).toBe('')
    })

    it('should hide clear button after clearing', async () => {
      const user = userEvent.setup()
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox')
      
      await user.type(input, 'test')
      let clearBtn = screen.getByRole('button', { name: /clear/i })
      expect(clearBtn).toBeInTheDocument()
      
      await user.click(clearBtn)
      clearBtn = screen.queryByRole('button', { name: /clear/i })
      expect(clearBtn).not.toBeInTheDocument()
    })

    it('should call onSearch with empty string when clear button is clicked', async () => {
      const user = userEvent.setup()
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox')
      
      await user.type(input, 'test')
      mockOnSearch.mockClear()
      
      const clearBtn = screen.getByRole('button', { name: /clear/i })
      await user.click(clearBtn)
      
      expect(mockOnSearch).toHaveBeenCalledWith('')
    })
  })

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<SearchBar onSearch={mockOnSearch} disabled />)
      const input = screen.getByRole('searchbox') as HTMLInputElement
      expect(input.disabled).toBe(true)
    })

    it('should not call onSearch when disabled', async () => {
      const user = userEvent.setup()
      vi.useFakeTimers()
      
      render(<SearchBar onSearch={mockOnSearch} disabled debounceMs={300} />)
      const input = screen.getByRole('searchbox') as HTMLInputElement
      
      await user.type(input, 'test')
      vi.advanceTimersByTime(300)
      
      expect(mockOnSearch).not.toHaveBeenCalled()
      
      vi.useRealTimers()
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox')
      expect(input).toHaveAttribute('type', 'search')
    })

    it('should be keyboard accessible', async () => {
      const user = userEvent.setup()
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox')
      
      input.focus()
      expect(input).toHaveFocus()
    })

    it('should support enter key press', async () => {
      const user = userEvent.setup()
      render(<SearchBar onSearch={mockOnSearch} />)
      const input = screen.getByRole('searchbox')
      
      await user.type(input, 'test{Enter}')
      expect(input).toHaveValue('test')
    })
  })

  describe('Error State', () => {
    it('should display error message when error prop is provided', () => {
      render(<SearchBar onSearch={mockOnSearch} error="Erro na busca" />)
      const errorMsg = screen.getByText('Erro na busca')
      expect(errorMsg).toBeInTheDocument()
    })

    it('should have error styling when error prop is provided', () => {
      render(<SearchBar onSearch={mockOnSearch} error="Erro na busca" />)
      const input = screen.getByRole('searchbox')
      expect(input).toHaveClass('search-input--error')
    })
  })

  describe('Loading State', () => {
    it('should show loading indicator when loading prop is true', () => {
      render(<SearchBar onSearch={mockOnSearch} loading />)
      const loader = screen.getByRole('img', { hidden: true, name: /loading|spinner/i })
      expect(loader).toBeInTheDocument()
    })

    it('should disable input when loading', () => {
      render(<SearchBar onSearch={mockOnSearch} loading />)
      const input = screen.getByRole('searchbox') as HTMLInputElement
      expect(input.disabled).toBe(true)
    })
  })

  describe('Styles', () => {
    it('should apply correct CSS classes', () => {
      render(<SearchBar onSearch={mockOnSearch} />)
      const container = screen.getByRole('searchbox').closest('.search-bar')
      expect(container).toHaveClass('search-bar')
    })
  })
})

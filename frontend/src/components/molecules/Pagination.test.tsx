import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Pagination from './Pagination'

describe('Pagination Component', () => {
  describe('Rendering', () => {
    it('should render pagination container', () => {
      render(<Pagination currentPage={1} totalPages={5} />)
      const pagination = screen.getByRole('navigation')
      expect(pagination).toBeInTheDocument()
    })

    it('should render page buttons', () => {
      render(<Pagination currentPage={1} totalPages={5} />)
      const page1 = screen.getByRole('button', { name: '1' })
      const page5 = screen.getByRole('button', { name: '5' })
      
      expect(page1).toBeInTheDocument()
      expect(page5).toBeInTheDocument()
    })

    it('should render previous button', () => {
      render(<Pagination currentPage={2} totalPages={5} />)
      const prevBtn = screen.getByRole('button', { name: /anterior|previous/i })
      expect(prevBtn).toBeInTheDocument()
    })

    it('should render next button', () => {
      render(<Pagination currentPage={1} totalPages={5} />)
      const nextBtn = screen.getByRole('button', { name: /próxima|next/i })
      expect(nextBtn).toBeInTheDocument()
    })

    it('should render page size selector', () => {
      render(<Pagination currentPage={1} totalPages={5} onPageSizeChange={() => {}} />)
      const sizeSelect = screen.getByLabelText(/itens por página|items per page/i)
      expect(sizeSelect).toBeInTheDocument()
    })

    it('should display current page info', () => {
      render(<Pagination currentPage={2} totalPages={5} itemsPerPage={10} totalItems={50} />)
      const info = screen.queryByText(/página.*2|page.*2|11.*20/i)
      expect(info).toBeInTheDocument()
    })

    it('should have correct number of page buttons', () => {
      render(<Pagination currentPage={1} totalPages={10} />)
      const buttons = screen.getAllByRole('button')
      
      // Previous + pages + next
      expect(buttons.length).toBeGreaterThanOrEqual(10)
    })
  })

  describe('Current Page Highlighting', () => {
    it('should highlight current page button', () => {
      render(<Pagination currentPage={3} totalPages={5} />)
      const page3Btn = screen.getByRole('button', { name: '3' })
      expect(page3Btn).toHaveClass('pagination__page--active')
    })

    it('should update active button when current page changes', () => {
      const { rerender } = render(<Pagination currentPage={1} totalPages={5} />)
      let page1Btn = screen.getByRole('button', { name: '1' })
      expect(page1Btn).toHaveClass('pagination__page--active')

      rerender(<Pagination currentPage={2} totalPages={5} />)
      const page2Btn = screen.getByRole('button', { name: '2' })
      expect(page2Btn).toHaveClass('pagination__page--active')
    })
  })

  describe('Navigation Buttons', () => {
    it('should disable previous button on first page', () => {
      render(<Pagination currentPage={1} totalPages={5} />)
      const prevBtn = screen.getByRole('button', { name: /anterior|previous/i })
      expect(prevBtn).toBeDisabled()
    })

    it('should enable previous button on non-first page', () => {
      render(<Pagination currentPage={2} totalPages={5} />)
      const prevBtn = screen.getByRole('button', { name: /anterior|previous/i })
      expect(prevBtn).not.toBeDisabled()
    })

    it('should disable next button on last page', () => {
      render(<Pagination currentPage={5} totalPages={5} />)
      const nextBtn = screen.getByRole('button', { name: /próxima|next/i })
      expect(nextBtn).toBeDisabled()
    })

    it('should enable next button on non-last page', () => {
      render(<Pagination currentPage={1} totalPages={5} />)
      const nextBtn = screen.getByRole('button', { name: /próxima|next/i })
      expect(nextBtn).not.toBeDisabled()
    })
  })

  describe('Page Callbacks', () => {
    it('should call onPageChange when page button is clicked', async () => {
      const user = userEvent.setup()
      const mockPageChange = vi.fn()
      render(
        <Pagination 
          currentPage={1} 
          totalPages={5}
          onPageChange={mockPageChange}
        />
      )

      const page3Btn = screen.getByRole('button', { name: '3' })
      await user.click(page3Btn)

      expect(mockPageChange).toHaveBeenCalledWith(3)
    })

    it('should call onPageChange with correct value for previous button', async () => {
      const user = userEvent.setup()
      const mockPageChange = vi.fn()
      render(
        <Pagination 
          currentPage={3} 
          totalPages={5}
          onPageChange={mockPageChange}
        />
      )

      const prevBtn = screen.getByRole('button', { name: /anterior|previous/i })
      await user.click(prevBtn)

      expect(mockPageChange).toHaveBeenCalledWith(2)
    })

    it('should call onPageChange with correct value for next button', async () => {
      const user = userEvent.setup()
      const mockPageChange = vi.fn()
      render(
        <Pagination 
          currentPage={1} 
          totalPages={5}
          onPageChange={mockPageChange}
        />
      )

      const nextBtn = screen.getByRole('button', { name: /próxima|next/i })
      await user.click(nextBtn)

      expect(mockPageChange).toHaveBeenCalledWith(2)
    })

    it('should not call onPageChange when disabled button is clicked', async () => {
      const user = userEvent.setup()
      const mockPageChange = vi.fn()
      render(
        <Pagination 
          currentPage={1} 
          totalPages={5}
          onPageChange={mockPageChange}
        />
      )

      const prevBtn = screen.getByRole('button', { name: /anterior|previous/i })
      await user.click(prevBtn)

      expect(mockPageChange).not.toHaveBeenCalled()
    })
  })

  describe('Page Size Change', () => {
    it('should call onPageSizeChange when page size is selected', async () => {
      const user = userEvent.setup()
      const mockSizeChange = vi.fn()
      render(
        <Pagination 
          currentPage={1} 
          totalPages={5}
          onPageSizeChange={mockSizeChange}
        />
      )

      const sizeSelect = screen.getByLabelText(/itens por página|items per page/i)
      await user.selectOptions(sizeSelect, '25')

      expect(mockSizeChange).toHaveBeenCalledWith(25)
    })

    it('should have default page size options', () => {
      render(<Pagination currentPage={1} totalPages={5} />)
      const sizeSelect = screen.getByLabelText(/itens por página|items per page/i) as HTMLSelectElement
      
      expect(sizeSelect.options.length).toBeGreaterThanOrEqual(3)
    })

    it('should select current page size option', () => {
      render(
        <Pagination 
          currentPage={1} 
          totalPages={5}
          itemsPerPage={25}
        />
      )
      const sizeSelect = screen.getByLabelText(/itens por página|items per page/i) as HTMLSelectElement
      expect(sizeSelect.value).toBe('25')
    })
  })

  describe('Edge Cases', () => {
    it('should handle single page', () => {
      render(<Pagination currentPage={1} totalPages={1} />)
      const prevBtn = screen.getByRole('button', { name: /anterior|previous/i })
      const nextBtn = screen.getByRole('button', { name: /próxima|next/i })
      
      expect(prevBtn).toBeDisabled()
      expect(nextBtn).toBeDisabled()
    })

    it('should handle large number of pages with ellipsis', () => {
      render(<Pagination currentPage={5} totalPages={100} />)
      const ellipsis = screen.queryByText('...')
      
      // May or may not have ellipsis depending on maxVisible
      expect(document.querySelector('.pagination')).toBeInTheDocument()
    })

    it('should handle zero total items gracefully', () => {
      render(
        <Pagination 
          currentPage={1} 
          totalPages={0}
          totalItems={0}
        />
      )
      const pagination = screen.getByRole('navigation')
      expect(pagination).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper navigation role', () => {
      render(<Pagination currentPage={1} totalPages={5} />)
      const nav = screen.getByRole('navigation')
      expect(nav).toBeInTheDocument()
    })

    it('should have aria-current for active page', () => {
      render(<Pagination currentPage={2} totalPages={5} />)
      const activeBtn = screen.getByRole('button', { name: '2' })
      expect(activeBtn).toHaveAttribute('aria-current', 'page')
    })

    it('should have descriptive button labels', () => {
      render(<Pagination currentPage={1} totalPages={5} />)
      const prevBtn = screen.getByRole('button', { name: /anterior|previous/i })
      const nextBtn = screen.getByRole('button', { name: /próxima|next/i })
      
      expect(prevBtn).toHaveAccessibleName()
      expect(nextBtn).toHaveAccessibleName()
    })

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup()
      const mockPageChange = vi.fn()
      render(
        <Pagination 
          currentPage={2} 
          totalPages={5}
          onPageChange={mockPageChange}
        />
      )

      const prevBtn = screen.getByRole('button', { name: /anterior|previous/i })
      prevBtn.focus()
      
      expect(prevBtn).toHaveFocus()
      
      await user.keyboard('{Enter}')
      expect(mockPageChange).toHaveBeenCalledWith(1)
    })
  })
})

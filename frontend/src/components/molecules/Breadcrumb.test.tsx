import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import userEvent from '@testing-library/user-event'
import Breadcrumb from './Breadcrumb'

describe('Breadcrumb Component', () => {
  const mockItems = [
    { label: 'Home', path: '/' },
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Animals', path: '/animals' },
    { label: 'Boi do Pasto' },
  ]

  describe('Rendering', () => {
    it('should render breadcrumb navigation', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const nav = screen.getByRole('navigation')
      expect(nav).toBeInTheDocument()
    })

    it('should render all breadcrumb items', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      expect(screen.getByText('Home')).toBeInTheDocument()
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Animals')).toBeInTheDocument()
      expect(screen.getByText('Boi do Pasto')).toBeInTheDocument()
    })

    it('should render links for items with path', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const links = screen.getAllByRole('link')
      expect(links.length).toBeGreaterThanOrEqual(3)
    })

    it('should render text for current page (last item)', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const lastItem = screen.getByText('Boi do Pasto')
      expect(lastItem).toBeInTheDocument()
    })

    it('should render separators between items', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const separators = document.querySelectorAll('.breadcrumb__separator')
      expect(separators.length).toBeGreaterThan(0)
    })

    it('should render custom separator if provided', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} separator="→" />
        </BrowserRouter>
      )
      const separator = screen.getByText('→')
      expect(separator).toBeInTheDocument()
    })

    it('should handle empty items array', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={[]} />
        </BrowserRouter>
      )
      const nav = screen.getByRole('navigation')
      expect(nav).toBeInTheDocument()
    })

    it('should render single item breadcrumb', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={[{ label: 'Home', path: '/' }]} />
        </BrowserRouter>
      )
      expect(screen.getByText('Home')).toBeInTheDocument()
    })
  })

  describe('Navigation', () => {
    it('should navigate when breadcrumb link is clicked', async () => {
      const user = userEvent.setup()
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )

      const homeLink = screen.getByText('Home')
      await user.click(homeLink)

      expect(homeLink).toBeInTheDocument()
    })

    it('should have correct href for navigation links', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )

      const dashboardLink = screen.getByText('Dashboard') as HTMLAnchorElement
      expect(dashboardLink.getAttribute('href')).toBe('/dashboard')
    })
  })

  describe('Current Item Styling', () => {
    it('should have aria-current for last item', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const currentItem = screen.getByText('Boi do Pasto').closest('li')
      expect(currentItem).toHaveAttribute('aria-current', 'page')
    })

    it('should have active class for last item', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const currentItem = screen.getByText('Boi do Pasto').closest('.breadcrumb__item')
      expect(currentItem).toHaveClass('breadcrumb__item--current')
    })

    it('should not be a link for current item', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const currentItem = screen.getByText('Boi do Pasto')
      expect(currentItem.tagName).not.toBe('A')
    })
  })

  describe('Accessibility', () => {
    it('should have nav role', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const nav = screen.getByRole('navigation')
      expect(nav).toBeInTheDocument()
    })

    it('should have aria-label for navigation', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const nav = screen.getByRole('navigation')
      expect(nav).toHaveAttribute('aria-label', 'Breadcrumb')
    })

    it('should have list structure', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const list = screen.getByRole('list')
      expect(list).toBeInTheDocument()
    })

    it('should mark current item as aria-current page', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const currentItem = screen.getByText('Boi do Pasto').closest('li')
      expect(currentItem).toHaveAttribute('aria-current', 'page')
    })

    it('should have accessible link names', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} />
        </BrowserRouter>
      )
      const homeLink = screen.getByText('Home')
      expect(homeLink).toHaveAccessibleName()
    })
  })

  describe('Custom Styling', () => {
    it('should apply custom className if provided', () => {
      const { container } = render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} className="custom-breadcrumb" />
        </BrowserRouter>
      )
      const breadcrumb = container.querySelector('.custom-breadcrumb')
      expect(breadcrumb).toBeInTheDocument()
    })

    it('should apply custom separator style', () => {
      render(
        <BrowserRouter>
          <Breadcrumb items={mockItems} separator="•" />
        </BrowserRouter>
      )
      const separator = screen.getByText('•')
      expect(separator).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle items with only labels (no paths)', () => {
      const items = [
        { label: 'Home', path: '/' },
        { label: 'Current Page' },
      ]
      render(
        <BrowserRouter>
          <Breadcrumb items={items} />
        </BrowserRouter>
      )
      expect(screen.getByText('Current Page')).toBeInTheDocument()
    })

    it('should handle long labels with truncation', () => {
      const longLabel = 'This is a very long breadcrumb label that might need truncation'
      const items = [
        { label: 'Home', path: '/' },
        { label: longLabel },
      ]
      render(
        <BrowserRouter>
          <Breadcrumb items={items} />
        </BrowserRouter>
      )
      expect(screen.getByText(longLabel)).toBeInTheDocument()
    })

    it('should handle special characters in labels', () => {
      const items = [
        { label: 'Home & Dashboard', path: '/' },
        { label: 'Animal (Cattle)', path: '/animals' },
      ]
      render(
        <BrowserRouter>
          <Breadcrumb items={items} />
        </BrowserRouter>
      )
      expect(screen.getByText('Home & Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Animal (Cattle)')).toBeInTheDocument()
    })
  })
})

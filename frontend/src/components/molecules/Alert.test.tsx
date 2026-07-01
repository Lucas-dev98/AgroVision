import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Alert from './Alert'

describe('Alert Component', () => {
  describe('Rendering', () => {
    it('should not render alert when isOpen is false', () => {
      render(<Alert isOpen={false} message="Test message" />)
      expect(screen.queryByRole('status')).not.toBeInTheDocument()
    })

    it('should render alert when isOpen is true', () => {
      render(<Alert isOpen={true} message="Test message" type="success" />)
      expect(screen.getByRole('status')).toBeInTheDocument()
    })

    it('should display alert message', () => {
      render(<Alert isOpen={true} message="Test message content" type="success" />)
      expect(screen.getByText('Test message content')).toBeInTheDocument()
    })

    it('should render close button when dismissible', () => {
      render(<Alert isOpen={true} message="Test" type="success" dismissible />)
      const closeBtn = screen.getByRole('button', { name: /fechar|close|×/i })
      expect(closeBtn).toBeInTheDocument()
    })

    it('should not render close button when not dismissible', () => {
      render(<Alert isOpen={true} message="Test" type="success" dismissible={false} />)
      const closeBtn = screen.queryByRole('button', { name: /fechar|close|×/i })
      expect(closeBtn).not.toBeInTheDocument()
    })

    it('should render title if provided', () => {
      render(
        <Alert 
          isOpen={true} 
          title="Alert Title"
          message="Test message" 
          type="info" 
        />
      )
      expect(screen.getByText('Alert Title')).toBeInTheDocument()
    })
  })

  describe('Alert Types', () => {
    it('should render success alert with correct class', () => {
      render(<Alert isOpen={true} message="Success!" type="success" />)
      const alert = screen.getByRole('status')
      expect(alert).toHaveClass('alert--success')
    })

    it('should render error alert with correct class', () => {
      render(<Alert isOpen={true} message="Error!" type="error" />)
      const alert = screen.getByRole('status')
      expect(alert).toHaveClass('alert--error')
    })

    it('should render warning alert with correct class', () => {
      render(<Alert isOpen={true} message="Warning!" type="warning" />)
      const alert = screen.getByRole('status')
      expect(alert).toHaveClass('alert--warning')
    })

    it('should render info alert with correct class', () => {
      render(<Alert isOpen={true} message="Info!" type="info" />)
      const alert = screen.getByRole('status')
      expect(alert).toHaveClass('alert--info')
    })
  })

  describe('Close Functionality', () => {
    it('should call onClose when close button is clicked', async () => {
      const user = userEvent.setup()
      const mockClose = vi.fn()
      render(
        <Alert 
          isOpen={true} 
          message="Test" 
          type="success"
          dismissible
          onClose={mockClose}
        />
      )

      const closeBtn = screen.getByRole('button', { name: /fechar|close|×/i })
      await user.click(closeBtn)

      expect(mockClose).toHaveBeenCalled()
    })

    it('should auto-dismiss after specified duration', async () => {
      const mockClose = vi.fn()
      render(
        <Alert 
          isOpen={true} 
          message="Test" 
          type="success"
          autoDismissMs={100}
          onClose={mockClose}
        />
      )

      await waitFor(() => {
        expect(mockClose).toHaveBeenCalled()
      }, { timeout: 200 })
    })

    it('should not auto-dismiss if autoDismissMs is 0 or undefined', async () => {
      const mockClose = vi.fn()
      render(
        <Alert 
          isOpen={true} 
          message="Test" 
          type="success"
          autoDismissMs={0}
          onClose={mockClose}
        />
      )

      // Wait a bit
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(mockClose).not.toHaveBeenCalled()
    })
  })

  describe('Auto-dismiss Behavior', () => {
    it('should clear auto-dismiss on mouse enter', async () => {
      const user = userEvent.setup()
      const mockClose = vi.fn()
      render(
        <Alert 
          isOpen={true} 
          message="Test" 
          type="success"
          autoDismissMs={100}
          onClose={mockClose}
        />
      )

      const alert = screen.getByRole('status')
      await user.hover(alert)

      // Wait but it should not dismiss due to hover
      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(mockClose).not.toHaveBeenCalled()
    })

    it('should resume auto-dismiss on mouse leave', async () => {
      const user = userEvent.setup()
      const mockClose = vi.fn()
      render(
        <Alert 
          isOpen={true} 
          message="Test" 
          type="success"
          autoDismissMs={100}
          onClose={mockClose}
        />
      )

      const alert = screen.getByRole('status')
      await user.hover(alert)
      await user.unhover(alert)

      await waitFor(() => {
        expect(mockClose).toHaveBeenCalled()
      }, { timeout: 200 })
    })
  })

  describe('Positioning', () => {
    it('should render with default top-right position', () => {
      render(<Alert isOpen={true} message="Test" type="success" />)
      const alert = screen.getByRole('status')
      expect(alert.parentElement).toHaveClass('alert__container--top-right')
    })

    it('should render with custom position', () => {
      render(
        <Alert 
          isOpen={true} 
          message="Test" 
          type="success"
          position="bottom-left"
        />
      )
      const alert = screen.getByRole('status')
      expect(alert.parentElement).toHaveClass('alert__container--bottom-left')
    })
  })

  describe('Accessibility', () => {
    it('should have status role for live announcements', () => {
      render(<Alert isOpen={true} message="Success message" type="success" />)
      const alert = screen.getByRole('status')
      expect(alert).toBeInTheDocument()
    })

    it('should have aria-label if provided', () => {
      render(
        <Alert 
          isOpen={true} 
          message="Test" 
          type="success"
          ariaLabel="Success notification"
        />
      )
      const alert = screen.getByRole('status')
      expect(alert).toHaveAttribute('aria-label', 'Success notification')
    })

    it('should have aria-live polite for status updates', () => {
      render(<Alert isOpen={true} message="Test" type="info" />)
      const alert = screen.getByRole('status')
      expect(alert).toHaveAttribute('aria-live', 'polite')
    })

    it('should have aria-live assertive for errors', () => {
      render(<Alert isOpen={true} message="Error!" type="error" />)
      const alert = screen.getByRole('status')
      expect(alert).toHaveAttribute('aria-live', 'assertive')
    })
  })

  describe('Icons', () => {
    it('should render icon for each alert type', () => {
      const { rerender } = render(
        <Alert isOpen={true} message="Success" type="success" />
      )
      let icon = document.querySelector('.alert__icon')
      expect(icon).toBeInTheDocument()

      rerender(<Alert isOpen={true} message="Error" type="error" />)
      icon = document.querySelector('.alert__icon')
      expect(icon).toBeInTheDocument()
    })

    it('should hide icon if showIcon is false', () => {
      render(
        <Alert 
          isOpen={true} 
          message="Test" 
          type="success"
          showIcon={false}
        />
      )
      const icon = document.querySelector('.alert__icon')
      expect(icon).not.toBeInTheDocument()
    })
  })

  describe('Multiple Alerts', () => {
    it('should render multiple alerts independently', () => {
      render(
        <>
          <Alert isOpen={true} message="Success" type="success" />
          <Alert isOpen={true} message="Error" type="error" />
        </>
      )
      expect(screen.getByText('Success')).toBeInTheDocument()
      expect(screen.getByText('Error')).toBeInTheDocument()
    })
  })
})

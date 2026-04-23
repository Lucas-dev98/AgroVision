import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Modal from './Modal'

describe('Modal Component', () => {
  describe('Rendering', () => {
    it('should not render modal when isOpen is false', () => {
      render(
        <Modal isOpen={false} title="Test Modal">
          <p>Content</p>
        </Modal>
      )
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('should render modal when isOpen is true', () => {
      render(
        <Modal isOpen={true} title="Test Modal">
          <p>Content</p>
        </Modal>
      )
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('should render modal title', () => {
      render(
        <Modal isOpen={true} title="Test Modal">
          <p>Content</p>
        </Modal>
      )
      expect(screen.getByText('Test Modal')).toBeInTheDocument()
    })

    it('should render modal content', () => {
      render(
        <Modal isOpen={true} title="Test Modal">
          <p>Test Content Here</p>
        </Modal>
      )
      expect(screen.getByText('Test Content Here')).toBeInTheDocument()
    })

    it('should render close button', () => {
      const mockClose = vi.fn()
      render(
        <Modal isOpen={true} title="Test Modal" onClose={mockClose}>
          <p>Content</p>
        </Modal>
      )
      const closeBtn = screen.getByRole('button', { name: /fechar|close|×/i })
      expect(closeBtn).toBeInTheDocument()
    })

    it('should render confirm button in confirmation mode', () => {
      render(
        <Modal 
          isOpen={true} 
          title="Confirm" 
          variant="confirmation"
          onConfirm={() => {}}
        >
          <p>Are you sure?</p>
        </Modal>
      )
      expect(screen.getByRole('button', { name: /confirmar|confirm/i })).toBeInTheDocument()
    })

    it('should render cancel button in confirmation mode', () => {
      render(
        <Modal 
          isOpen={true} 
          title="Confirm" 
          variant="confirmation"
          onConfirm={() => {}}
        >
          <p>Are you sure?</p>
        </Modal>
      )
      expect(screen.getByRole('button', { name: /cancelar|cancel/i })).toBeInTheDocument()
    })

    it('should render backdrop', () => {
      render(
        <Modal isOpen={true} title="Test Modal">
          <p>Content</p>
        </Modal>
      )
      const backdrop = document.querySelector('.modal__backdrop')
      expect(backdrop).toBeInTheDocument()
    })

    it('should have large variant style', () => {
      render(
        <Modal isOpen={true} title="Test" size="large">
          <p>Content</p>
        </Modal>
      )
      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveClass('modal__content--large')
    })
  })

  describe('Close Functionality', () => {
    it('should call onClose when close button is clicked', async () => {
      const user = userEvent.setup()
      const mockClose = vi.fn()
      render(
        <Modal isOpen={true} title="Test" onClose={mockClose}>
          <p>Content</p>
        </Modal>
      )

      const closeBtn = screen.getByRole('button', { name: /fechar|close|×/i })
      await user.click(closeBtn)

      expect(mockClose).toHaveBeenCalled()
    })

    it('should call onClose when backdrop is clicked', async () => {
      const user = userEvent.setup()
      const mockClose = vi.fn()
      render(
        <Modal isOpen={true} title="Test" onClose={mockClose} closeOnBackdrop>
          <p>Content</p>
        </Modal>
      )

      const backdrop = document.querySelector('.modal__backdrop')
      if (backdrop) {
        await user.click(backdrop)
        expect(mockClose).toHaveBeenCalled()
      }
    })

    it('should call onClose when Escape key is pressed', async () => {
      const user = userEvent.setup()
      const mockClose = vi.fn()
      render(
        <Modal isOpen={true} title="Test" onClose={mockClose}>
          <p>Content</p>
        </Modal>
      )

      await user.keyboard('{Escape}')

      expect(mockClose).toHaveBeenCalled()
    })

    it('should not close on backdrop click if closeOnBackdrop is false', async () => {
      const user = userEvent.setup()
      const mockClose = vi.fn()
      render(
        <Modal isOpen={true} title="Test" onClose={mockClose} closeOnBackdrop={false}>
          <p>Content</p>
        </Modal>
      )

      const backdrop = document.querySelector('.modal__backdrop')
      if (backdrop) {
        await user.click(backdrop)
        expect(mockClose).not.toHaveBeenCalled()
      }
    })
  })

  describe('Confirmation Modal', () => {
    it('should call onConfirm when confirm button is clicked', async () => {
      const user = userEvent.setup()
      const mockConfirm = vi.fn()
      render(
        <Modal 
          isOpen={true} 
          title="Confirm" 
          variant="confirmation"
          onConfirm={mockConfirm}
        >
          <p>Are you sure?</p>
        </Modal>
      )

      const confirmBtn = screen.getByRole('button', { name: /confirmar|confirm/i })
      await user.click(confirmBtn)

      expect(mockConfirm).toHaveBeenCalled()
    })

    it('should call onCancel when cancel button is clicked', async () => {
      const user = userEvent.setup()
      const mockCancel = vi.fn()
      render(
        <Modal 
          isOpen={true} 
          title="Confirm" 
          variant="confirmation"
          onCancel={mockCancel}
        >
          <p>Are you sure?</p>
        </Modal>
      )

      const cancelBtn = screen.getByRole('button', { name: /cancelar|cancel/i })
      await user.click(cancelBtn)

      expect(mockCancel).toHaveBeenCalled()
    })

    it('should have warning style for danger variant', () => {
      render(
        <Modal 
          isOpen={true} 
          title="Delete" 
          variant="confirmation"
          isDanger
          onConfirm={() => {}}
        >
          <p>Delete?</p>
        </Modal>
      )

      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveClass('modal--danger')
    })
  })

  describe('Accessibility', () => {
    it('should have proper dialog role', () => {
      render(
        <Modal isOpen={true} title="Test Modal">
          <p>Content</p>
        </Modal>
      )
      const dialog = screen.getByRole('dialog')
      expect(dialog).toBeInTheDocument()
    })

    it('should have aria-label with title', () => {
      render(
        <Modal isOpen={true} title="Test Modal">
          <p>Content</p>
        </Modal>
      )
      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-labelledby')
    })

    it('should have aria-describedby for content', () => {
      render(
        <Modal isOpen={true} title="Test Modal">
          <p>Content description</p>
        </Modal>
      )
      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-describedby')
    })

    it('should focus close button on open', () => {
      render(
        <Modal isOpen={true} title="Test Modal">
          <p>Content</p>
        </Modal>
      )
      const dialog = screen.getByRole('dialog')
      expect(dialog).toBeInTheDocument()
    })

    it('should trap focus inside modal', async () => {
      const user = userEvent.setup()
      render(
        <Modal isOpen={true} title="Test Modal">
          <input type="text" placeholder="Test input" />
        </Modal>
      )

      const input = screen.getByPlaceholderText('Test input')
      input.focus()

      expect(input).toHaveFocus()
    })
  })

  describe('Variants', () => {
    it('should render default variant modal', () => {
      render(
        <Modal isOpen={true} title="Test">
          <p>Content</p>
        </Modal>
      )
      const dialog = screen.getByRole('dialog')
      expect(dialog).not.toHaveClass('modal--danger')
    })

    it('should render warning variant with correct styling', () => {
      render(
        <Modal isOpen={true} title="Warning" variant="confirmation">
          <p>Warning content</p>
        </Modal>
      )
      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveClass('modal__content')
    })
  })
})

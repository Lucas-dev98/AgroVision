import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import userEvent from '@testing-library/user-event'
import AnimalDetail from './AnimalDetail'

describe('AnimalDetail Organism', () => {
  const mockAnimal = {
    id: '1',
    nome: 'Boi do Pasto',
    raca: 'Nelore',
    rfid: 'RF00000001',
    status: 'ativo' as const,
    peso_inicial: 450,
    sexo: 'M' as const,
    data_nascimento: '2021-01-15T00:00:00Z',
  }

  const mockBreadcrumbs = [
    { label: 'Rebanho', path: '/animals' },
    { label: mockAnimal.nome },
  ]

  describe('Rendering', () => {
    it('should render page container', () => {
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )
      expect(screen.getByRole('region')).toBeInTheDocument()
    })

    it('should render breadcrumb navigation', () => {
      const { container } = render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )
      const breadcrumb = container.querySelector('.animal-detail__breadcrumb')
      expect(breadcrumb).toBeInTheDocument()
    })

    it('should render animal card', () => {
      const { container } = render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )
      const card = container.querySelector('.animal-detail__card')
      expect(card).toBeInTheDocument()
    })

    it('should render edit form', () => {
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )
      const editBtn = screen.getByRole('button', { name: /editar|edit/i })
      expect(editBtn).toBeInTheDocument()
    })

    it('should render action buttons', () => {
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )
      expect(screen.getByRole('button', { name: /editar|edit/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /deletar|delete/i })).toBeInTheDocument()
    })

    it('should render loading state', () => {
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} isLoading={true} />
        </BrowserRouter>
      )
      const loading = screen.getByText(/carregando|loading/i)
      expect(loading).toBeInTheDocument()
    })

    it('should render error message when error exists', () => {
      render(
        <BrowserRouter>
          <AnimalDetail 
            animal={mockAnimal} 
            breadcrumbs={mockBreadcrumbs}
            error="Erro ao carregar"
          />
        </BrowserRouter>
      )
      const errorMsg = screen.getByText('Erro ao carregar')
      expect(errorMsg).toBeInTheDocument()
    })
  })

  describe('Edit Mode', () => {
    it('should enable edit mode when edit button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )

      const editBtn = screen.getByRole('button', { name: /editar|edit/i })
      await user.click(editBtn)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /salvar|save/i })).toBeInTheDocument()
      })
    })

    it('should show cancel button in edit mode', async () => {
      const user = userEvent.setup()
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )

      const editBtn = screen.getByRole('button', { name: /editar|edit/i })
      await user.click(editBtn)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /cancelar|cancel/i })).toBeInTheDocument()
      })
    })

    it('should call onSave when save button is clicked', async () => {
      const user = userEvent.setup()
      const mockSave = vi.fn()
      render(
        <BrowserRouter>
          <AnimalDetail 
            animal={mockAnimal} 
            breadcrumbs={mockBreadcrumbs}
            onSave={mockSave}
          />
        </BrowserRouter>
      )

      const editBtn = screen.getByRole('button', { name: /editar|edit/i })
      await user.click(editBtn)

      const saveBtn = await screen.findByRole('button', { name: /salvar|save/i })
      await user.click(saveBtn)

      expect(mockSave).toHaveBeenCalled()
    })

    it('should exit edit mode when cancel is clicked', async () => {
      const user = userEvent.setup()
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )

      const editBtn = screen.getByRole('button', { name: /editar|edit/i })
      await user.click(editBtn)

      const cancelBtn = await screen.findByRole('button', { name: /cancelar|cancel/i })
      await user.click(cancelBtn)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /editar|edit/i })).toBeInTheDocument()
      })
    })
  })

  describe('Delete Functionality', () => {
    it('should show delete confirmation modal when delete button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )

      const deleteBtn = screen.getByRole('button', { name: /deletar|delete/i })
      await user.click(deleteBtn)

      await waitFor(() => {
        expect(screen.getByText(/certeza|sure/i)).toBeInTheDocument()
      })
    })

    it('should call onDelete when deletion is confirmed', async () => {
      const user = userEvent.setup()
      const mockDelete = vi.fn()
      render(
        <BrowserRouter>
          <AnimalDetail 
            animal={mockAnimal} 
            breadcrumbs={mockBreadcrumbs}
            onDelete={mockDelete}
          />
        </BrowserRouter>
      )

      const deleteBtn = screen.getByRole('button', { name: /deletar|delete/i })
      await user.click(deleteBtn)

      const confirmBtn = await screen.findByRole('button', { name: /deletar|delete/i })
      await user.click(confirmBtn)

      expect(mockDelete).toHaveBeenCalledWith(mockAnimal.id)
    })

    it('should close modal when canceling delete', async () => {
      const user = userEvent.setup()
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )

      const deleteBtn = screen.getByRole('button', { name: /deletar|delete/i })
      await user.click(deleteBtn)

      const cancelBtn = await screen.findByRole('button', { name: /cancelar|cancel/i })
      await user.click(cancelBtn)

      await waitFor(() => {
        expect(screen.queryByText(/certeza|sure/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('Layout', () => {
    it('should render two-column layout on large screens', () => {
      const { container } = render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )
      const layout = container.querySelector('.animal-detail__content')
      expect(layout).toBeInTheDocument()
    })

    it('should render card with animal information', () => {
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )
      expect(screen.getByText(mockAnimal.rfid)).toBeInTheDocument()
    })
  })

  describe('Alerts', () => {
    it('should show success alert on save', async () => {
      const user = userEvent.setup()
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )

      const editBtn = screen.getByRole('button', { name: /editar|edit/i })
      await user.click(editBtn)

      const saveBtn = await screen.findByRole('button', { name: /salvar|save/i })
      await user.click(saveBtn)

      await waitFor(() => {
        expect(screen.getByText(/sucesso|success|salvo/i)).toBeInTheDocument()
      }, { timeout: 3000 })
    })

    it('should show error alert on delete failure', async () => {
      const user = userEvent.setup()
      const mockDelete = vi.fn().mockRejectedValue(new Error('Delete failed'))
      render(
        <BrowserRouter>
          <AnimalDetail 
            animal={mockAnimal} 
            breadcrumbs={mockBreadcrumbs}
            onDelete={mockDelete}
          />
        </BrowserRouter>
      )

      const deleteBtn = screen.getByRole('button', { name: /deletar|delete/i })
      await user.click(deleteBtn)

      const confirmBtn = await screen.findByRole('button', { name: /deletar|delete/i })
      await user.click(confirmBtn)

      await waitFor(() => {
        expect(screen.getByText(/erro|error|falha/i)).toBeInTheDocument()
      }, { timeout: 3000 })
    })
  })

  describe('Accessibility', () => {
    it('should have region role for main content', () => {
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )
      expect(screen.getByRole('region')).toBeInTheDocument()
    })

    it('should have proper heading hierarchy', () => {
      render(
        <BrowserRouter>
          <AnimalDetail animal={mockAnimal} breadcrumbs={mockBreadcrumbs} />
        </BrowserRouter>
      )
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
    })
  })
})

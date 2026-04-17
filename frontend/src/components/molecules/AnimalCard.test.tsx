import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AnimalCard from './AnimalCard'

describe('AnimalCard Component', () => {
  const mockAnimal = {
    id: '507f1f77bcf86cd799439011',
    nome: 'Boi do Pasto',
    raca: 'Nelore',
    rfid: 'RF12345678',
    status: 'ativo',
    peso_inicial: 450,
    sexo: 'M',
    data_nascimento: new Date('2021-01-15').toISOString(),
  }

  describe('Rendering', () => {
    it('should render animal card', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const card = screen.getByRole('article')
      expect(card).toBeInTheDocument()
    })

    it('should display animal name', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const name = screen.getByText('Boi do Pasto')
      expect(name).toBeInTheDocument()
    })

    it('should display animal breed', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const breed = screen.getByText(/Nelore/i)
      expect(breed).toBeInTheDocument()
    })

    it('should display RFID', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const rfid = screen.getByText(/RF12345678/i)
      expect(rfid).toBeInTheDocument()
    })

    it('should display status badge', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const status = screen.getByText(/ativo/i)
      expect(status).toBeInTheDocument()
    })

    it('should display initial weight', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const weight = screen.getByText(/450 kg/i) || screen.getByText(/450/)
      expect(weight).toBeInTheDocument()
    })

    it('should display gender', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const gender = screen.getByText(/Macho|M/)
      expect(gender).toBeInTheDocument()
    })

    it('should display action buttons', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const editBtn = screen.getByRole('button', { name: /editar|edit/i })
      const deleteBtn = screen.getByRole('button', { name: /deletar|delete|remover/i })
      
      expect(editBtn).toBeInTheDocument()
      expect(deleteBtn).toBeInTheDocument()
    })
  })

  describe('Status Badge Colors', () => {
    it('should display green badge for active status', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const badge = screen.getByText(/ativo/i).closest('.animal-card__status')
      expect(badge).toHaveClass('animal-card__status--active')
    })

    it('should display yellow badge for inactive status', () => {
      const inactiveAnimal = { ...mockAnimal, status: 'inativo' }
      render(<AnimalCard animal={inactiveAnimal} />)
      const badge = screen.getByText(/inativo/i).closest('.animal-card__status')
      expect(badge).toHaveClass('animal-card__status--inactive')
    })

    it('should display red badge for sold status', () => {
      const soldAnimal = { ...mockAnimal, status: 'vendido' }
      render(<AnimalCard animal={soldAnimal} />)
      const badge = screen.getByText(/vendido/i).closest('.animal-card__status')
      expect(badge).toHaveClass('animal-card__status--sold')
    })
  })

  describe('Callbacks', () => {
    it('should call onEdit when edit button is clicked', async () => {
      const user = userEvent.setup()
      const mockEdit = vi.fn()
      render(<AnimalCard animal={mockAnimal} onEdit={mockEdit} />)
      
      const editBtn = screen.getByRole('button', { name: /editar|edit/i })
      await user.click(editBtn)
      
      expect(mockEdit).toHaveBeenCalledWith(mockAnimal)
    })

    it('should call onDelete when delete button is clicked', async () => {
      const user = userEvent.setup()
      const mockDelete = vi.fn()
      render(<AnimalCard animal={mockAnimal} onDelete={mockDelete} />)
      
      const deleteBtn = screen.getByRole('button', { name: /deletar|delete|remover/i })
      await user.click(deleteBtn)
      
      expect(mockDelete).toHaveBeenCalledWith(mockAnimal.id)
    })

    it('should call onClick when card is clicked', async () => {
      const user = userEvent.setup()
      const mockClick = vi.fn()
      render(<AnimalCard animal={mockAnimal} onClick={mockClick} />)
      
      const card = screen.getByRole('article')
      await user.click(card)
      
      expect(mockClick).toHaveBeenCalledWith(mockAnimal)
    })
  })

  describe('Hover Effects', () => {
    it('should apply hover class on mouse over', async () => {
      const user = userEvent.setup()
      render(<AnimalCard animal={mockAnimal} />)
      
      const card = screen.getByRole('article')
      await user.hover(card)
      
      expect(card).toHaveClass('animal-card--hover')
    })
  })

  describe('Responsive', () => {
    it('should render with responsive layout', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const card = screen.getByRole('article')
      expect(card).toHaveClass('animal-card')
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA role', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const card = screen.getByRole('article')
      expect(card).toBeInTheDocument()
    })

    it('should have semantic heading', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const heading = screen.getByRole('heading', { level: 3 })
      expect(heading).toHaveTextContent('Boi do Pasto')
    })

    it('should have button labels for action buttons', () => {
      render(<AnimalCard animal={mockAnimal} />)
      const editBtn = screen.getByRole('button', { name: /editar|edit/i })
      const deleteBtn = screen.getByRole('button', { name: /deletar|delete|remover/i })
      
      expect(editBtn).toHaveAccessibleName()
      expect(deleteBtn).toHaveAccessibleName()
    })
  })
})

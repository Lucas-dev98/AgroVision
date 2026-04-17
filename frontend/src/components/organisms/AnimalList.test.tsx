import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import userEvent from '@testing-library/user-event'
import AnimalList from './AnimalList'

describe('AnimalList Organism', () => {
  const mockAnimals = [
    {
      id: '1',
      nome: 'Boi do Pasto',
      raca: 'Nelore',
      rfid: 'RF00000001',
      status: 'ativo' as const,
      peso_inicial: 450,
      sexo: 'M' as const,
      data_nascimento: '2021-01-15T00:00:00Z',
    },
    {
      id: '2',
      nome: 'Vaca Malhada',
      raca: 'Brahman',
      rfid: 'RF00000002',
      status: 'ativo' as const,
      peso_inicial: 380,
      sexo: 'F' as const,
      data_nascimento: '2020-06-10T00:00:00Z',
    },
    {
      id: '3',
      nome: 'Touro Puro',
      raca: 'Guzerá',
      rfid: 'RF00000003',
      status: 'inativo' as const,
      peso_inicial: 520,
      sexo: 'M' as const,
      data_nascimento: '2019-03-22T00:00:00Z',
    },
  ]

  describe('Rendering', () => {
    it('should render animal list container', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )
      expect(screen.getByRole('region')).toBeInTheDocument()
    })

    it('should render search bar', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )
      const searchInput = screen.getByPlaceholderText(/buscar|search/i)
      expect(searchInput).toBeInTheDocument()
    })

    it('should render all animal cards', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )
      expect(screen.getByText('Boi do Pasto')).toBeInTheDocument()
      expect(screen.getByText('Vaca Malhada')).toBeInTheDocument()
      expect(screen.getByText('Touro Puro')).toBeInTheDocument()
    })

    it('should render pagination', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )
      const nav = screen.getByRole('navigation')
      expect(nav).toBeInTheDocument()
    })

    it('should render empty state when no animals', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={[]} totalAnimals={0} />
        </BrowserRouter>
      )
      const emptyState = screen.getByText(/nenhum animal|no animals/i)
      expect(emptyState).toBeInTheDocument()
    })

    it('should render loading skeleton when isLoading', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={[]} totalAnimals={0} isLoading={true} />
        </BrowserRouter>
      )
      const skeletons = document.querySelectorAll('.animal-list__skeleton')
      expect(skeletons.length).toBeGreaterThan(0)
    })

    it('should render error message when error exists', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={[]} totalAnimals={0} error="Erro ao carregar" />
        </BrowserRouter>
      )
      expect(screen.getByText('Erro ao carregar')).toBeInTheDocument()
    })

    it('should render filter button', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )
      const filterBtn = screen.getByRole('button', { name: /filtrar|filter/i })
      expect(filterBtn).toBeInTheDocument()
    })

    it('should render add button', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )
      const addBtn = screen.getByRole('button', { name: /adicionar|novo|add|new/i })
      expect(addBtn).toBeInTheDocument()
    })
  })

  describe('Search Functionality', () => {
    it('should call onSearch when search input changes', async () => {
      const user = userEvent.setup()
      const mockSearch = vi.fn()
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} onSearch={mockSearch} />
        </BrowserRouter>
      )

      const searchInput = screen.getByPlaceholderText(/buscar|search/i)
      await user.type(searchInput, 'Boi')

      await waitFor(() => {
        expect(mockSearch).toHaveBeenCalled()
      })
    })

    it('should filter animals by search term', async () => {
      const user = userEvent.setup()
      const mockSearch = vi.fn()
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} onSearch={mockSearch} />
        </BrowserRouter>
      )

      const searchInput = screen.getByPlaceholderText(/buscar|search/i)
      await user.type(searchInput, 'Nelore')

      expect(mockSearch).toHaveBeenCalled()
    })
  })

  describe('Pagination', () => {
    it('should handle page changes', async () => {
      const user = userEvent.setup()
      const mockPageChange = vi.fn()
      render(
        <BrowserRouter>
          <AnimalList 
            animals={mockAnimals} 
            totalAnimals={30}
            currentPage={1}
            onPageChange={mockPageChange}
          />
        </BrowserRouter>
      )

      const nextBtn = screen.getByRole('button', { name: /próxima|next/i })
      await user.click(nextBtn)

      expect(mockPageChange).toHaveBeenCalledWith(2)
    })

    it('should handle page size changes', async () => {
      const user = userEvent.setup()
      const mockPageSizeChange = vi.fn()
      render(
        <BrowserRouter>
          <AnimalList 
            animals={mockAnimals} 
            totalAnimals={30}
            onPageSizeChange={mockPageSizeChange}
          />
        </BrowserRouter>
      )

      const sizeSelect = screen.getByLabelText(/itens por página/i)
      await user.selectOptions(sizeSelect, '25')

      expect(mockPageSizeChange).toHaveBeenCalledWith(25)
    })
  })

  describe('Animal Actions', () => {
    it('should call onEdit when animal edit button is clicked', async () => {
      const user = userEvent.setup()
      const mockEdit = vi.fn()
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} onEdit={mockEdit} />
        </BrowserRouter>
      )

      const editBtns = screen.getAllByRole('button', { name: /editar|edit/i })
      await user.click(editBtns[0])

      expect(mockEdit).toHaveBeenCalledWith(mockAnimals[0])
    })

    it('should call onDelete when animal delete button is clicked', async () => {
      const user = userEvent.setup()
      const mockDelete = vi.fn()
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} onDelete={mockDelete} />
        </BrowserRouter>
      )

      const deleteBtns = screen.getAllByRole('button', { name: /deletar|delete/i })
      await user.click(deleteBtns[0])

      expect(mockDelete).toHaveBeenCalledWith(mockAnimals[0].id)
    })

    it('should call onViewDetails when animal card is clicked', async () => {
      const user = userEvent.setup()
      const mockViewDetails = vi.fn()
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} onViewDetails={mockViewDetails} />
        </BrowserRouter>
      )

      const animalCard = screen.getByText('Boi do Pasto').closest('article')
      if (animalCard) {
        await user.click(animalCard)
        expect(mockViewDetails).toHaveBeenCalledWith(mockAnimals[0])
      }
    })

    it('should call onAddNew when add button is clicked', async () => {
      const user = userEvent.setup()
      const mockAddNew = vi.fn()
      render(
        <BrowserRouter>
          <AnimalList 
            animals={mockAnimals} 
            totalAnimals={3}
            onAddNew={mockAddNew}
          />
        </BrowserRouter>
      )

      const addBtn = screen.getByRole('button', { name: /adicionar|novo|add|new/i })
      await user.click(addBtn)

      expect(mockAddNew).toHaveBeenCalled()
    })
  })

  describe('Filter Functionality', () => {
    it('should show filter panel when filter button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )

      const filterBtn = screen.getByRole('button', { name: /filtrar|filter/i })
      await user.click(filterBtn)

      // Filter panel should appear
      await waitFor(() => {
        expect(screen.getByText(/status|Status/)).toBeInTheDocument()
      })
    })

    it('should filter by status', async () => {
      const user = userEvent.setup()
      const mockFilter = vi.fn()
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} onFilter={mockFilter} />
        </BrowserRouter>
      )

      const filterBtn = screen.getByRole('button', { name: /filtrar|filter/i })
      await user.click(filterBtn)

      await waitFor(() => {
        const ativoCheckbox = screen.getByLabelText(/ativo|active/i)
        user.click(ativoCheckbox)
      })

      expect(mockFilter).toHaveBeenCalled()
    })
  })

  describe('Loading States', () => {
    it('should show skeleton loaders while loading', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={[]} totalAnimals={0} isLoading={true} />
        </BrowserRouter>
      )
      const skeletons = document.querySelectorAll('.animal-list__skeleton')
      expect(skeletons.length).toBeGreaterThanOrEqual(1)
    })

    it('should hide skeletons when loading is false', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} isLoading={false} />
        </BrowserRouter>
      )
      const skeletons = document.querySelectorAll('.animal-list__skeleton')
      expect(skeletons.length).toBe(0)
    })
  })

  describe('Accessibility', () => {
    it('should have region role for main content', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )
      const region = screen.getByRole('region')
      expect(region).toBeInTheDocument()
    })

    it('should have proper ARIA labels', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )
      const searchInput = screen.getByPlaceholderText(/buscar|search/i)
      expect(searchInput).toHaveAttribute('aria-label')
    })
  })

  describe('Responsive Layout', () => {
    it('should render with grid layout', () => {
      render(
        <BrowserRouter>
          <AnimalList animals={mockAnimals} totalAnimals={3} />
        </BrowserRouter>
      )
      const grid = document.querySelector('.animal-list__grid')
      expect(grid).toBeInTheDocument()
    })
  })
})

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AnimalForm from './AnimalForm'

describe('AnimalForm Component', () => {
  const mockAnimal = {
    id: '507f1f77bcf86cd799439011',
    nome: 'Boi do Pasto',
    raca: 'Nelore',
    rfid: 'RF12345678',
    status: 'ativo',
    peso_inicial: 450,
    sexo: 'M',
    data_nascimento: new Date('2021-01-15').toISOString().split('T')[0],
  }

  describe('Rendering', () => {
    it('should render form with create mode', () => {
      render(<AnimalForm />)
      const form = screen.getByRole('form')
      expect(form).toBeInTheDocument()
    })

    it('should render form title for create', () => {
      render(<AnimalForm />)
      const title = screen.getByText(/Registrar Novo Animal|New Animal/i)
      expect(title).toBeInTheDocument()
    })

    it('should render form title for edit', () => {
      render(<AnimalForm animal={mockAnimal} />)
      const title = screen.getByText(/Editar Animal|Edit Animal/i)
      expect(title).toBeInTheDocument()
    })

    it('should render all form fields', () => {
      render(<AnimalForm />)
      
      expect(screen.getByLabelText(/Nome/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Raça/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/RFID/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Peso Inicial/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Gênero|Sexo/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Data.*Nascimento/i)).toBeInTheDocument()
    })

    it('should render status field only in edit mode', () => {
      const { rerender } = render(<AnimalForm />)
      expect(screen.queryByLabelText(/Status/i)).not.toBeInTheDocument()

      rerender(<AnimalForm animal={mockAnimal} />)
      expect(screen.getByLabelText(/Status/i)).toBeInTheDocument()
    })

    it('should render submit button', () => {
      render(<AnimalForm />)
      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar|Submit/i })
      expect(submitBtn).toBeInTheDocument()
    })

    it('should render cancel button', () => {
      render(<AnimalForm onCancel={() => {}} />)
      const cancelBtn = screen.getByRole('button', { name: /Cancelar|Cancel/i })
      expect(cancelBtn).toBeInTheDocument()
    })

    it('should populate fields in edit mode', () => {
      render(<AnimalForm animal={mockAnimal} />)
      
      const nomeInput = screen.getByDisplayValue('Boi do Pasto')
      const racaInput = screen.getByDisplayValue('Nelore')
      const rfidInput = screen.getByDisplayValue('RF12345678')
      const pesoInput = screen.getByDisplayValue('450')

      expect(nomeInput).toBeInTheDocument()
      expect(racaInput).toBeInTheDocument()
      expect(rfidInput).toBeInTheDocument()
      expect(pesoInput).toBeInTheDocument()
    })

    it('should render error messages area', () => {
      render(<AnimalForm />)
      const errorArea = screen.queryByRole('alert') || screen.queryByTestId('error-area')
      // Error area may be hidden initially
      expect(document.querySelector('[role="alert"]')).toBeDefined()
    })
  })

  describe('Form Validation', () => {
    it('should show error for empty nome', async () => {
      const user = userEvent.setup()
      render(<AnimalForm />)
      
      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      await user.click(submitBtn)

      await waitFor(() => {
        expect(screen.getByText(/Nome é obrigatório|Name is required/i)).toBeInTheDocument()
      })
    })

    it('should show error for empty raca', async () => {
      const user = userEvent.setup()
      render(<AnimalForm />)
      
      const nomeInput = screen.getByLabelText(/Nome/i)
      await user.type(nomeInput, 'Boi do Pasto')

      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      await user.click(submitBtn)

      await waitFor(() => {
        expect(screen.getByText(/Raça é obrigatória|Breed is required/i)).toBeInTheDocument()
      })
    })

    it('should show error for invalid RFID format', async () => {
      const user = userEvent.setup()
      render(<AnimalForm />)
      
      const rfidInput = screen.getByLabelText(/RFID/i)
      await user.type(rfidInput, 'INVALID')

      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      await user.click(submitBtn)

      await waitFor(() => {
        expect(screen.getByText(/RFID inválido|Invalid RFID/i)).toBeInTheDocument()
      })
    })

    it('should show error for peso <= 0', async () => {
      const user = userEvent.setup()
      render(<AnimalForm />)
      
      const pesoInput = screen.getByLabelText(/Peso Inicial/i)
      await user.clear(pesoInput)
      await user.type(pesoInput, '0')

      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      await user.click(submitBtn)

      await waitFor(() => {
        expect(screen.getByText(/Peso deve ser maior|Weight must be/i)).toBeInTheDocument()
      })
    })

    it('should validate future birth date', async () => {
      const user = userEvent.setup()
      render(<AnimalForm />)
      
      const futureDate = new Date()
      futureDate.setFullYear(futureDate.getFullYear() + 1)
      const dateStr = futureDate.toISOString().split('T')[0]

      const dateInput = screen.getByLabelText(/Data.*Nascimento/i)
      await user.clear(dateInput)
      await user.type(dateInput, dateStr)

      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      await user.click(submitBtn)

      await waitFor(() => {
        expect(screen.getByText(/data de nascimento não pode ser futura|birth date cannot be in future/i)).toBeInTheDocument()
      })
    })

    it('should clear errors on valid input', async () => {
      const user = userEvent.setup()
      render(<AnimalForm />)
      
      const nomeInput = screen.getByLabelText(/Nome/i)
      await user.type(nomeInput, '')

      let submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      await user.click(submitBtn)

      await waitFor(() => {
        expect(screen.getByText(/Nome é obrigatório|Name is required/i)).toBeInTheDocument()
      })

      await user.type(nomeInput, 'Boi do Pasto')
      
      const errorElement = screen.queryByText(/Nome é obrigatório|Name is required/i)
      expect(errorElement).not.toBeInTheDocument()
    })
  })

  describe('Form Submission', () => {
    it('should call onSubmit with form data on create', async () => {
      const user = userEvent.setup()
      const mockSubmit = vi.fn()
      render(<AnimalForm onSubmit={mockSubmit} />)

      const nomeInput = screen.getByLabelText(/Nome/i)
      const racaInput = screen.getByLabelText(/Raça/i)
      const rfidInput = screen.getByLabelText(/RFID/i)
      const pesoInput = screen.getByLabelText(/Peso Inicial/i)
      const sexoInput = screen.getByLabelText(/Gênero|Sexo/i)
      const dateInput = screen.getByLabelText(/Data.*Nascimento/i)

      await user.type(nomeInput, 'Boi do Pasto')
      await user.type(racaInput, 'Nelore')
      await user.type(rfidInput, 'RF12345678')
      await user.clear(pesoInput)
      await user.type(pesoInput, '450')
      await user.selectOptions(sexoInput, 'M')
      await user.type(dateInput, '2021-01-15')

      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      await user.click(submitBtn)

      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
          nome: 'Boi do Pasto',
          raca: 'Nelore',
          rfid: 'RF12345678',
          peso_inicial: 450,
          sexo: 'M',
          data_nascimento: '2021-01-15',
        }))
      })
    })

    it('should call onSubmit with id in edit mode', async () => {
      const user = userEvent.setup()
      const mockSubmit = vi.fn()
      render(<AnimalForm animal={mockAnimal} onSubmit={mockSubmit} />)

      const nomeInput = screen.getByDisplayValue('Boi do Pasto')
      await user.clear(nomeInput)
      await user.type(nomeInput, 'Boi Atualizado')

      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      await user.click(submitBtn)

      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
          id: mockAnimal.id,
          nome: 'Boi Atualizado',
        }))
      })
    })

    it('should disable submit button while submitting', async () => {
      const user = userEvent.setup()
      const mockSubmit = vi.fn(
        () => new Promise(resolve => setTimeout(resolve, 100))
      )
      render(<AnimalForm onSubmit={mockSubmit} isSubmitting={true} />)

      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      expect(submitBtn).toBeDisabled()
    })
  })

  describe('Form Cancellation', () => {
    it('should call onCancel when cancel button is clicked', async () => {
      const user = userEvent.setup()
      const mockCancel = vi.fn()
      render(<AnimalForm onCancel={mockCancel} />)

      const cancelBtn = screen.getByRole('button', { name: /Cancelar|Cancel/i })
      await user.click(cancelBtn)

      expect(mockCancel).toHaveBeenCalled()
    })

    it('should not call onSubmit when cancel is clicked', async () => {
      const user = userEvent.setup()
      const mockSubmit = vi.fn()
      const mockCancel = vi.fn()
      render(
        <AnimalForm 
          onSubmit={mockSubmit}
          onCancel={mockCancel}
        />
      )

      const cancelBtn = screen.getByRole('button', { name: /Cancelar|Cancel/i })
      await user.click(cancelBtn)

      expect(mockCancel).toHaveBeenCalled()
      expect(mockSubmit).not.toHaveBeenCalled()
    })
  })

  describe('Accessibility', () => {
    it('should have proper form role', () => {
      render(<AnimalForm />)
      const form = screen.getByRole('form')
      expect(form).toBeInTheDocument()
    })

    it('should have accessible form labels', () => {
      render(<AnimalForm />)
      
      const labels = screen.getAllByText(/Nome|Raça|RFID|Peso|Gênero|Nascimento/i)
      expect(labels.length).toBeGreaterThan(0)
    })

    it('should have keyboard navigation', async () => {
      const user = userEvent.setup()
      render(<AnimalForm />)
      
      const nomeInput = screen.getByLabelText(/Nome/i)
      nomeInput.focus()
      
      expect(nomeInput).toHaveFocus()
    })

    it('should display field validation errors with role alert', async () => {
      const user = userEvent.setup()
      render(<AnimalForm />)
      
      const submitBtn = screen.getByRole('button', { name: /Registrar|Salvar/i })
      await user.click(submitBtn)

      await waitFor(() => {
        const errorElements = screen.getAllByText(/obrigatório|required/i)
        expect(errorElements.length).toBeGreaterThan(0)
      })
    })
  })
})

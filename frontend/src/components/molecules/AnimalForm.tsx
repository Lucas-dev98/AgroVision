import React, { useState, useEffect } from 'react'
import './AnimalForm.css'

interface Animal {
  id?: string
  nome: string
  raca: string
  rfid: string
  status?: 'ativo' | 'inativo' | 'vendido'
  peso_inicial: number
  sexo: 'M' | 'F'
  data_nascimento: string
}

interface AnimalFormProps {
  animal?: Animal
  onSubmit?: (data: Animal) => Promise<void> | void
  onCancel?: () => void
  isSubmitting?: boolean
}

interface FormErrors {
  nome?: string
  raca?: string
  rfid?: string
  peso_inicial?: string
  sexo?: string
  data_nascimento?: string
}

const AnimalForm: React.FC<AnimalFormProps> = ({
  animal,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const [formData, setFormData] = useState<Animal>({
    nome: animal?.nome || '',
    raca: animal?.raca || '',
    rfid: animal?.rfid || '',
    status: animal?.status || 'ativo',
    peso_inicial: animal?.peso_inicial || 0,
    sexo: animal?.sexo || 'M',
    data_nascimento: animal?.data_nascimento || '',
  })

  const [errors, setErrors] = useState<FormErrors>({})
  const isEditMode = !!animal?.id

  useEffect(() => {
    if (animal) {
      setFormData({
        id: animal.id,
        nome: animal.nome,
        raca: animal.raca,
        rfid: animal.rfid,
        status: animal.status || 'ativo',
        peso_inicial: animal.peso_inicial,
        sexo: animal.sexo,
        data_nascimento: animal.data_nascimento,
      })
    }
  }, [animal])

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório'
    }

    if (!formData.raca.trim()) {
      newErrors.raca = 'Raça é obrigatória'
    }

    if (!formData.rfid.trim()) {
      newErrors.rfid = 'RFID é obrigatório'
    } else if (!/^[A-Z]{2}\d{8}$/.test(formData.rfid)) {
      newErrors.rfid = 'RFID inválido. Formato: 2 letras + 8 números (ex: RF12345678)'
    }

    if (formData.peso_inicial <= 0) {
      newErrors.peso_inicial = 'Peso deve ser maior que zero'
    }

    if (!formData.data_nascimento) {
      newErrors.data_nascimento = 'Data de nascimento é obrigatória'
    } else {
      const birthDate = new Date(formData.data_nascimento)
      const today = new Date()
      if (birthDate > today) {
        newErrors.data_nascimento = 'Data de nascimento não pode ser futura'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target

    if (name === 'peso_inicial') {
      setFormData({
        ...formData,
        [name]: parseFloat(value) || 0,
      })
    } else {
      setFormData({
        ...formData,
        [name]: value,
      })
    }

    // Clear error for this field
    if (errors[name as keyof FormErrors]) {
      setErrors({
        ...errors,
        [name]: undefined,
      })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    const dataToSubmit = isEditMode
      ? { id: animal!.id, ...formData }
      : formData

    try {
      await onSubmit?.(dataToSubmit)
    } catch (error) {
      console.error('Erro ao submeter formulário:', error)
    }
  }

  const handleCancel = () => {
    onCancel?.()
  }

  return (
    <form className="animal-form" onSubmit={handleSubmit} role="form">
      <div className="animal-form__container">
        <div className="animal-form__header">
          <h2 className="animal-form__title">
            {isEditMode ? 'Editar Animal' : 'Registrar Novo Animal'}
          </h2>
        </div>

        <div className="animal-form__body">
          {/* Nome */}
          <div className="animal-form__group">
            <label htmlFor="nome" className="animal-form__label">
              Nome <span className="animal-form__required">*</span>
            </label>
            <input
              type="text"
              id="nome"
              name="nome"
              value={formData.nome}
              onChange={handleInputChange}
              placeholder="Ex: Boi do Pasto"
              className={`animal-form__input ${errors.nome ? 'animal-form__input--error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.nome && (
              <span className="animal-form__error">{errors.nome}</span>
            )}
          </div>

          {/* Raça */}
          <div className="animal-form__group">
            <label htmlFor="raca" className="animal-form__label">
              Raça <span className="animal-form__required">*</span>
            </label>
            <input
              type="text"
              id="raca"
              name="raca"
              value={formData.raca}
              onChange={handleInputChange}
              placeholder="Ex: Nelore"
              className={`animal-form__input ${errors.raca ? 'animal-form__input--error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.raca && (
              <span className="animal-form__error">{errors.raca}</span>
            )}
          </div>

          {/* RFID */}
          <div className="animal-form__group">
            <label htmlFor="rfid" className="animal-form__label">
              RFID <span className="animal-form__required">*</span>
            </label>
            <input
              type="text"
              id="rfid"
              name="rfid"
              value={formData.rfid}
              onChange={handleInputChange}
              placeholder="Ex: RF12345678"
              className={`animal-form__input ${errors.rfid ? 'animal-form__input--error' : ''}`}
              disabled={isSubmitting}
              maxLength={10}
            />
            {errors.rfid && (
              <span className="animal-form__error">{errors.rfid}</span>
            )}
          </div>

          {/* Peso Inicial */}
          <div className="animal-form__group">
            <label htmlFor="peso_inicial" className="animal-form__label">
              Peso Inicial (kg) <span className="animal-form__required">*</span>
            </label>
            <input
              type="number"
              id="peso_inicial"
              name="peso_inicial"
              value={formData.peso_inicial || ''}
              onChange={handleInputChange}
              placeholder="Ex: 450"
              className={`animal-form__input ${errors.peso_inicial ? 'animal-form__input--error' : ''}`}
              disabled={isSubmitting}
              min="0"
              step="0.1"
            />
            {errors.peso_inicial && (
              <span className="animal-form__error">{errors.peso_inicial}</span>
            )}
          </div>

          {/* Gênero */}
          <div className="animal-form__group">
            <label htmlFor="sexo" className="animal-form__label">
              Gênero <span className="animal-form__required">*</span>
            </label>
            <select
              id="sexo"
              name="sexo"
              value={formData.sexo}
              onChange={handleInputChange}
              className={`animal-form__select ${errors.sexo ? 'animal-form__input--error' : ''}`}
              disabled={isSubmitting}
            >
              <option value="M">Macho</option>
              <option value="F">Fêmea</option>
            </select>
            {errors.sexo && (
              <span className="animal-form__error">{errors.sexo}</span>
            )}
          </div>

          {/* Data Nascimento */}
          <div className="animal-form__group">
            <label htmlFor="data_nascimento" className="animal-form__label">
              Data de Nascimento <span className="animal-form__required">*</span>
            </label>
            <input
              type="date"
              id="data_nascimento"
              name="data_nascimento"
              value={formData.data_nascimento}
              onChange={handleInputChange}
              className={`animal-form__input ${errors.data_nascimento ? 'animal-form__input--error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.data_nascimento && (
              <span className="animal-form__error">{errors.data_nascimento}</span>
            )}
          </div>

          {/* Status (apenas no modo edição) */}
          {isEditMode && (
            <div className="animal-form__group">
              <label htmlFor="status" className="animal-form__label">
                Status
              </label>
              <select
                id="status"
                name="status"
                value={formData.status || 'ativo'}
                onChange={handleInputChange}
                className="animal-form__select"
                disabled={isSubmitting}
              >
                <option value="ativo">Ativo</option>
                <option value="inativo">Inativo</option>
                <option value="vendido">Vendido</option>
              </select>
            </div>
          )}
        </div>

        {/* Footer com ações */}
        <div className="animal-form__footer">
          <button
            type="button"
            className="animal-form__button animal-form__button--cancel"
            onClick={handleCancel}
            disabled={isSubmitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="animal-form__button animal-form__button--submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Salvando...' : isEditMode ? 'Atualizar' : 'Registrar'}
          </button>
        </div>
      </div>
    </form>
  )
}

export default AnimalForm

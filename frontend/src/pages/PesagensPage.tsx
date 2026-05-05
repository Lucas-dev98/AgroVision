import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Pesagem } from '@types/index'
import apiService from '@services/api'
import Button from '@components/atoms/Button'
import Modal from '@components/molecules/Modal'
import '../styles/global.css'
import '../styles/PesagensPage.css'

interface PesagemFormData {
  animal_id: number
  peso_kg: number
  peso_arroba: number
  data: string
  hora?: string
  observacoes?: string
}

const PesagensPage: React.FC = () => {
  const navigate = useNavigate()
  
  const [pesagens, setPesagens] = useState<Pesagem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState<PesagemFormData>({
    animal_id: 0,
    peso_kg: 0,
    peso_arroba: 0,
    data: new Date().toISOString().split('T')[0],
    hora: new Date().toTimeString().slice(0, 5),
    observacoes: '',
  })
  const [animals, setAnimals] = useState<any[]>([])

  useEffect(() => {
    loadPesagens()
    loadAnimals()
  }, [])

  const loadPesagens = async () => {
    try {
      setLoading(true)
      const data = await apiService.getPesagens()
      setPesagens(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar pesagens')
      console.error('Erro ao carregar pesagens:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadAnimals = async () => {
    try {
      const data = await apiService.getAnimals()
      setAnimals(data.items)
    } catch (err) {
      console.error('Erro ao carregar animais:', err)
    }
  }

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target

    if (name === 'peso_kg' || name === 'peso_arroba' || name === 'animal_id') {
      setFormData({
        ...formData,
        [name]: name === 'animal_id' ? parseInt(value) : parseFloat(value) || 0,
      })
    } else {
      setFormData({
        ...formData,
        [name]: value,
      })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.animal_id || formData.peso_kg <= 0) {
      alert('Preencha todos os campos obrigatórios corretamente')
      return
    }

    setIsSubmitting(true)
    try {
      await apiService.createPesagem({
        animal_id: formData.animal_id,
        peso_kg: formData.peso_kg,
        peso_arroba: formData.peso_arroba,
        data: formData.data,
        hora: formData.hora,
        observacoes: formData.observacoes,
      })

      setFormData({
        animal_id: 0,
        peso_kg: 0,
        peso_arroba: 0,
        data: new Date().toISOString().split('T')[0],
        hora: new Date().toTimeString().slice(0, 5),
        observacoes: '',
      })

      setIsModalOpen(false)
      loadPesagens()
    } catch (err: any) {
      alert('Erro ao criar pesagem: ' + (err.message || 'Tente novamente'))
      console.error('Erro ao criar pesagem:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleBack = () => {
    navigate('/dashboard')
  }

  const getAnimalName = (animalId: number) => {
    const animal = animals.find(a => a.id === animalId)
    return animal ? animal.nome : `Animal #${animalId}`
  }

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('pt-BR')
    } catch {
      return dateStr
    }
  }

  return (
    <div className="pesagens-page">
      <div className="pesagens-page__header">
        <Button 
          onClick={handleBack} 
          variant="secondary"
          className="pesagens-page__back-btn"
        >
          ← Voltar
        </Button>
        <h1>Pesagens</h1>
      </div>

      <div className="pesagens-page__actions">
        <Button 
          onClick={() => setIsModalOpen(true)}
          variant="primary"
        >
          Adicionar Pesagem
        </Button>
      </div>

      {loading && (
        <div className="pesagens-page__loading">
          <div className="spinner"></div>
          <p>Carregando pesagens...</p>
        </div>
      )}

      {error && (
        <div className="pesagens-page__error">
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && pesagens.length === 0 && (
        <div className="pesagens-page__empty">
          <p>Nenhuma pesagem registrada</p>
        </div>
      )}

      {!loading && pesagens.length > 0 && (
        <div className="pesagens-page__table">
          <table>
            <thead>
              <tr>
                <th>Animal</th>
                <th>Data</th>
                <th>Peso (kg)</th>
                <th>Peso (arroba)</th>
                <th>Observações</th>
              </tr>
            </thead>
            <tbody>
              {pesagens.map((pesagem) => (
                <tr key={pesagem.id}>
                  <td>{getAnimalName(pesagem.animal_id)}</td>
                  <td>{formatDate(pesagem.data)}</td>
                  <td>{pesagem.peso_kg.toFixed(2)}</td>
                  <td>{pesagem.peso_arroba.toFixed(2)}</td>
                  <td>{pesagem.observacoes || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal para criar pesagem */}
      <Modal
        isOpen={isModalOpen}
        title="Adicionar Pesagem"
        onClose={() => setIsModalOpen(false)}
        size="large"
      >
        <form className="pesagem-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="animal_id">Animal *</label>
            <select
              id="animal_id"
              name="animal_id"
              value={formData.animal_id}
              onChange={handleInputChange}
              required
            >
              <option value="">Selecione um animal</option>
              {animals.map((animal) => (
                <option key={animal.id} value={animal.id}>
                  {animal.nome} ({animal.rfid})
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="data">Data *</label>
              <input
                id="data"
                type="date"
                name="data"
                value={formData.data}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="hora">Hora</label>
              <input
                id="hora"
                type="time"
                name="hora"
                value={formData.hora}
                onChange={handleInputChange}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="peso_kg">Peso (kg) *</label>
              <input
                id="peso_kg"
                type="number"
                name="peso_kg"
                value={formData.peso_kg}
                onChange={handleInputChange}
                step="0.01"
                min="0"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="peso_arroba">Peso (arroba) *</label>
              <input
                id="peso_arroba"
                type="number"
                name="peso_arroba"
                value={formData.peso_arroba}
                onChange={handleInputChange}
                step="0.01"
                min="0"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="observacoes">Observações</label>
            <textarea
              id="observacoes"
              name="observacoes"
              value={formData.observacoes}
              onChange={handleInputChange}
              placeholder="Adicione observações sobre esta pesagem"
              rows={4}
            />
          </div>

          <div className="form-actions">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsModalOpen(false)}
              disabled={isSubmitting}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Salvando...' : 'Salvar Pesagem'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default PesagensPage

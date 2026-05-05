import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Animal } from '@types/index'
import apiService from '@services/api'
import Modal from '@components/molecules/Modal'
import AnimalForm from '@components/molecules/AnimalForm'
import Button from '@components/atoms/Button'
import '../styles/global.css'
import '../styles/AnimalDetailPage.css'

const AnimalDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  
  const [animal, setAnimal] = useState<Animal | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditMode, setIsEditMode] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleteConfirming, setDeleteConfirming] = useState(false)

  useEffect(() => {
    const loadAnimal = async () => {
      if (!id) return

      try {
        setLoading(true)
        const data = await apiService.getAnimal(parseInt(id))
        setAnimal(data)
        setError(null)
      } catch (err: any) {
        setError(err.message || 'Erro ao carregar animal')
        console.error('Erro ao carregar animal:', err)
      } finally {
        setLoading(false)
      }
    }

    loadAnimal()
  }, [id])

  const handleEdit = () => {
    setIsEditMode(true)
  }

  const handleCancel = () => {
    setIsEditMode(false)
  }

  const handleSave = async (formData: any) => {
    if (!animal) return

    setIsSubmitting(true)
    try {
      const updatedAnimal = await apiService.updateAnimal(animal.id, {
        nome: formData.nome,
        raca: formData.raca,
        rfid: formData.rfid,
        status: formData.status,
        peso_inicial: formData.peso_inicial,
        data_nascimento: formData.data_nascimento,
      })
      setAnimal(updatedAnimal)
      setIsEditMode(false)
    } catch (err: any) {
      alert('Erro ao atualizar animal: ' + (err.message || 'Tente novamente'))
      console.error('Erro ao atualizar animal:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteConfirm = async () => {
    if (!animal) return

    setDeleteConfirming(true)
    try {
      await apiService.deleteAnimal(animal.id)
      navigate('/dashboard')
    } catch (err: any) {
      alert('Erro ao deletar animal: ' + (err.message || 'Tente novamente'))
      console.error('Erro ao deletar animal:', err)
      setShowDeleteConfirm(false)
    } finally {
      setDeleteConfirming(false)
    }
  }

  const handleBack = () => {
    navigate('/dashboard')
  }

  if (loading) {
    return (
      <div className="animal-detail-page">
        <div className="animal-detail-page__loading">
          <div className="spinner"></div>
          <p>Carregando detalhes do animal...</p>
        </div>
      </div>
    )
  }

  if (error || !animal) {
    return (
      <div className="animal-detail-page">
        <div className="animal-detail-page__error">
          <h2>Erro ao carregar animal</h2>
          <p>{error || 'Animal não encontrado'}</p>
          <Button onClick={handleBack}>Voltar ao Dashboard</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="animal-detail-page">
      <div className="animal-detail-page__header">
        <Button 
          onClick={handleBack} 
          variant="secondary"
          className="animal-detail-page__back-btn"
        >
          ← Voltar
        </Button>
        <h1>{animal.nome}</h1>
      </div>

      {!isEditMode ? (
        <div className="animal-detail-page__content">
          <div className="animal-detail-page__info-grid">
            <div className="animal-detail-page__info-item">
              <label>Nome</label>
              <p>{animal.nome}</p>
            </div>
            <div className="animal-detail-page__info-item">
              <label>Raça</label>
              <p>{animal.raca}</p>
            </div>
            <div className="animal-detail-page__info-item">
              <label>RFID</label>
              <p>{animal.rfid}</p>
            </div>
            <div className="animal-detail-page__info-item">
              <label>Status</label>
              <p className={`status status--${animal.status.toLowerCase()}`}>
                {animal.status}
              </p>
            </div>
            <div className="animal-detail-page__info-item">
              <label>Peso Inicial (kg)</label>
              <p>{animal.peso_inicial}</p>
            </div>
            <div className="animal-detail-page__info-item">
              <label>Data de Nascimento</label>
              <p>{new Date(animal.data_nascimento).toLocaleDateString('pt-BR')}</p>
            </div>
            <div className="animal-detail-page__info-item">
              <label>Data de Entrada</label>
              <p>{new Date(animal.data_entrada).toLocaleDateString('pt-BR')}</p>
            </div>
            <div className="animal-detail-page__info-item">
              <label>Última Atualização</label>
              <p>{new Date(animal.updated_at).toLocaleDateString('pt-BR')}</p>
            </div>
          </div>

          <div className="animal-detail-page__actions">
            <Button 
              onClick={handleEdit}
              variant="primary"
            >
              Editar
            </Button>
            <Button 
              onClick={() => setShowDeleteConfirm(true)}
              variant="danger"
            >
              Deletar
            </Button>
          </div>
        </div>
      ) : (
        <div className="animal-detail-page__edit-form">
          <AnimalForm
            animal={{
              id: animal.id.toString(),
              nome: animal.nome,
              raca: animal.raca,
              rfid: animal.rfid,
              status: (animal.status.toLowerCase() as any),
              peso_inicial: animal.peso_inicial,
              sexo: 'M',
              data_nascimento: animal.data_nascimento,
            }}
            onSubmit={handleSave}
            onCancel={handleCancel}
            isSubmitting={isSubmitting}
          />
        </div>
      )}

      {/* Modal de confirmação de deleção */}
      <Modal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        title="Confirmar Exclusão"
      >
        <div className="delete-confirm-modal">
          <p>Tem certeza que deseja deletar este animal?</p>
          <p className="delete-confirm-modal__warning">
            Esta ação não pode ser desfeita.
          </p>
          <div className="delete-confirm-modal__actions">
            <Button
              onClick={() => setShowDeleteConfirm(false)}
              variant="secondary"
            >
              Cancelar
            </Button>
            <Button
              onClick={handleDeleteConfirm}
              variant="danger"
              disabled={deleteConfirming}
            >
              {deleteConfirming ? 'Deletando...' : 'Confirmar Exclusão'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default AnimalDetailPage

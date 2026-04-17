import React, { useState, useCallback } from 'react'
import { Breadcrumb, AnimalCard, AnimalForm, Modal, Alert } from '../molecules'
import './AnimalDetail.css'

interface Animal {
  id: string
  nome: string
  raca: string
  rfid: string
  status: 'ativo' | 'inativo' | 'vendido'
  peso_inicial: number
  sexo: 'M' | 'F'
  data_nascimento: string
}

interface BreadcrumbItem {
  label: string
  path?: string
}

interface AnimalDetailProps {
  animal: Animal
  breadcrumbs: BreadcrumbItem[]
  isLoading?: boolean
  error?: string
  onSave?: (animal: Animal) => void
  onDelete?: (id: string) => void
  onCancel?: () => void
}

const AnimalDetail: React.FC<AnimalDetailProps> = ({
  animal,
  breadcrumbs,
  isLoading = false,
  error,
  onSave,
  onDelete,
  onCancel,
}) => {
  const [isEditMode, setIsEditMode] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showAlert, setShowAlert] = useState(false)
  const [alertMessage, setAlertMessage] = useState('')
  const [alertType, setAlertType] = useState<'success' | 'error' | 'warning' | 'info'>('info')
  const [isSaving, setIsSaving] = useState(false)

  const handleEdit = () => {
    setIsEditMode(true)
  }

  const handleCancel = () => {
    setIsEditMode(false)
    onCancel?.()
  }

  const handleSave = useCallback(
    async (updatedAnimal: Animal) => {
      setIsSaving(true)
      try {
        onSave?.(updatedAnimal)
        setAlertMessage('Animal atualizado com sucesso!')
        setAlertType('success')
        setShowAlert(true)
        setIsEditMode(false)
      } catch (err) {
        setAlertMessage('Erro ao atualizar animal!')
        setAlertType('error')
        setShowAlert(true)
      } finally {
        setIsSaving(false)
      }
    },
    [onSave]
  )

  const handleDeleteClick = () => {
    setShowDeleteModal(true)
  }

  const handleConfirmDelete = () => {
    try {
      onDelete?.(animal.id)
      setShowDeleteModal(false)
      setAlertMessage('Animal deletado com sucesso!')
      setAlertType('success')
      setShowAlert(true)
    } catch (err) {
      setAlertMessage('Erro ao deletar animal!')
      setAlertType('error')
      setShowAlert(true)
      setShowDeleteModal(false)
    }
  }

  if (isLoading) {
    return (
      <section className="animal-detail" role="region" aria-label="Detalhes do animal">
        <div className="animal-detail__loading">
          <div className="animal-detail__spinner" />
          <p>Carregando detalhes do animal...</p>
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="animal-detail" role="region" aria-label="Detalhes do animal">
        <div className="animal-detail__error">
          <h2>Erro ao carregar</h2>
          <p>{error}</p>
        </div>
      </section>
    )
  }

  return (
    <section className="animal-detail" role="region" aria-label="Detalhes do animal">
      {/* Breadcrumb */}
      <nav className="animal-detail__breadcrumb">
        <Breadcrumb items={breadcrumbs} />
      </nav>

      {/* Header with Actions */}
      <div className="animal-detail__header">
        <h1 className="animal-detail__title">{animal.nome}</h1>
        <div className="animal-detail__actions">
          {!isEditMode ? (
            <>
              <button
                className="animal-detail__button animal-detail__button--edit"
                onClick={handleEdit}
                aria-label="Editar animal"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
                Editar
              </button>
              <button
                className="animal-detail__button animal-detail__button--delete"
                onClick={handleDeleteClick}
                aria-label="Deletar animal"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  <line x1="10" y1="11" x2="10" y2="17" />
                  <line x1="14" y1="11" x2="14" y2="17" />
                </svg>
                Deletar
              </button>
            </>
          ) : (
            <>
              <button
                className="animal-detail__button animal-detail__button--save"
                disabled={isSaving}
                aria-label="Salvar alterações"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                  <polyline points="17 21 17 13 7 13 7 21" />
                  <polyline points="7 3 7 8 15 8" />
                </svg>
                {isSaving ? 'Salvando...' : 'Salvar'}
              </button>
              <button
                className="animal-detail__button animal-detail__button--cancel"
                onClick={handleCancel}
                aria-label="Cancelar edição"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
                Cancelar
              </button>
            </>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="animal-detail__content">
        {/* Info Card */}
        {!isEditMode && (
          <div className="animal-detail__card">
            <AnimalCard animal={animal} />
          </div>
        )}

        {/* Edit Form */}
        {isEditMode && (
          <div className="animal-detail__form">
            <AnimalForm animal={animal} onSubmit={handleSave} isEditMode={true} />
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        title="Confirmar Exclusão"
        variant="confirmation"
        isDanger
        onConfirm={handleConfirmDelete}
        onCancel={() => setShowDeleteModal(false)}
        confirmText="Deletar"
        cancelText="Cancelar"
      >
        <p>
          Tem certeza que deseja deletar <strong>{animal.nome}</strong>? Esta ação não pode ser
          desfeita.
        </p>
      </Modal>

      {/* Alert */}
      <Alert
        isOpen={showAlert}
        message={alertMessage}
        type={alertType}
        autoDismissMs={3000}
        onClose={() => setShowAlert(false)}
      />
    </section>
  )
}

export default AnimalDetail

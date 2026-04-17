import React, { useState, useCallback } from 'react'
import { SearchBar, Pagination, AnimalCard, Modal, Alert } from '../molecules'
import './AnimalList.css'

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

interface AnimalListProps {
  animals: Animal[]
  totalAnimals: number
  currentPage?: number
  pageSize?: number
  isLoading?: boolean
  error?: string
  onSearch?: (query: string) => void
  onPageChange?: (page: number) => void
  onPageSizeChange?: (size: number) => void
  onEdit?: (animal: Animal) => void
  onDelete?: (id: string) => void
  onViewDetails?: (animal: Animal) => void
  onAddNew?: () => void
  onFilter?: (filters: any) => void
}

const AnimalList: React.FC<AnimalListProps> = ({
  animals,
  totalAnimals,
  currentPage = 1,
  pageSize = 10,
  isLoading = false,
  error,
  onSearch,
  onPageChange,
  onPageSizeChange,
  onEdit,
  onDelete,
  onViewDetails,
  onAddNew,
  onFilter,
}) => {
  const [showFilter, setShowFilter] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedAnimalId, setSelectedAnimalId] = useState<string | null>(null)
  const [showAlert, setShowAlert] = useState(false)
  const [alertMessage, setAlertMessage] = useState('')
  const [alertType, setAlertType] = useState<'success' | 'error' | 'warning' | 'info'>('info')

  const totalPages = Math.ceil(totalAnimals / pageSize)

  const handleDeleteClick = (id: string) => {
    setSelectedAnimalId(id)
    setShowDeleteModal(true)
  }

  const handleConfirmDelete = () => {
    if (selectedAnimalId) {
      onDelete?.(selectedAnimalId)
      setShowDeleteModal(false)
      setSelectedAnimalId(null)
      setAlertMessage('Animal deletado com sucesso!')
      setAlertType('success')
      setShowAlert(true)
    }
  }

  const handleSearch = useCallback(
    (query: string) => {
      onSearch?.(query)
    },
    [onSearch]
  )

  const renderSkeletons = () => {
    return Array.from({ length: 3 }).map((_, index) => (
      <div key={`skeleton-${index}`} className="animal-list__skeleton">
        <div className="animal-list__skeleton-header" />
        <div className="animal-list__skeleton-content" />
        <div className="animal-list__skeleton-footer" />
      </div>
    ))
  }

  return (
    <section className="animal-list" role="region" aria-label="Lista de animais">
      {/* Header com Ações */}
      <div className="animal-list__header">
        <div className="animal-list__title-group">
          <h1 className="animal-list__title">Rebanho</h1>
          <span className="animal-list__count">{totalAnimals} animal(is)</span>
        </div>

        <div className="animal-list__actions">
          <button
            className="animal-list__button animal-list__button--filter"
            onClick={() => setShowFilter(!showFilter)}
            aria-label="Abrir filtros"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
            </svg>
            Filtrar
          </button>

          <button
            className="animal-list__button animal-list__button--add"
            onClick={onAddNew}
            aria-label="Adicionar novo animal"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Novo Animal
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="animal-list__search">
        <SearchBar
          onSearch={handleSearch}
          placeholder="Buscar por nome, raça ou RFID..."
          minLength={2}
          debounceMs={300}
        />
      </div>

      {/* Filter Panel */}
      {showFilter && (
        <div className="animal-list__filter">
          <div className="animal-list__filter-group">
            <label className="animal-list__filter-label">Status</label>
            <div className="animal-list__filter-options">
              <label className="animal-list__filter-checkbox">
                <input type="checkbox" value="ativo" />
                <span>Ativo</span>
              </label>
              <label className="animal-list__filter-checkbox">
                <input type="checkbox" value="inativo" />
                <span>Inativo</span>
              </label>
              <label className="animal-list__filter-checkbox">
                <input type="checkbox" value="vendido" />
                <span>Vendido</span>
              </label>
            </div>
          </div>

          <div className="animal-list__filter-actions">
            <button
              className="animal-list__filter-button animal-list__filter-button--reset"
              onClick={() => {
                onFilter?.({})
                setShowFilter(false)
              }}
            >
              Limpar Filtros
            </button>
            <button
              className="animal-list__filter-button animal-list__filter-button--apply"
              onClick={() => setShowFilter(false)}
            >
              Aplicar
            </button>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="animal-list__error">
          <p>{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && animals.length === 0 && !error && (
        <div className="animal-list__empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
          </svg>
          <h2>Nenhum animal encontrado</h2>
          <p>Comece adicionando animais ao seu rebanho.</p>
          <button
            className="animal-list__empty-button"
            onClick={onAddNew}
          >
            + Adicionar Primeiro Animal
          </button>
        </div>
      )}

      {/* Loading Skeletons */}
      {isLoading && (
        <div className="animal-list__grid">
          {renderSkeletons()}
        </div>
      )}

      {/* Animals Grid */}
      {!isLoading && animals.length > 0 && (
        <div className="animal-list__grid">
          {animals.map((animal) => (
            <AnimalCard
              key={animal.id}
              animal={animal}
              onEdit={onEdit}
              onDelete={() => handleDeleteClick(animal.id)}
              onClick={onViewDetails}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {!isLoading && animals.length > 0 && totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalAnimals}
          itemsPerPage={pageSize}
          onPageChange={onPageChange}
          onPageSizeChange={onPageSizeChange}
        />
      )}

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
        <p>Tem certeza que deseja deletar este animal? Esta ação não pode ser desfeita.</p>
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

export default AnimalList

import React, { useState } from 'react'
import './AnimalCard.css'

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

interface AnimalCardProps {
  animal: Animal
  onEdit?: (animal: Animal) => void
  onDelete?: (id: string) => void
  onClick?: (animal: Animal) => void
}

const AnimalCard: React.FC<AnimalCardProps> = ({
  animal,
  onEdit,
  onDelete,
  onClick,
}) => {
  const [isHovered, setIsHovered] = useState(false)

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation()
    onEdit?.(animal)
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete?.(animal.id)
  }

  const handleCardClick = () => {
    onClick?.(animal)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ativo':
        return 'active'
      case 'inativo':
        return 'inactive'
      case 'vendido':
        return 'sold'
      default:
        return 'active'
    }
  }

  const getGenderLabel = (sexo: string) => {
    return sexo === 'M' ? 'Macho' : 'Fêmea'
  }

  const calculateAge = () => {
    const birthDate = new Date(animal.data_nascimento)
    const today = new Date()
    let age = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    
    return age
  }

  return (
    <article
      className={`animal-card ${isHovered ? 'animal-card--hover' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleCardClick}
      role="article"
    >
      {/* Header */}
      <div className="animal-card__header">
        <h3 className="animal-card__title">{animal.nome}</h3>
        <div className={`animal-card__status animal-card__status--${getStatusColor(animal.status)}`}>
          {animal.status.charAt(0).toUpperCase() + animal.status.slice(1)}
        </div>
      </div>

      {/* Content */}
      <div className="animal-card__content">
        <div className="animal-card__info-grid">
          {/* Raça */}
          <div className="animal-card__info-item">
            <span className="animal-card__label">Raça</span>
            <span className="animal-card__value">{animal.raca}</span>
          </div>

          {/* RFID */}
          <div className="animal-card__info-item">
            <span className="animal-card__label">RFID</span>
            <span className="animal-card__value animal-card__rfid">{animal.rfid}</span>
          </div>

          {/* Gênero */}
          <div className="animal-card__info-item">
            <span className="animal-card__label">Gênero</span>
            <span className="animal-card__value">{getGenderLabel(animal.sexo)}</span>
          </div>

          {/* Peso Inicial */}
          <div className="animal-card__info-item">
            <span className="animal-card__label">Peso Inicial</span>
            <span className="animal-card__value">{animal.peso_inicial} kg</span>
          </div>

          {/* Idade */}
          <div className="animal-card__info-item">
            <span className="animal-card__label">Idade</span>
            <span className="animal-card__value">{calculateAge()} anos</span>
          </div>

          {/* Data Nascimento */}
          <div className="animal-card__info-item">
            <span className="animal-card__label">Nascimento</span>
            <span className="animal-card__value">
              {new Date(animal.data_nascimento).toLocaleDateString('pt-BR')}
            </span>
          </div>
        </div>
      </div>

      {/* Footer with Actions */}
      <div className="animal-card__footer">
        <button
          className="animal-card__action animal-card__action--edit"
          onClick={handleEdit}
          type="button"
          aria-label={`Editar ${animal.nome}`}
          title="Editar animal"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
          </svg>
          Editar
        </button>
        <button
          className="animal-card__action animal-card__action--delete"
          onClick={handleDelete}
          type="button"
          aria-label={`Deletar ${animal.nome}`}
          title="Deletar animal"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
          </svg>
          Deletar
        </button>
      </div>
    </article>
  )
}

export default AnimalCard

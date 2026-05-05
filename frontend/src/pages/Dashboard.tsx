import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAnimals } from '@hooks/useAnimals'
import { useAuth } from '@context/AuthContext'
import Button from '@components/atoms/Button'
import Card from '@components/atoms/Card'
import Modal from '@components/molecules/Modal'
import AnimalForm from '@components/molecules/AnimalForm'
import SearchBar from '@components/molecules/SearchBar'
import apiService from '@services/api'
import logoImg from '../assets/agrovision-logo.jpg'
import '../styles/global.css'
import '../styles/app-layout.css'
import '../styles/App.css'

function Dashboard() {
  const { animals, loading, error, refetch } = useAnimals()
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [hasSearched, setHasSearched] = useState(false)

  useEffect(() => {
    apiService.healthCheck().then(setIsHealthy)
  }, [])

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login', { replace: true })
    } catch (err) {
      console.error('Erro ao fazer logout:', err)
      // Mesmo com erro, fazer logout local
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      navigate('/login', { replace: true })
    }
  }

  const handleCreateAnimal = async (animalData: any) => {
    setIsSubmitting(true)
    try {
      await apiService.createAnimal(animalData)
      setIsModalOpen(false)
      refetch?.()
    } catch (err) {
      console.error('Erro ao criar animal:', err)
      alert('Erro ao criar animal. Tente novamente.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
  }

  const handleDeleteAnimal = async (id: number) => {
    try {
      await apiService.deleteAnimal(id)
      setDeleteConfirmId(null)
      refetch?.()
    } catch (err) {
      console.error('Erro ao deletar animal:', err)
      alert('Erro ao deletar animal. Tente novamente.')
    }
  }

  const handleSearch = async (query: string) => {
    setSearchQuery(query)
    setHasSearched(true)

    if (!query.trim()) {
      setSearchResults([])
      return
    }

    setIsSearching(true)
    try {
      // Buscar por RFID na API
      const animal = await apiService.getAnimalByRfid(query)
      setSearchResults([animal])
    } catch (err) {
      console.error('Erro ao buscar animal por RFID:', err)
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    setSearchResults([])
    setHasSearched(false)
  }

  return (
    <div className="app-container">
      <header>
        <div className="header__top">
          <div className="header__left">
            <img 
              src={logoImg} 
              alt="AgroVision Logo" 
              className="header__logo"
            />
            <h1>AgroVision</h1>
          </div>
          <div className="header__right">
            <Button 
              variant="danger" 
              size="sm"
              onClick={handleLogout}
            >
              Sair
            </Button>
          </div>
        </div>
        <p>Tecnologia inteligente para o campo</p>
        
        {isHealthy !== null && (
          <div className={`api-status ${isHealthy ? 'api-status--connected' : 'api-status--disconnected'}`}>
            {isHealthy ? '✅ API Conectada' : '❌ API Desconectada'}
          </div>
        )}
      </header>

      <main>
        <section>
          <div className="section-header">
            <h2>Animais</h2>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Button 
                variant="primary" 
                size="md"
                onClick={() => setIsModalOpen(true)}
              >
                Adicionar Animal
              </Button>
              <Button 
                variant="secondary" 
                size="md"
                onClick={() => navigate('/pesagens')}
              >
                Ver Pesagens
              </Button>
              <Button 
                variant="secondary" 
                size="md"
                onClick={() => navigate('/cotacoes')}
              >
                Ver Cotações
              </Button>
            </div>
          </div>

          {/* Barra de Busca por RFID */}
          <div style={{ marginBottom: '20px' }}>
            <SearchBar
              placeholder="Buscar por RFID (ex: RF12345678)..."
              onSearch={handleSearch}
              loading={isSearching}
            />
            {hasSearched && searchQuery && (
              <div style={{ marginTop: '10px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                <span>Resultados para: <strong>{searchQuery}</strong></span>
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={handleClearSearch}
                >
                  Limpar
                </Button>
              </div>
            )}
          </div>

          {loading && (
            <div className="loading">
              <p>Carregando animais...</p>
            </div>
          )}

          {error && (
            <div className="error-message">
              Erro: {error}
            </div>
          )}

          {hasSearched && searchQuery && isSearching && (
            <div className="loading">
              <p>Buscando animal...</p>
            </div>
          )}

          {hasSearched && searchQuery && !isSearching && searchResults.length === 0 && (
            <div className="empty-state">
              <p>Nenhum animal encontrado com RFID: {searchQuery}</p>
            </div>
          )}

          {!hasSearched && !loading && animals.length === 0 && !error && (
            <div className="empty-state">
              <p>Nenhum animal encontrado</p>
            </div>
          )}

          {/* Mostrar resultados de busca ou lista completa */}
          <div className="animals-grid">
            {(hasSearched && searchQuery ? searchResults : animals).map((animal) => (
              <Card 
                key={animal.id}
                title={animal.nome}
              >
                <div className="animal-card-content">
                  <div className="animal-info">
                    <div><strong>Raça:</strong> {animal.raca}</div>
                    <div><strong>RFID:</strong> {animal.rfid}</div>
                    <div><strong>Status:</strong> {animal.status}</div>
                    <div><strong>Peso Inicial:</strong> {animal.peso_inicial} kg</div>
                  </div>
                  <div className="animal-actions">
                    <Button 
                      variant="secondary" 
                      size="sm" 
                      fullWidth
                      onClick={() => navigate(`/animal/${animal.id}`)}
                    >
                      Detalhes
                    </Button>
                    <Button 
                      variant="danger" 
                      size="sm" 
                      fullWidth
                      onClick={() => setDeleteConfirmId(animal.id)}
                    >
                      Deletar
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </section>

        {/* Modal para criar novo animal */}
        <Modal
          isOpen={isModalOpen}
          title="Registrar Novo Animal"
          onClose={handleCloseModal}
          size="large"
        >
          <AnimalForm
            onSubmit={handleCreateAnimal}
            onCancel={handleCloseModal}
            isSubmitting={isSubmitting}
          />
        </Modal>

        {/* Modal de confirmação de exclusão */}
        <Modal
          isOpen={deleteConfirmId !== null}
          title="Confirmar Exclusão"
          onClose={() => setDeleteConfirmId(null)}
          onConfirm={() => deleteConfirmId && handleDeleteAnimal(deleteConfirmId)}
          variant="confirmation"
          isDanger={true}
          size="small"
        >
          <p>
            Tem certeza que deseja deletar este animal? Esta ação não pode ser desfeita.
          </p>
        </Modal>
      </main>
    </div>
  )
}

export default Dashboard

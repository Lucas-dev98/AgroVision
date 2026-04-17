import React, { useState, useEffect } from 'react'
import { useAnimals } from '@hooks/useAnimals'
import Button from '@components/atoms/Button'
import Card from '@components/atoms/Card'
import apiService from '@services/api'
import logoSvg from '@/assets/agrovision-logo.svg'
import './styles/global.css'
import './styles/app-layout.css'
import './styles/App.css'

function App() {
  const { animals, loading, error } = useAnimals()
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null)

  useEffect(() => {
    apiService.healthCheck().then(setIsHealthy)
  }, [])

  return (
    <div className="app-container">
      <header>
        <div className="header__top">
          <img 
            src={logoSvg} 
            alt="AgroVision Logo" 
            className="header__logo"
          />
          <h1>AgroVision</h1>
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
            <Button variant="primary" size="md">
              Adicionar Animal
            </Button>
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

          {!loading && animals.length === 0 && !error && (
            <div className="empty-state">
              <p>Nenhum animal encontrado</p>
            </div>
          )}

          <div className="animals-grid">
            {animals.map((animal) => (
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
                    <Button variant="secondary" size="sm" fullWidth>
                      Detalhes
                    </Button>
                    <Button variant="danger" size="sm" fullWidth>
                      Deletar
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App

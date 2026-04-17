import React, { useState, useEffect } from 'react'
import { useAnimals } from '@hooks/useAnimals'
import Button from '@components/atoms/Button'
import Card from '@components/atoms/Card'
import apiService from '@services/api'
import './styles/App.css'

function App() {
  const { animals, loading, error } = useAnimals()
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null)

  useEffect(() => {
    apiService.healthCheck().then(setIsHealthy)
  }, [])

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          🐄 AgroVision
        </h1>
        <p className="text-lg text-gray-600">
          Sistema de Gestão de Rebanho
        </p>
        
        <div className="mt-4">
          {isHealthy ? (
            <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded">
              ✅ API Conectada
            </span>
          ) : (
            <span className="inline-block bg-red-100 text-red-800 px-3 py-1 rounded">
              ❌ API Desconectada
            </span>
          )}
        </div>
      </header>

      <main>
        <section className="mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800">
              Animais
            </h2>
            <Button variant="primary" size="md">
              Adicionar Animal
            </Button>
          </div>

          {loading && (
            <div className="text-center py-8">
              <p className="text-gray-600">Carregando animais...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              Erro: {error}
            </div>
          )}

          {!loading && animals.length === 0 && !error && (
            <div className="text-center py-8">
              <p className="text-gray-600">Nenhum animal encontrado</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {animals.map((animal) => (
              <Card 
                key={animal.id}
                title={animal.nome}
              >
                <div className="space-y-2 text-sm">
                  <p><strong>Raça:</strong> {animal.raca}</p>
                  <p><strong>RFID:</strong> {animal.rfid}</p>
                  <p><strong>Status:</strong> {animal.status}</p>
                  <p><strong>Peso Inicial:</strong> {animal.peso_inicial} kg</p>
                  <div className="pt-4 flex gap-2">
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

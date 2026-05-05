import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '@components/atoms/Button'
import Modal from '@components/molecules/Modal'
import '../styles/global.css'
import '../styles/MLPage.css'

interface MLModel {
  id: string
  name: string
  type: 'anomaly_detection' | 'behavior_classification' | 'prediction'
  status: 'active' | 'training' | 'inactive'
  accuracy?: number
  last_trained?: string
  version: string
}

interface PredictionResult {
  id: string
  model_id: string
  input: string
  output: string
  confidence: number
  created_at: string
}

const MLPage: React.FC = () => {
  const navigate = useNavigate()
  
  const [models, setModels] = useState<MLModel[]>([
    {
      id: 'model_1',
      name: 'Detecção de Anomalias',
      type: 'anomaly_detection',
      status: 'active',
      accuracy: 0.94,
      last_trained: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      version: '2.1.0',
    },
    {
      id: 'model_2',
      name: 'Classificação de Comportamento',
      type: 'behavior_classification',
      status: 'active',
      accuracy: 0.88,
      last_trained: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      version: '1.5.0',
    },
    {
      id: 'model_3',
      name: 'Predição de Peso',
      type: 'prediction',
      status: 'training',
      version: '3.0.0-beta',
    },
  ])

  const [predictions, setPredictions] = useState<PredictionResult[]>([])
  const [selectedModel, setSelectedModel] = useState<MLModel | null>(null)
  const [isTrainingModalOpen, setIsTrainingModalOpen] = useState(false)
  const [isPredictionModalOpen, setIsPredictionModalOpen] = useState(false)
  const [isTraining, setIsTraining] = useState(false)
  const [isPredicting, setIsPredicting] = useState(false)
  const [predictionInput, setPredictionInput] = useState('')
  const [trainingParams, setTrainingParams] = useState({
    epochs: 10,
    batch_size: 32,
    learning_rate: 0.001,
  })

  const handleOpenTraining = (model: MLModel) => {
    setSelectedModel(model)
    setIsTrainingModalOpen(true)
  }

  const handleOpenPrediction = (model: MLModel) => {
    setSelectedModel(model)
    setIsPredictionModalOpen(true)
  }

  const handleStartTraining = async () => {
    if (!selectedModel) return

    setIsTraining(true)
    try {
      // TODO: Implementar chamada para API de treinamento
      // const response = await apiService.trainModel(selectedModel.id, trainingParams)
      
      // Simulação para prototipagem
      alert(`Treinamento iniciado para ${selectedModel.name}! (Simulação)`);
      
      // Atualizar status do modelo
      setModels(models.map(m => 
        m.id === selectedModel.id 
          ? { ...m, status: 'training' }
          : m
      ))
      
      setIsTrainingModalOpen(false)
    } catch (error: any) {
      alert('Erro ao iniciar treinamento: ' + (error.message || 'Tente novamente'))
      console.error('Erro ao treinar:', error)
    } finally {
      setIsTraining(false)
    }
  }

  const handleMakePrediction = async () => {
    if (!selectedModel || !predictionInput) {
      alert('Preencha o campo de entrada')
      return
    }

    setIsPredicting(true)
    try {
      // TODO: Implementar chamada para API de predição
      // const response = await apiService.predict(selectedModel.id, { input: predictionInput })
      
      // Simulação para prototipagem
      const mockPrediction: PredictionResult = {
        id: `pred_${Date.now()}`,
        model_id: selectedModel.id,
        input: predictionInput,
        output: `Resultado simulado para: ${predictionInput}`,
        confidence: Math.random() * 0.4 + 0.6, // 0.6 - 1.0
        created_at: new Date().toISOString(),
      }

      setPredictions([mockPrediction, ...predictions])
      setPredictionInput('')
      setIsPredictionModalOpen(false)
    } catch (error: any) {
      alert('Erro na predição: ' + (error.message || 'Tente novamente'))
      console.error('Erro na predição:', error)
    } finally {
      setIsPredicting(false)
    }
  }

  const handleBack = () => {
    navigate('/dashboard')
  }

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('pt-BR')
    } catch {
      return dateStr
    }
  }

  const getModelTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      anomaly_detection: 'Detecção de Anomalias',
      behavior_classification: 'Classificação de Comportamento',
      prediction: 'Predição',
    }
    return labels[type] || type
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'status--active',
      training: 'status--training',
      inactive: 'status--inactive',
    }
    return colors[status] || ''
  }

  return (
    <div className="ml-page">
      <div className="ml-page__header">
        <Button 
          onClick={handleBack} 
          variant="secondary"
        >
          ← Voltar
        </Button>
        <h1>Machine Learning (ML)</h1>
      </div>

      <div className="ml-page__content">
        {/* Models Section */}
        <section className="ml-section">
          <h2>Modelos Disponíveis</h2>
          <div className="models-grid">
            {models.map((model) => (
              <div key={model.id} className="model-card">
                <div className="model-header">
                  <h3>{model.name}</h3>
                  <span className={`status ${getStatusColor(model.status)}`}>
                    {model.status === 'active' ? '✓ Ativo' : model.status === 'training' ? '⚙ Treinando' : '✗ Inativo'}
                  </span>
                </div>

                <div className="model-info">
                  <p><strong>Tipo:</strong> {getModelTypeLabel(model.type)}</p>
                  <p><strong>Versão:</strong> {model.version}</p>
                  {model.accuracy !== undefined && (
                    <p><strong>Acurácia:</strong> {(model.accuracy * 100).toFixed(1)}%</p>
                  )}
                  {model.last_trained && (
                    <p><strong>Último Treinamento:</strong> {formatDate(model.last_trained)}</p>
                  )}
                </div>

                <div className="model-actions">
                  {model.status !== 'inactive' && (
                    <>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleOpenPrediction(model)}
                        disabled={model.status === 'training'}
                      >
                        Fazer Predição
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleOpenTraining(model)}
                      >
                        Treinar
                      </Button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Predictions Section */}
        <section className="ml-section">
          <h2>Histórico de Predições</h2>
          
          {predictions.length === 0 ? (
            <div className="predictions-empty">
              <p>Nenhuma predição realizada ainda</p>
            </div>
          ) : (
            <div className="predictions-table">
              <table>
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Modelo</th>
                    <th>Entrada</th>
                    <th>Saída</th>
                    <th>Confiança</th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.map((pred) => {
                    const model = models.find(m => m.id === pred.model_id)
                    return (
                      <tr key={pred.id}>
                        <td>{formatDate(pred.created_at)}</td>
                        <td>{model?.name || 'Modelo Desconhecido'}</td>
                        <td>{pred.input}</td>
                        <td>{pred.output}</td>
                        <td>
                          <span className="confidence-badge">
                            {(pred.confidence * 100).toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>

      {/* Training Modal */}
      <Modal
        isOpen={isTrainingModalOpen}
        onClose={() => setIsTrainingModalOpen(false)}
        title={`Treinar Modelo: ${selectedModel?.name}`}
        size="medium"
      >
        <div className="training-form">
          <div className="form-group">
            <label htmlFor="epochs">Épocas</label>
            <input
              id="epochs"
              type="number"
              value={trainingParams.epochs}
              onChange={(e) => setTrainingParams({
                ...trainingParams,
                epochs: parseInt(e.target.value) || 0
              })}
              min="1"
              max="100"
            />
          </div>

          <div className="form-group">
            <label htmlFor="batch_size">Tamanho do Batch</label>
            <input
              id="batch_size"
              type="number"
              value={trainingParams.batch_size}
              onChange={(e) => setTrainingParams({
                ...trainingParams,
                batch_size: parseInt(e.target.value) || 0
              })}
              min="1"
              max="256"
            />
          </div>

          <div className="form-group">
            <label htmlFor="learning_rate">Taxa de Aprendizado</label>
            <input
              id="learning_rate"
              type="number"
              value={trainingParams.learning_rate}
              onChange={(e) => setTrainingParams({
                ...trainingParams,
                learning_rate: parseFloat(e.target.value) || 0
              })}
              min="0.0001"
              max="0.1"
              step="0.0001"
            />
          </div>

          <div className="form-actions">
            <Button
              variant="secondary"
              onClick={() => setIsTrainingModalOpen(false)}
              disabled={isTraining}
            >
              Cancelar
            </Button>
            <Button
              variant="primary"
              onClick={handleStartTraining}
              disabled={isTraining}
            >
              {isTraining ? 'Treinando...' : 'Iniciar Treinamento'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Prediction Modal */}
      <Modal
        isOpen={isPredictionModalOpen}
        onClose={() => setIsPredictionModalOpen(false)}
        title={`Fazer Predição: ${selectedModel?.name}`}
        size="medium"
      >
        <div className="prediction-form">
          <div className="form-group">
            <label htmlFor="prediction_input">Dados de Entrada</label>
            <textarea
              id="prediction_input"
              value={predictionInput}
              onChange={(e) => setPredictionInput(e.target.value)}
              placeholder="Digite os dados para predição"
              rows={4}
            />
          </div>

          <div className="form-actions">
            <Button
              variant="secondary"
              onClick={() => setIsPredictionModalOpen(false)}
              disabled={isPredicting}
            >
              Cancelar
            </Button>
            <Button
              variant="primary"
              onClick={handleMakePrediction}
              disabled={isPredicting || !predictionInput}
            >
              {isPredicting ? 'Processando...' : 'Fazer Predição'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default MLPage

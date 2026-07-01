import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '@components/atoms/Button'
import Modal from '@components/molecules/Modal'
import apiService from '@services/api'
import '../styles/global.css'
import '../styles/VisionPage.css'

interface DetectionResult {
  id: string
  image_url: string
  detections: Array<{
    class: string
    confidence: number
    bbox: [number, number, number, number]
  }>
  created_at: string
}

const VisionPage: React.FC = () => {
  const navigate = useNavigate()
  
  const [detectionResults, setDetectionResults] = useState<DetectionResult[]>([])
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedResult, setSelectedResult] = useState<DetectionResult | null>(null)
  const [preview, setPreview] = useState<string | null>(null)

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setSelectedImage(file)

    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleDetect = async () => {
    if (!selectedImage) {
      alert('Selecione uma imagem primeiro')
      return
    }

    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('image', selectedImage)
      
      const result = await apiService.detectAnimals(formData) as unknown as DetectionResult
      
      setDetectionResults([result, ...detectionResults])
      setSelectedImage(null)
      setPreview(null)
      alert('Detecção realizada com sucesso!')
    } catch (error: any) {
      alert('Erro na detecção: ' + (error.response?.data?.error || error.message || 'Tente novamente'))
      console.error('Erro na detecção:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleBack = () => {
    navigate('/dashboard')
  }

  const handleViewResult = (result: DetectionResult) => {
    setSelectedResult(result)
    setIsModalOpen(true)
  }

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('pt-BR')
    } catch {
      return dateStr
    }
  }

  return (
    <div className="vision-page">
      <div className="vision-page__header">
        <Button 
          onClick={handleBack} 
          variant="secondary"
        >
          ← Voltar
        </Button>
        <h1>Detecção de Animais (YOLO Vision)</h1>
      </div>

      <div className="vision-page__upload-section">
        <div className="upload-card">
          <h2>Enviar Imagem para Detecção</h2>
          
          {preview ? (
            <div className="preview-container">
              <img src={preview} alt="Preview" className="preview-image" />
              <p className="file-name">{selectedImage?.name}</p>
            </div>
          ) : (
            <div className="upload-area">
              <div className="upload-icon">📸</div>
              <p>Clique para selecionar uma imagem ou arraste aqui</p>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="file-input"
              />
            </div>
          )}

          <div className="upload-actions">
            {preview && (
              <Button
                variant="secondary"
                onClick={() => {
                  setSelectedImage(null)
                  setPreview(null)
                }}
              >
                Limpar Seleção
              </Button>
            )}
            <Button
              variant="primary"
              onClick={handleDetect}
              disabled={!selectedImage || isLoading}
            >
              {isLoading ? 'Detectando...' : 'Detectar Animais'}
            </Button>
          </div>
        </div>
      </div>

      <div className="vision-page__results-section">
        <h2>Histórico de Detecções</h2>
        
        {detectionResults.length === 0 ? (
          <div className="results-empty">
            <p>Nenhuma detecção realizada ainda</p>
          </div>
        ) : (
          <div className="results-grid">
            {detectionResults.map((result) => (
              <div key={result.id} className="result-card">
                <img 
                  src={result.image_url} 
                  alt="Detection result" 
                  className="result-image"
                />
                <div className="result-info">
                  <p className="result-date">{formatDate(result.created_at)}</p>
                  <p className="result-count">
                    {result.detections.length} objeto(s) detectado(s)
                  </p>
                  <Button
                    variant="secondary"
                    size="sm"
                    fullWidth
                    onClick={() => handleViewResult(result)}
                  >
                    Ver Detalhes
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal de detalhes */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedResult(null)
        }}
        title="Detalhes da Detecção"
        size="large"
      >
        {selectedResult && (
          <div className="detection-details">
            <img 
              src={selectedResult.image_url} 
              alt="Full detection" 
              className="full-image"
            />
            <div className="detections-list">
              <h3>Objetos Detectados:</h3>
              {selectedResult.detections.length === 0 ? (
                <p>Nenhum objeto detectado</p>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Classe</th>
                      <th>Confiança</th>
                      <th>Posição</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedResult.detections.map((detection, idx) => (
                      <tr key={idx}>
                        <td>{detection.class}</td>
                        <td>{(detection.confidence * 100).toFixed(1)}%</td>
                        <td>
                          [{detection.bbox[0]}, {detection.bbox[1]}, {detection.bbox[2]}, {detection.bbox[3]}]
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default VisionPage

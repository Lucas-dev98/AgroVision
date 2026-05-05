import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Animal, Pesagem } from '@types/index'
import apiService from '@services/api'
import Modal from '@components/molecules/Modal'
import AnimalForm from '@components/molecules/AnimalForm'
import Button from '@components/atoms/Button'
import '../styles/global.css'
import '../styles/AnimalDetailPage.css'

interface PesagemFormData {
  peso_kg: number
  peso_arroba: number
  data: string
  hora?: string
  observacoes?: string
}

const AnimalDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  
  const [animal, setAnimal] = useState<Animal | null>(null)
  const [pesagens, setPesagens] = useState<Pesagem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditMode, setIsEditMode] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleteConfirming, setDeleteConfirming] = useState(false)
  const [isPesagemModalOpen, setIsPesagemModalOpen] = useState(false)
  const [isPesagemSubmitting, setIsPesagemSubmitting] = useState(false)
  const [pesagemFormData, setPesagemFormData] = useState<PesagemFormData>({
    peso_kg: 0,
    peso_arroba: 0,
    data: new Date().toISOString().split('T')[0],
    hora: new Date().toTimeString().slice(0, 5),
    observacoes: '',
  })

  useEffect(() => {
    const loadData = async () => {
      if (!id) return

      try {
        setLoading(true)
        const [animalData, pesagensData] = await Promise.all([
          apiService.getAnimal(parseInt(id)),
          apiService.getPesagens(parseInt(id)).catch(() => []),
        ])
        setAnimal(animalData)
        setPesagens(pesagensData)
        setError(null)
      } catch (err: any) {
        setError(err.message || 'Erro ao carregar dados')
        console.error('Erro ao carregar dados:', err)
      } finally {
        setLoading(false)
      }
    }

    loadData()
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

  const handleAddPesagem = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!animal || pesagemFormData.peso_kg <= 0) {
      alert('Preencha todos os campos obrigatórios corretamente')
      return
    }

    setIsPesagemSubmitting(true)
    try {
      await apiService.createPesagem({
        animal_id: animal.id,
        peso_kg: pesagemFormData.peso_kg,
        peso_arroba: pesagemFormData.peso_arroba,
        data: pesagemFormData.data,
        hora: pesagemFormData.hora,
        observacoes: pesagemFormData.observacoes,
      })

      setPesagemFormData({
        peso_kg: 0,
        peso_arroba: 0,
        data: new Date().toISOString().split('T')[0],
        hora: new Date().toTimeString().slice(0, 5),
        observacoes: '',
      })

      setIsPesagemModalOpen(false)
      
      // Recarregar pesagens
      const updatedPesagens = await apiService.getPesagens(animal.id).catch(() => [])
      setPesagens(updatedPesagens)
    } catch (err: any) {
      alert('Erro ao criar pesagem: ' + (err.message || 'Tente novamente'))
      console.error('Erro ao criar pesagem:', err)
    } finally {
      setIsPesagemSubmitting(false)
    }
  }

  const handlePesagemInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target

    if (name === 'peso_kg' || name === 'peso_arroba') {
      setPesagemFormData({
        ...pesagemFormData,
        [name]: parseFloat(value) || 0,
      })
    } else {
      setPesagemFormData({
        ...pesagemFormData,
        [name]: value,
      })
    }
  }

  const handleBack = () => {
    navigate('/dashboard')
  }

  const calculateGainSinceEntry = () => {
    if (pesagens.length === 0) return 0
    return pesagens[pesagens.length - 1].peso_kg - animal!.peso_inicial
  }

  const calculateAverageDailyGain = () => {
    if (pesagens.length < 2) return 0
    const firstPesagem = pesagens[0]
    const lastPesagem = pesagens[pesagens.length - 1]
    const days = Math.floor(
      (new Date(lastPesagem.data).getTime() - new Date(firstPesagem.data).getTime()) / (1000 * 60 * 60 * 24)
    )
    if (days === 0) return 0
    return ((lastPesagem.peso_kg - firstPesagem.peso_kg) / days).toFixed(2)
  }

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('pt-BR')
    } catch {
      return dateStr
    }
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
              <p>{formatDate(animal.data_nascimento)}</p>
            </div>
            <div className="animal-detail-page__info-item">
              <label>Data de Entrada</label>
              <p>{formatDate(animal.data_entrada)}</p>
            </div>
            <div className="animal-detail-page__info-item">
              <label>Última Atualização</label>
              <p>{formatDate(animal.updated_at)}</p>
            </div>
          </div>

          {/* Pesagens Stats */}
          {pesagens.length > 0 && (
            <div className="animal-detail-page__stats">
              <div className="stat-item">
                <label>Peso Atual (kg)</label>
                <p>{pesagens[pesagens.length - 1].peso_kg.toFixed(2)}</p>
              </div>
              <div className="stat-item">
                <label>Ganho Desde Entrada</label>
                <p>{calculateGainSinceEntry().toFixed(2)} kg</p>
              </div>
              <div className="stat-item">
                <label>Ganho Médio Diário</label>
                <p>{calculateAverageDailyGain()} kg/dia</p>
              </div>
              <div className="stat-item">
                <label>Total de Pesagens</label>
                <p>{pesagens.length}</p>
              </div>
            </div>
          )}

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

          {/* Pesagens Section */}
          <div className="animal-detail-page__pesagens">
            <div className="pesagens-header">
              <h2>Histórico de Pesagens</h2>
              <Button 
                onClick={() => setIsPesagemModalOpen(true)}
                variant="primary"
                size="sm"
              >
                Adicionar Pesagem
              </Button>
            </div>

            {pesagens.length === 0 ? (
              <div className="pesagens-empty">
                <p>Nenhuma pesagem registrada</p>
              </div>
            ) : (
              <div className="pesagens-table">
                <table>
                  <thead>
                    <tr>
                      <th>Data</th>
                      <th>Peso (kg)</th>
                      <th>Peso (arroba)</th>
                      <th>Observações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...pesagens].reverse().map((pesagem) => (
                      <tr key={pesagem.id}>
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

      {/* Modal para adicionar pesagem */}
      <Modal
        isOpen={isPesagemModalOpen}
        onClose={() => setIsPesagemModalOpen(false)}
        title="Adicionar Pesagem"
        size="medium"
      >
        <form className="pesagem-form" onSubmit={handleAddPesagem}>
          <div className="form-group">
            <label htmlFor="data">Data *</label>
            <input
              id="data"
              type="date"
              name="data"
              value={pesagemFormData.data}
              onChange={handlePesagemInputChange}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="peso_kg">Peso (kg) *</label>
              <input
                id="peso_kg"
                type="number"
                name="peso_kg"
                value={pesagemFormData.peso_kg}
                onChange={handlePesagemInputChange}
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
                value={pesagemFormData.peso_arroba}
                onChange={handlePesagemInputChange}
                step="0.01"
                min="0"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="hora">Hora</label>
            <input
              id="hora"
              type="time"
              name="hora"
              value={pesagemFormData.hora}
              onChange={handlePesagemInputChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="observacoes">Observações</label>
            <textarea
              id="observacoes"
              name="observacoes"
              value={pesagemFormData.observacoes}
              onChange={handlePesagemInputChange}
              placeholder="Adicione observações"
              rows={3}
            />
          </div>

          <div className="form-actions">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsPesagemModalOpen(false)}
              disabled={isPesagemSubmitting}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isPesagemSubmitting}
            >
              {isPesagemSubmitting ? 'Salvando...' : 'Salvar Pesagem'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default AnimalDetailPage

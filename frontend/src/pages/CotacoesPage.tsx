import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Cotacao } from '@types/index'
import apiService from '@services/api'
import Button from '@components/atoms/Button'
import Modal from '@components/molecules/Modal'
import '../styles/global.css'
import '../styles/CotacoesPage.css'

interface CotacaoFormData {
  preco_arroba: number
  data_referencia: string
}

const CotacoesPage: React.FC = () => {
  const navigate = useNavigate()
  
  const [cotacoes, setCotacoes] = useState<Cotacao[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<CotacaoFormData>({
    preco_arroba: 0,
    data_referencia: new Date().toISOString().split('T')[0],
  })

  useEffect(() => {
    loadCotacoes()
  }, [])

  const loadCotacoes = async () => {
    try {
      setLoading(true)
      const data = await apiService.getCotacoes()
      setCotacoes(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar cotações')
      console.error('Erro ao carregar cotações:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const { name, value } = e.target

    if (name === 'preco_arroba') {
      setFormData({
        ...formData,
        [name]: parseFloat(value) || 0,
      })
    } else {
      setFormData({
        ...formData,
        [name]: value,
      })
    }
  }

  const resetForm = () => {
    setFormData({
      preco_arroba: 0,
      data_referencia: new Date().toISOString().split('T')[0],
    })
    setEditingId(null)
  }

  const handleOpenModal = (cotacao?: Cotacao) => {
    if (cotacao) {
      setEditingId(cotacao.id)
      setFormData({
        preco_arroba: cotacao.preco_arroba,
        data_referencia: cotacao.data_referencia,
      })
    } else {
      resetForm()
    }
    setIsModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (formData.preco_arroba <= 0) {
      alert('O preço deve ser maior que zero')
      return
    }

    setIsSubmitting(true)
    try {
      if (editingId) {
        // Atualizar cotação (se a API suportar)
        // await apiService.updateCotacao(editingId, formData)
        alert('Atualização de cotação não implementada na API')
      } else {
        await apiService.createCotacao({
          preco_arroba: formData.preco_arroba,
          data_referencia: formData.data_referencia,
        })
      }

      resetForm()
      setIsModalOpen(false)
      loadCotacoes()
    } catch (err: any) {
      alert('Erro ao salvar cotação: ' + (err.message || 'Tente novamente'))
      console.error('Erro ao salvar cotação:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja deletar esta cotação?')) {
      return
    }

    try {
      // Deletar cotação (se a API suportar)
      // await apiService.deleteCotacao(id)
      alert('Deleção de cotação não implementada na API')
      // loadCotacoes()
    } catch (err: any) {
      alert('Erro ao deletar cotação: ' + (err.message || 'Tente novamente'))
      console.error('Erro ao deletar cotação:', err)
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

  const getAveragePrice = () => {
    if (cotacoes.length === 0) return 0
    const sum = cotacoes.reduce((acc, c) => acc + c.preco_arroba, 0)
    return (sum / cotacoes.length).toFixed(2)
  }

  const getMaxPrice = () => {
    if (cotacoes.length === 0) return 0
    return Math.max(...cotacoes.map(c => c.preco_arroba)).toFixed(2)
  }

  const getMinPrice = () => {
    if (cotacoes.length === 0) return 0
    return Math.min(...cotacoes.map(c => c.preco_arroba)).toFixed(2)
  }

  return (
    <div className="cotacoes-page">
      <div className="cotacoes-page__header">
        <Button 
          onClick={handleBack} 
          variant="secondary"
          className="cotacoes-page__back-btn"
        >
          ← Voltar
        </Button>
        <h1>Cotações de Preço</h1>
      </div>

      {/* Stats Cards */}
      {!loading && cotacoes.length > 0 && (
        <div className="cotacoes-page__stats">
          <div className="stat-card">
            <h3>Preço Médio</h3>
            <p className="stat-value">R$ {getAveragePrice()}</p>
          </div>
          <div className="stat-card">
            <h3>Preço Máximo</h3>
            <p className="stat-value">R$ {getMaxPrice()}</p>
          </div>
          <div className="stat-card">
            <h3>Preço Mínimo</h3>
            <p className="stat-value">R$ {getMinPrice()}</p>
          </div>
        </div>
      )}

      <div className="cotacoes-page__actions">
        <Button 
          onClick={() => handleOpenModal()}
          variant="primary"
        >
          Adicionar Cotação
        </Button>
      </div>

      {loading && (
        <div className="cotacoes-page__loading">
          <div className="spinner"></div>
          <p>Carregando cotações...</p>
        </div>
      )}

      {error && (
        <div className="cotacoes-page__error">
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && cotacoes.length === 0 && (
        <div className="cotacoes-page__empty">
          <p>Nenhuma cotação registrada</p>
        </div>
      )}

      {!loading && cotacoes.length > 0 && (
        <div className="cotacoes-page__table">
          <table>
            <thead>
              <tr>
                <th>Data de Referência</th>
                <th>Preço (arroba)</th>
                <th>Data de Criação</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {cotacoes.map((cotacao) => (
                <tr key={cotacao.id}>
                  <td>{formatDate(cotacao.data_referencia)}</td>
                  <td>R$ {cotacao.preco_arroba.toFixed(2)}</td>
                  <td>{formatDate(cotacao.criada_em)}</td>
                  <td>
                    <div className="action-buttons">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleOpenModal(cotacao)}
                      >
                        Editar
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(cotacao.id)}
                      >
                        Deletar
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal para criar/editar cotação */}
      <Modal
        isOpen={isModalOpen}
        title={editingId ? 'Editar Cotação' : 'Adicionar Cotação'}
        onClose={() => {
          setIsModalOpen(false)
          resetForm()
        }}
        size="medium"
      >
        <form className="cotacao-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="data_referencia">Data de Referência *</label>
            <input
              id="data_referencia"
              type="date"
              name="data_referencia"
              value={formData.data_referencia}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="preco_arroba">Preço por Arroba (R$) *</label>
            <input
              id="preco_arroba"
              type="number"
              name="preco_arroba"
              value={formData.preco_arroba}
              onChange={handleInputChange}
              step="0.01"
              min="0"
              placeholder="0.00"
              required
            />
          </div>

          <div className="form-actions">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setIsModalOpen(false)
                resetForm()
              }}
              disabled={isSubmitting}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Salvando...' : editingId ? 'Atualizar' : 'Salvar Cotação'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default CotacoesPage

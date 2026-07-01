import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAnimals } from '@hooks/useAnimals'
import Button from '@components/atoms/Button'
import Card from '@components/atoms/Card'
import Modal from '@components/molecules/Modal'
import AnimalForm from '@components/molecules/AnimalForm'
import SearchBar from '@components/molecules/SearchBar'
import apiService from '@services/api'
import { Animal } from '@/types'
import '../styles/global.css'
import '../styles/Dashboard.css'

type DashboardAnimalFormData = {
  id?: string
  nome: string
  raca: string
  rfid: string
  status?: 'ativo' | 'inativo' | 'vendido'
  peso_inicial: number
  sexo: 'M' | 'F'
  data_nascimento: string
}

const dashboardModules = [
  {
    title: 'Animais',
    description: 'Cadastro, busca por RFID, detalhes e ações rápidas sobre o rebanho.',
    path: '/dashboard',
    accent: 'Core',
  },
  {
    title: 'Pesagens',
    description: 'Histórico de ganho de peso e acompanhamento do desempenho do lote.',
    path: '/pesagens',
    accent: 'Operação',
  },
  {
    title: 'Cotações',
    description: 'Preço médio, mínimo e máximo da arroba para decisões de mercado.',
    path: '/cotacoes',
    accent: 'Mercado',
  },
  {
    title: 'Vision',
    description: 'Fluxo de detecção por imagem para apoiar inventário e auditoria.',
    path: '/vision',
    accent: 'IA Visual',
  },
  {
    title: 'Machine Learning',
    description: 'Treino e predição com modelos dedicados ao comportamento e desempenho.',
    path: '/ml',
    accent: 'IA Preditiva',
  },
  {
    title: 'Propriedades',
    description: 'Fazendas, talhões e áreas produtivas com visão multiunidade.',
    path: '/rural/propriedades',
    accent: 'Estrutura',
  },
  {
    title: 'Custos',
    description: 'Receitas, despesas e rentabilidade por operação e área.',
    path: '/rural/custos',
    accent: 'Financeiro',
  },
  {
    title: 'Estoque',
    description: 'Insumos críticos, consumo e previsão de ruptura.',
    path: '/rural/estoque',
    accent: 'Suprimentos',
  },
  {
    title: 'Clima',
    description: 'Previsões, alertas e planejamento orientado pelo tempo.',
    path: '/rural/clima',
    accent: 'Ambiente',
  },
  {
    title: 'Assistente IA',
    description: 'Chat especializado para dúvidas e apoio à decisão rural.',
    path: '/rural/assistente',
    accent: 'Consulta',
  },
  {
    title: 'Voz',
    description: 'Comandos de voz para registros rápidos no campo.',
    path: '/rural/voz',
    accent: 'Mobilidade',
  },
  {
    title: 'Drone',
    description: 'Monitoramento aéreo para falhas e estresse hídrico.',
    path: '/rural/drone',
    accent: 'Aéreo',
  },
  {
    title: 'Calendário',
    description: 'Planejamento de safra, tratos, aplicações e colheita.',
    path: '/rural/calendario',
    accent: 'Agenda',
  },
]

function Dashboard() {
  const { animals, loading, error, refetch } = useAnimals()
  const navigate = useNavigate()
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null)
  const [pesagensCount, setPesagensCount] = useState<number | null>(null)
  const [cotacoesCount, setCotacoesCount] = useState<number | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<Animal[]>([])
  const [hasSearched, setHasSearched] = useState(false)

  useEffect(() => {
    const loadOverview = async () => {
      try {
        const [pesagens, cotacoes, healthy] = await Promise.all([
          apiService.getPesagens(),
          apiService.getCotacoes(),
          apiService.healthCheck(),
        ])

        setPesagensCount(pesagens.length)
        setCotacoesCount(cotacoes.length)
        setIsHealthy(healthy)
      } catch (err) {
        console.error('Erro ao carregar visao geral:', err)
        setIsHealthy(false)
      }
    }

    loadOverview()
  }, [])

  const activeAnimals = animals.filter(animal => animal.status === 'ATIVO').length
  const soldAnimals = animals.filter(animal => animal.status === 'VENDIDO').length
  const averageInitialWeight = animals.length
    ? (animals.reduce((sum, animal) => sum + animal.peso_inicial, 0) / animals.length).toFixed(1)
    : '0.0'
  const totalAnimals = animals.length
  const recentAnimals = [...animals]
    .slice()
    .sort((a, b) => b.id - a.id)
    .slice(0, 6)
  const visibleAnimals = hasSearched && searchQuery ? searchResults : recentAnimals

  const handleCreateAnimal = async (animalData: DashboardAnimalFormData) => {
    setIsSubmitting(true)
    try {
      const status = animalData.status === 'vendido' ? 'VENDIDO' : 'ATIVO'
      await apiService.createAnimal({
        nome: animalData.nome,
        raca: animalData.raca,
        rfid: animalData.rfid,
        status,
        peso_inicial: animalData.peso_inicial,
        data_nascimento: animalData.data_nascimento,
      })
      setIsModalOpen(false)
      refetch?.()
    } catch (err) {
      console.error('Erro ao criar animal:', err)
      alert('Erro ao criar animal. Tente novamente.')
    } finally {
      setIsSubmitting(false)
    }
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
    <div className="dashboard-page">
      <section className="dashboard-hero">
        <div className="dashboard-hero__copy">
          <p className="dashboard-hero__eyebrow">Centro de controle</p>
          <h2>Operação completa do rebanho em uma única visão</h2>
          <p>
            Monitore animais, pesagens, cotações, visão computacional e modelos de IA com
            navegação rápida, decisões apoiadas por dados e um fluxo pronto para uso diário.
          </p>

          <div className="dashboard-hero__actions">
            <Button variant="primary" size="lg" onClick={() => setIsModalOpen(true)}>
              Novo animal
            </Button>
            <Button variant="secondary" size="lg" onClick={() => navigate('/pesagens')}>
              Registrar pesagem
            </Button>
            <Button variant="secondary" size="lg" onClick={() => navigate('/vision')}>
              Abrir Vision
            </Button>
          </div>
        </div>

        <div className="dashboard-hero__status-card">
          <div className={`dashboard-status ${isHealthy ? 'dashboard-status--ok' : 'dashboard-status--warn'}`}>
            <span className="dashboard-status__dot" />
            {isHealthy === null ? 'Validando backend...' : isHealthy ? 'Backend e gateway online' : 'Backend com atenção'}
          </div>
          <div className="dashboard-hero__status-list">
            <div>
              <strong>{totalAnimals}</strong>
              <span>animais cadastrados</span>
            </div>
            <div>
              <strong>{activeAnimals}</strong>
              <span>ativos em acompanhamento</span>
            </div>
            <div>
              <strong>{pesagensCount ?? '...'}</strong>
              <span>pesagens registradas</span>
            </div>
            <div>
              <strong>{cotacoesCount ?? '...'}</strong>
              <span>cotações disponíveis</span>
            </div>
          </div>
        </div>
      </section>

      <section className="dashboard-metrics">
        <article className="dashboard-metric-card">
          <span>Total do rebanho</span>
          <strong>{totalAnimals}</strong>
          <p>Animais conhecidos pelo gateway</p>
        </article>
        <article className="dashboard-metric-card dashboard-metric-card--accent">
          <span>Animais ativos</span>
          <strong>{activeAnimals}</strong>
          <p>Prontos para manejo e pesagem</p>
        </article>
        <article className="dashboard-metric-card">
          <span>Animais vendidos</span>
          <strong>{soldAnimals}</strong>
          <p>Histórico para auditoria</p>
        </article>
        <article className="dashboard-metric-card">
          <span>Peso inicial médio</span>
          <strong>{averageInitialWeight} kg</strong>
          <p>Base média do rebanho atual</p>
        </article>
      </section>

      <section className="dashboard-modules">
        {dashboardModules.map(module => (
          <Card key={module.title} className="dashboard-module-card">
            <div className="dashboard-module-card__kicker">{module.accent}</div>
            <h3>{module.title}</h3>
            <p>{module.description}</p>
            <Button variant="secondary" size="sm" onClick={() => navigate(module.path)}>
              Abrir módulo
            </Button>
          </Card>
        ))}
      </section>

      <section className="dashboard-grid">
        <div className="dashboard-panel dashboard-panel--main">
          <div className="dashboard-panel__header">
            <div>
              <h2>Animais recentes</h2>
              <p>Busque por RFID ou acesse os detalhes com um clique.</p>
            </div>
            <Button variant="primary" size="sm" onClick={() => setIsModalOpen(true)}>
              Adicionar animal
            </Button>
          </div>

          <SearchBar
            placeholder="Buscar por RFID (ex: RF12345678)..."
            onSearch={handleSearch}
            loading={isSearching}
          />

          {hasSearched && searchQuery && (
            <div className="dashboard-search-summary">
              <span>
                Resultados para <strong>{searchQuery}</strong>
              </span>
              <Button variant="secondary" size="sm" onClick={handleClearSearch}>
                Limpar
              </Button>
            </div>
          )}

          {error && <div className="dashboard-alert dashboard-alert--error">Erro: {error}</div>}

          {loading && (
            <div className="dashboard-skeleton-grid" aria-label="Carregando animais">
              {Array.from({ length: 3 }).map((_, index) => (
                <div key={index} className="dashboard-skeleton-card" />
              ))}
            </div>
          )}

          {!loading && hasSearched && searchQuery && isSearching && (
            <div className="dashboard-empty-state">Buscando animal...</div>
          )}

          {!loading && hasSearched && searchQuery && !isSearching && searchResults.length === 0 && (
            <div className="dashboard-empty-state">
              Nenhum animal encontrado com RFID: {searchQuery}
            </div>
          )}

          {!loading && visibleAnimals.length === 0 && !hasSearched && !error && (
            <div className="dashboard-empty-state">
              Nenhum animal encontrado ainda. Use o botão Novo animal para começar.
            </div>
          )}

          <div className="dashboard-animals-grid">
            {visibleAnimals.map(animal => (
              <Card
                key={animal.id}
                title={animal.nome}
                className="dashboard-animal-card"
                onClick={() => navigate(`/animal/${animal.id}`)}
              >
                <div className="dashboard-animal-card__meta">
                  <span>Raça: {animal.raca}</span>
                  <span>RFID: {animal.rfid}</span>
                  <span>Peso inicial: {animal.peso_inicial} kg</span>
                </div>
                <div className={`dashboard-animal-chip dashboard-animal-chip--${animal.status.toLowerCase()}`}>
                  {animal.status}
                </div>
              </Card>
            ))}
          </div>
        </div>

        <aside className="dashboard-panel dashboard-panel--side">
          <div className="dashboard-panel__header">
            <div>
              <h2>Fluxos essenciais</h2>
              <p>Atalhos para as jornadas mais usadas no dia a dia.</p>
            </div>
          </div>

          <div className="dashboard-action-stack">
            <button className="dashboard-action-card" type="button" onClick={() => navigate('/pesagens')}>
              <span>Pesagens</span>
              <strong>Registrar e acompanhar ganho de peso</strong>
              <p>Use para medir evolução e alimentar relatórios operacionais.</p>
            </button>
            <button className="dashboard-action-card" type="button" onClick={() => navigate('/cotacoes')}>
              <span>Cotações</span>
              <strong>Consultar mercado e tendências</strong>
              <p>Compare preço médio, mínimo e máximo da arroba.</p>
            </button>
            <button className="dashboard-action-card" type="button" onClick={() => navigate('/vision')}>
              <span>Vision</span>
              <strong>Executar detecção por imagem</strong>
              <p>Ideal para fluxos assistidos por IA visual e auditoria rápida.</p>
            </button>
            <button className="dashboard-action-card" type="button" onClick={() => navigate('/ml')}>
              <span>Machine Learning</span>
              <strong>Treinar e prever com dados do rebanho</strong>
              <p>Centralize modelos e predições para apoiar decisões.</p>
            </button>
          </div>
        </aside>
      </section>

      <Modal
        isOpen={isModalOpen}
        title="Registrar Novo Animal"
        onClose={() => setIsModalOpen(false)}
        size="large"
      >
        <AnimalForm
          onSubmit={handleCreateAnimal}
          onCancel={() => setIsModalOpen(false)}
          isSubmitting={isSubmitting}
        />
      </Modal>

      <Modal
        isOpen={deleteConfirmId !== null}
        title="Confirmar Exclusão"
        onClose={() => setDeleteConfirmId(null)}
        onConfirm={() => deleteConfirmId && handleDeleteAnimal(deleteConfirmId)}
        variant="confirmation"
        isDanger
        size="small"
      >
        <p>Tem certeza que deseja deletar este animal? Esta ação não pode ser desfeita.</p>
      </Modal>
    </div>
  )
}

export default Dashboard

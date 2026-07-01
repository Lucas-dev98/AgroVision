import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Button from '@components/atoms/Button'
import Card from '@components/atoms/Card'
import '../styles/RuralModulePage.css'

type ModuleKey =
  | 'propriedades'
  | 'custos'
  | 'estoque'
  | 'clima'
  | 'assistente'
  | 'voz'
  | 'drone'
  | 'calendario'

type ModuleDefinition = {
  title: string
  kicker: string
  summary: string
  status: string
  highlights: string[]
  actions: string[]
}

const moduleCatalog: Record<ModuleKey, ModuleDefinition> = {
  propriedades: {
    title: 'Gestão de Propriedades',
    kicker: 'Estrutura fundiária',
    summary: 'Cadastro de fazendas, talhões e áreas produtivas com visão operacional da propriedade inteira.',
    status: 'Estrutura pronta para multi-propriedade',
    highlights: ['Fazendas', 'Talhões', 'Áreas produtivas', 'Lotes por unidade'],
    actions: ['Cadastrar propriedade', 'Importar talhões', 'Vincular cultura'],
  },
  custos: {
    title: 'Controle de Custos',
    kicker: 'Financeiro operacional',
    summary: 'Acompanhe despesas, receitas, custos por hectare e margem por atividade em um único fluxo.',
    status: 'Foco em lucratividade por unidade',
    highlights: ['Insumos', 'Mão de obra', 'Manutenção', 'Margem por talhão'],
    actions: ['Registrar despesa', 'Criar centro de custo', 'Comparar rentabilidade'],
  },
  estoque: {
    title: 'Gestão de Estoque',
    kicker: 'Suprimentos e consumo',
    summary: 'Monitore insumos, previsão de esgotamento e reposição antes de faltar no campo.',
    status: 'Previsão e alertas de ruptura',
    highlights: ['Insumos críticos', 'Consumo médio', 'Reposição', 'Alertas de baixo estoque'],
    actions: ['Adicionar item', 'Registrar saída', 'Gerar alerta'],
  },
  clima: {
    title: 'Clima Inteligente',
    kicker: 'Monitoramento ambiental',
    summary: 'Integração meteorológica com alertas de chuva, vento, temperatura e risco operacional.',
    status: 'Alertas meteorológicos e previsões',
    highlights: ['Chuva', 'Temperatura', 'Vento', 'Janela operacional'],
    actions: ['Configurar alertas', 'Ver previsão', 'Receber notificação'],
  },
  assistente: {
    title: 'Assistente IA',
    kicker: 'Consulta inteligente',
    summary: 'Chat treinado para a realidade rural, respondendo perguntas sobre a propriedade e o manejo.',
    status: 'Base conversacional especializada',
    highlights: ['Perguntas operacionais', 'Sugestões de manejo', 'Histórico contextual', 'Respostas rápidas'],
    actions: ['Abrir chat', 'Salvar comando', 'Consultar histórico'],
  },
  voz: {
    title: 'Entrada por Voz',
    kicker: 'Operação mãos-livres',
    summary: 'Registros rápidos no campo com comandos de voz para reduzir tempo de digitação.',
    status: 'Foco em mobilidade e rapidez',
    highlights: ['Comandos curtos', 'Registro de eventos', 'Confirmação automática', 'Modo offline futuro'],
    actions: ['Gravar comando', 'Revisar transcrição', 'Enviar registro'],
  },
  drone: {
    title: 'Monitoramento por Drone',
    kicker: 'Visão aérea avançada',
    summary: 'Fluxo para inspeção de áreas, falhas, estresse hídrico e comparação visual entre mapas.',
    status: 'Fase avançada do roadmap',
    highlights: ['Falhas de cobertura', 'Estresse hídrico', 'Mapas comparativos', 'Rotas de voo'],
    actions: ['Importar voo', 'Analisar imagem', 'Gerar relatório'],
  },
  calendario: {
    title: 'Calendário Agrícola',
    kicker: 'Planejamento anual',
    summary: 'Organize semeadura, tratos, colheita, aplicações e eventos sazonais por cultura.',
    status: 'Base para planejamento por cultura',
    highlights: ['Safras', 'Aplicações', 'Colheita', 'Eventos críticos'],
    actions: ['Novo evento', 'Ver agenda', 'Exportar cronograma'],
  },
}

const defaultModule: ModuleDefinition = {
  title: 'Módulo rural',
  kicker: 'Plataforma modular',
  summary: 'Funcionalidade em definição para ampliar o escopo do AgroVision com uma experiência consistente.',
  status: 'Em expansão',
  highlights: ['Catálogo modular', 'Experiência unificada', 'Base para novos fluxos', 'Evolução incremental'],
  actions: ['Explorar módulo', 'Voltar ao painel', 'Definir prioridade'],
}

const modules = [
  { id: 'propriedades', label: 'Propriedades' },
  { id: 'custos', label: 'Custos' },
  { id: 'estoque', label: 'Estoque' },
  { id: 'clima', label: 'Clima' },
  { id: 'assistente', label: 'Assistente IA' },
  { id: 'voz', label: 'Voz' },
  { id: 'drone', label: 'Drone' },
  { id: 'calendario', label: 'Calendário' },
] as const

const RuralModulePage: React.FC = () => {
  const navigate = useNavigate()
  const params = useParams<{ moduleId: ModuleKey }>()
  const moduleId = params.moduleId && moduleCatalog[params.moduleId] ? params.moduleId : undefined
  const module = moduleId ? moduleCatalog[moduleId] : defaultModule

  return (
    <div className="rural-module-page">
      <section className="rural-module-hero">
        <div>
          <p className="rural-module-hero__eyebrow">{module.kicker}</p>
          <h2>{module.title}</h2>
          <p>{module.summary}</p>
        </div>
        <div className="rural-module-hero__status">
          <span>{module.status}</span>
          <strong>{module.actions[0]}</strong>
        </div>
      </section>

      <section className="rural-module-grid">
        <Card title="Capacidades" className="rural-module-card">
          <div className="rural-module-chip-list">
            {module.highlights.map(item => (
              <span key={item} className="rural-module-chip">{item}</span>
            ))}
          </div>
        </Card>

        <Card title="Próximas ações" className="rural-module-card">
          <div className="rural-module-action-list">
            {module.actions.map(action => (
              <button key={action} type="button" className="rural-module-action">
                {action}
              </button>
            ))}
          </div>
        </Card>

        <Card title="Módulos da visão" className="rural-module-card rural-module-card--full">
          <div className="rural-module-nav-grid">
            {modules.map(item => (
              <button
                key={item.id}
                type="button"
                className={`rural-module-nav-item ${moduleId === item.id ? 'rural-module-nav-item--active' : ''}`}
                onClick={() => navigate(`/rural/${item.id}`)}
              >
                {item.label}
              </button>
            ))}
          </div>
          <div className="rural-module-footer-actions">
            <Button variant="secondary" size="sm" onClick={() => navigate('/dashboard')}>
              Voltar ao painel
            </Button>
            <Button variant="primary" size="sm" onClick={() => navigate('/dashboard')}>
              Abrir centro de controle
            </Button>
          </div>
        </Card>
      </section>
    </div>
  )
}

export default RuralModulePage
import React, { useMemo, useState } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import Button from '@components/atoms/Button'
import { useAuth } from '@context/AuthContext'
import logoImg from '@/assets/agrovision-logo.jpg'
import './AppShell.css'

interface AppShellProps {
  children: React.ReactNode
}

const navigationItems = [
  { to: '/dashboard', label: 'Painel', description: 'Visão geral do rebanho' },
  { to: '/dashboard', label: 'Animais', description: 'Cadastro e acompanhamento' },
  { to: '/pesagens', label: 'Pesagens', description: 'Evolução e ganho de peso' },
  { to: '/cotacoes', label: 'Cotações', description: 'Preço por arroba' },
  { to: '/vision', label: 'Vision', description: 'Detecção por imagem' },
  { to: '/ml', label: 'ML', description: 'Treino e predição' },
  { to: '/rural/propriedades', label: 'Propriedades', description: 'Fazendas e talhões' },
  { to: '/rural/custos', label: 'Custos', description: 'Receitas e despesas' },
  { to: '/rural/estoque', label: 'Estoque', description: 'Insumos e consumo' },
  { to: '/rural/clima', label: 'Clima', description: 'Alertas meteorológicos' },
  { to: '/rural/assistente', label: 'Assistente IA', description: 'Perguntas sobre a propriedade' },
  { to: '/rural/voz', label: 'Voz', description: 'Registros mãos-livres' },
  { to: '/rural/drone', label: 'Drone', description: 'Monitoramento aéreo' },
  { to: '/rural/calendario', label: 'Calendário', description: 'Planejamento agrícola' },
]

const pageMeta: Record<string, { kicker: string; title: string; subtitle: string }> = {
  '/dashboard': {
    kicker: 'Centro de comando',
    title: 'Gestão do rebanho em tempo real',
    subtitle: 'KPIs, atalhos e módulos integrados para operar o AgroVision com foco no fluxo diário.',
  },
  '/pesagens': {
    kicker: 'Operação',
    title: 'Pesagens e ganho de peso',
    subtitle: 'Registre a evolução e acompanhe o desempenho do lote com precisão.',
  },
  '/cotacoes': {
    kicker: 'Mercado',
    title: 'Cotações de arroba',
    subtitle: 'Compare tendências e tome decisões com base no mercado atual.',
  },
  '/vision': {
    kicker: 'IA visual',
    title: 'Detecção de animais por imagem',
    subtitle: 'Acompanhe resultados de visão computacional em um fluxo claro e auditável.',
  },
  '/ml': {
    kicker: 'IA preditiva',
    title: 'Machine learning aplicado ao rebanho',
    subtitle: 'Treine modelos e consulte predições em uma interface objetiva.',
  },
  '/rural/propriedades': {
    kicker: 'Estrutura fundiária',
    title: 'Gestão de propriedades e talhões',
    subtitle: 'Cadastre fazendas, áreas produtivas e vínculos por cultura.',
  },
  '/rural/custos': {
    kicker: 'Financeiro operacional',
    title: 'Custos e rentabilidade',
    subtitle: 'Acompanhe despesas, receitas e margem por unidade produtiva.',
  },
  '/rural/estoque': {
    kicker: 'Suprimentos',
    title: 'Gestão de estoque e consumo',
    subtitle: 'Visualize insumos, previsão de ruptura e reposição.',
  },
  '/rural/clima': {
    kicker: 'Ambiente',
    title: 'Clima inteligente e alertas',
    subtitle: 'Monitore previsões e eventos meteorológicos relevantes.',
  },
  '/rural/assistente': {
    kicker: 'Consulta inteligente',
    title: 'Assistente IA para agricultura',
    subtitle: 'Responda dúvidas e acelere a tomada de decisão no campo.',
  },
  '/rural/voz': {
    kicker: 'Operação mãos-livres',
    title: 'Entrada por voz',
    subtitle: 'Registros rápidos com transcrição e validação.',
  },
  '/rural/drone': {
    kicker: 'Visão aérea',
    title: 'Monitoramento por drone',
    subtitle: 'Apoie inspeções, falhas de cobertura e estresse hídrico.',
  },
  '/rural/calendario': {
    kicker: 'Planejamento',
    title: 'Calendário agrícola',
    subtitle: 'Organize safra, aplicações, tratos e colheita.',
  },
}

const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const meta = useMemo(() => {
    const matchedRoute =
      location.pathname.startsWith('/animal/')
        ? '/dashboard'
        : location.pathname.startsWith('/rural/')
          ? location.pathname
          : location.pathname
    return pageMeta[matchedRoute] || pageMeta['/dashboard']
  }, [location.pathname])

  const userLabel = user?.nome || user?.email || 'Operador conectado'
  const userInitials = userLabel
    .split(' ')
    .map(part => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await logout()
      navigate('/login', { replace: true })
    } finally {
      setIsLoggingOut(false)
    }
  }

  return (
    <div className="app-shell">
      <aside className="app-shell__sidebar">
        <div className="app-shell__brand">
          <img src={logoImg} alt="AgroVision" className="app-shell__brand-logo" />
          <div>
            <strong>AgroVision</strong>
            <p>Control Center</p>
          </div>
        </div>

        <nav className="app-shell__nav" aria-label="Navegação principal">
          {navigationItems.map(item => (
            <NavLink
              key={`${item.to}-${item.label}`}
              to={item.to}
              className={({ isActive }) =>
                `app-shell__nav-item ${isActive ? 'app-shell__nav-item--active' : ''}`
              }
            >
              <span className="app-shell__nav-label">{item.label}</span>
              <span className="app-shell__nav-description">{item.description}</span>
            </NavLink>
          ))}
        </nav>

        <div className="app-shell__sidebar-card">
          <div className="app-shell__sidebar-kicker">Sessão atual</div>
          <div className="app-shell__sidebar-user">{userLabel}</div>
          <div className="app-shell__sidebar-email">{user?.email || 'Gateway autenticado'}</div>
          <div className="app-shell__sidebar-actions">
            <Button variant="secondary" size="sm" fullWidth onClick={() => navigate('/dashboard')}>
              Ir para o painel
            </Button>
            <Button variant="danger" size="sm" fullWidth onClick={handleLogout} disabled={isLoggingOut}>
              {isLoggingOut ? 'Saindo...' : 'Sair'}
            </Button>
          </div>
        </div>
      </aside>

      <div className="app-shell__workspace">
        <header className="app-shell__topbar">
          <div>
            <p className="app-shell__kicker">{meta.kicker}</p>
            <h1 className="app-shell__title">{meta.title}</h1>
            <p className="app-shell__subtitle">{meta.subtitle}</p>
          </div>

          <div className="app-shell__topbar-actions">
            <div className="app-shell__status-pill">
              <span className="app-shell__status-dot" />
              Plataforma ativa
            </div>
            <div className="app-shell__user-chip" aria-label="Usuário autenticado">
              <span className="app-shell__user-avatar">{userInitials || 'AV'}</span>
              <div>
                <strong>{userLabel}</strong>
                <p>
                  {location.pathname === '/dashboard'
                    ? 'Painel principal'
                    : location.pathname.startsWith('/rural/')
                      ? 'Módulo rural'
                      : location.pathname}
                </p>
              </div>
            </div>
          </div>
        </header>

        <main className="app-shell__content">{children}</main>
      </div>
    </div>
  )
}

export default AppShell
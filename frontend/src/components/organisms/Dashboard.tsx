import React from 'react'
import './Dashboard.css'

interface ModelStatus {
  trained: boolean
  accuracy: number
  lastUpdate: string | null
}

interface TrainingStatus {
  models: {
    behavior: ModelStatus
    anomaly: ModelStatus
    reid: ModelStatus
    temporal: ModelStatus
  }
}

interface Activity {
  id: string
  type: 'animal_added' | 'prediction' | 'training' | 'alert'
  message: string
  timestamp: string
}

interface DashboardData {
  totalAnimals: number
  activeAnimals: number
  inactiveAnimals: number
  soldAnimals: number
  averageWeight: number
  trainingStatus: TrainingStatus
  recentActivities: Activity[]
}

interface DashboardProps {
  data?: DashboardData
  isLoading?: boolean
  error?: string
  onRefresh?: () => void
}

const Dashboard: React.FC<DashboardProps> = ({ data, isLoading = false, error, onRefresh }) => {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'animal_added':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
        )
      case 'prediction':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="21 8 21 21 3 21 3 10" />
            <line x1="1" y1="1" x2="23" y2="1" />
            <path d="M10 5h4" />
          </svg>
        )
      case 'training':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
          </svg>
        )
      default:
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="1" />
          </svg>
        )
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const renderSkeletons = () => {
    return Array.from({ length: 4 }).map((_, index) => (
      <div key={`skeleton-${index}`} className="dashboard__skeleton">
        <div className="dashboard__skeleton-header" />
        <div className="dashboard__skeleton-content" />
      </div>
    ))
  }

  if (isLoading) {
    return (
      <section className="dashboard" role="region" aria-label="Dashboard">
        <div className="dashboard__header">
          <h1 className="dashboard__title">Dashboard</h1>
        </div>
        <div className="dashboard__grid">
          {renderSkeletons()}
        </div>
        <section className="dashboard__section">
          <h2 className="dashboard__section-title">Status dos Modelos</h2>
          <div className="dashboard__models-grid">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={`model-skeleton-${index}`} className="dashboard__skeleton">
                <div className="dashboard__skeleton-header" />
                <div className="dashboard__skeleton-content" />
              </div>
            ))}
          </div>
        </section>
      </section>
    )
  }

  if (error) {
    return (
      <section className="dashboard" role="region" aria-label="Dashboard">
        <div className="dashboard__error">
          <h2>Erro ao carregar</h2>
          <p>{error}</p>
          {onRefresh && (
            <button className="dashboard__retry-button" onClick={onRefresh}>
              Tentar Novamente
            </button>
          )}
        </div>
      </section>
    )
  }

  if (!data) {
    return (
      <section className="dashboard" role="region" aria-label="Dashboard">
        <div className="dashboard__empty">
          <p>Nenhum dado disponível</p>
        </div>
      </section>
    )
  }

  return (
    <section className="dashboard" role="region" aria-label="Dashboard">
      {/* Header */}
      <div className="dashboard__header">
        <h1 className="dashboard__title">Dashboard</h1>
        {onRefresh && (
          <button className="dashboard__refresh" onClick={onRefresh} aria-label="Atualizar dashboard">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 4 23 10 17 10" />
              <polyline points="1 20 1 14 7 14" />
              <path d="M3.51 9a9 9 0 0114.85-3.36M20.49 15a9 9 0 01-14.85 3.36" />
            </svg>
          </button>
        )}
      </div>

      {/* KPI Grid */}
      <div className="dashboard__grid">
        <div className="dashboard__kpi" aria-label="Total de animais">
          <div className="dashboard__kpi-icon dashboard__kpi-icon--primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z" />
            </svg>
          </div>
          <div className="dashboard__kpi-content">
            <p className="dashboard__kpi-label">Total de Animais</p>
            <p className="dashboard__kpi-value">{data.totalAnimals}</p>
          </div>
        </div>

        <div className="dashboard__kpi" aria-label="Animais ativos">
          <div className="dashboard__kpi-icon dashboard__kpi-icon--success">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          </div>
          <div className="dashboard__kpi-content">
            <p className="dashboard__kpi-label">Animais Ativos</p>
            <p className="dashboard__kpi-value">{data.activeAnimals}</p>
          </div>
        </div>

        <div className="dashboard__kpi" aria-label="Peso médio">
          <div className="dashboard__kpi-icon dashboard__kpi-icon--info">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2v20M2 12h20" />
            </svg>
          </div>
          <div className="dashboard__kpi-content">
            <p className="dashboard__kpi-label">Peso Médio</p>
            <p className="dashboard__kpi-value">{data.averageWeight.toFixed(1)} kg</p>
          </div>
        </div>

        <div className="dashboard__kpi" aria-label="Animais vendidos">
          <div className="dashboard__kpi-icon dashboard__kpi-icon--warning">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
              <polyline points="13 2 13 9 20 9" />
            </svg>
          </div>
          <div className="dashboard__kpi-content">
            <p className="dashboard__kpi-label">Vendidos</p>
            <p className="dashboard__kpi-value">{data.soldAnimals}</p>
          </div>
        </div>
      </div>

      {/* Training Status */}
      <section className="dashboard__section">
        <h2 className="dashboard__section-title">Status dos Modelos</h2>
        <div className="dashboard__models-grid">
          {Object.entries(data.trainingStatus.models).map(([modelName, modelData]) => (
            <article
              key={modelName}
              className={`dashboard__model-card ${modelData.trained ? 'dashboard__model-card--trained' : 'dashboard__model-card--pending'}`}
            >
              <div className="dashboard__model-header">
                <h3 className="dashboard__model-name">
                  {modelName.charAt(0).toUpperCase() + modelName.slice(1)}
                </h3>
                <span className={`dashboard__model-badge ${modelData.trained ? 'dashboard__model-badge--trained' : 'dashboard__model-badge--pending'}`}>
                  {modelData.trained ? 'Treinado' : 'Pendente'}
                </span>
              </div>

              {modelData.trained && (
                <div className="dashboard__model-content">
                  <div className="dashboard__accuracy">
                    <label>Acurácia</label>
                    <div className="dashboard__progress-bar">
                      <div
                        className="dashboard__progress-fill"
                        style={{ width: `${modelData.accuracy * 100}%` }}
                      />
                    </div>
                    <span className="dashboard__accuracy-value">{(modelData.accuracy * 100).toFixed(1)}%</span>
                  </div>

                  {modelData.lastUpdate && (
                    <p className="dashboard__model-date">Atualizado em: {formatDate(modelData.lastUpdate)}</p>
                  )}
                </div>
              )}

              {!modelData.trained && (
                <p className="dashboard__model-pending-text">Aguardando treinamento inicial</p>
              )}
            </article>
          ))}
        </div>
      </section>

      {/* Recent Activities */}
      <section className="dashboard__section">
        <h2 className="dashboard__section-title">Atividades Recentes</h2>
        <div className="dashboard__activities">
          {data.recentActivities.length > 0 ? (
            data.recentActivities.map((activity) => (
              <div key={activity.id} className={`dashboard__activity-item dashboard__activity-item--${activity.type}`}>
                <div className="dashboard__activity-icon">{getActivityIcon(activity.type)}</div>
                <div className="dashboard__activity-content">
                  <p className="dashboard__activity-message">{activity.message}</p>
                  <time className="dashboard__activity-time">{formatDate(activity.timestamp)}</time>
                </div>
              </div>
            ))
          ) : (
            <p className="dashboard__no-activities">Nenhuma atividade recente</p>
          )}
        </div>
      </section>
    </section>
  )
}

export default Dashboard

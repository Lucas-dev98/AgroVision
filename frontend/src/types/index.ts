/**
 * Tipos base para AgroVision Frontend
 */

export interface Animal {
  id: number
  nome: string
  raca: string
  data_nascimento: string
  rfid: string
  lote_id: number
  status: 'ATIVO' | 'VENDIDO' | 'FALECIDO'
  peso_inicial: number
  data_entrada: string
  created_at: string
  updated_at: string
}

export interface Pesagem {
  id: number
  animal_id: number
  peso_kg: number
  peso_arroba: number
  data: string
  hora?: string
  observacoes?: string
  created_at: string
  updated_at: string
}

export interface Cotacao {
  id: number
  preco_arroba: number
  data_referencia: string
  criada_em: string
  atualizada_em: string
}

export interface Property {
  id: string
  user_id: string
  name: string
  total_area: number
  planted_area: number
  location_lat: number
  location_lng: number
  soil_type: string
  created_at: string
  updated_at: string
}

export interface DashboardData {
  animal: Animal
  pesagens: Pesagem[]
  cotacoes: Cotacao[]
  valor_total: number
}

export interface MLModel {
  id: string
  name: string
  type: 'anomaly_detection' | 'behavior_classification' | 'prediction'
  status: 'active' | 'training' | 'inactive'
  accuracy?: number
  last_trained?: string
  version: string
}

export interface PredictionResult {
  id: string
  model_id: string
  input: string
  output: string
  confidence: number
  created_at: string
}

export interface ApiResponse<T> {
  data?: T
  status: number
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}

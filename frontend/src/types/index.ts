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

export interface DashboardData {
  animal: Animal
  pesagens: Pesagem[]
  cotacoes: Cotacao[]
  valor_total: number
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

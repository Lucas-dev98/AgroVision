import axios, { AxiosInstance } from 'axios'
import { Animal, Pesagem, Cotacao, DashboardData, PaginatedResponse } from '@types/index'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Interceptor para adicionar token JWT se existir
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })
  }

  /**
   * Animal Service
   */
  async getAnimals(): Promise<PaginatedResponse<Animal>> {
    const response = await this.client.get<PaginatedResponse<Animal>>('/animals')
    return response.data
  }

  async getAnimal(id: number): Promise<Animal> {
    const response = await this.client.get<Animal>(`/animals/${id}`)
    return response.data
  }

  async getAnimalByRfid(rfid: string): Promise<Animal> {
    const response = await this.client.get<Animal>(`/animals/rfid/${rfid}`)
    return response.data
  }

  async createAnimal(data: Partial<Animal>): Promise<Animal> {
    const response = await this.client.post<Animal>('/animals', data)
    return response.data
  }

  async updateAnimal(id: number, data: Partial<Animal>): Promise<Animal> {
    const response = await this.client.put<Animal>(`/animals/${id}`, data)
    return response.data
  }

  async deleteAnimal(id: number): Promise<void> {
    await this.client.delete(`/animals/${id}`)
  }

  /**
   * Pesagem Service
   */
  async getPesagens(animalId?: number): Promise<Pesagem[]> {
    const response = await this.client.get<Pesagem[]>('/pesagens', {
      params: animalId ? { animal_id: animalId } : {},
    })
    return response.data
  }

  async getPesagem(id: number): Promise<Pesagem> {
    const response = await this.client.get<Pesagem>(`/pesagens/${id}`)
    return response.data
  }

  async getPesagemHistorico(animalId: number): Promise<Pesagem[]> {
    const response = await this.client.get<Pesagem[]>(`/pesagens/animal/${animalId}/historico`)
    return response.data
  }

  async getPesagemUltima(animalId: number): Promise<Pesagem> {
    const response = await this.client.get<Pesagem>(`/pesagens/animal/${animalId}/ultima`)
    return response.data
  }

  async getPesagemGanho(animalId: number): Promise<{ ganho_kg: number; periodo_dias: number }> {
    const response = await this.client.get<{ ganho_kg: number; periodo_dias: number }>(`/pesagens/animal/${animalId}/ganho`)
    return response.data
  }

  async createPesagem(data: Partial<Pesagem>): Promise<Pesagem> {
    const response = await this.client.post<Pesagem>('/pesagens', data)
    return response.data
  }

  /**
   * Cotacao Service
   */
  async getCotacoes(): Promise<Cotacao[]> {
    const response = await this.client.get<Cotacao[]>('/cotacoes')
    return response.data
  }

  async getCotacao(id: number): Promise<Cotacao> {
    const response = await this.client.get<Cotacao>(`/cotacoes/${id}`)
    return response.data
  }

  async getCotacaoAtual(): Promise<Cotacao> {
    const response = await this.client.get<Cotacao>('/cotacoes/atual')
    return response.data
  }

  async getCotacaoMedia(): Promise<{ preco_medio: number; periodo_dias: number }> {
    const response = await this.client.get<{ preco_medio: number; periodo_dias: number }>('/cotacoes/media')
    return response.data
  }

  async getCotacaoHistorico(): Promise<Cotacao[]> {
    const response = await this.client.get<Cotacao[]>('/cotacoes/historico')
    return response.data
  }

  async createCotacao(data: Partial<Cotacao>): Promise<Cotacao> {
    const response = await this.client.post<Cotacao>('/cotacoes', data)
    return response.data
  }

  /**
   * Dashboard Aggregation
   */
  async getDashboard(animalId: number): Promise<DashboardData> {
    const response = await this.client.get<DashboardData>(`/dashboard/animal/${animalId}`)
    return response.data
  }

  async getAllDashboards(): Promise<DashboardData[]> {
    const response = await this.client.get<DashboardData[]>('/dashboard/animals')
    return response.data
  }

  /**
   * Health Check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health')
      return response.status === 200
    } catch {
      return false
    }
  }
}

export default new ApiService()

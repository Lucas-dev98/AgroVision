import axios, { AxiosInstance } from 'axios'
import { Animal, Pesagem, Cotacao, DashboardData, PaginatedResponse } from '@types/index'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api/v1'

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
    const response = await this.client.get<PaginatedResponse<Animal>>('/animais')
    return response.data
  }

  async getAnimal(id: number): Promise<Animal> {
    const response = await this.client.get<Animal>(`/animais/${id}`)
    return response.data
  }

  async createAnimal(data: Partial<Animal>): Promise<Animal> {
    const response = await this.client.post<Animal>('/animais', data)
    return response.data
  }

  async updateAnimal(id: number, data: Partial<Animal>): Promise<Animal> {
    const response = await this.client.put<Animal>(`/animais/${id}`, data)
    return response.data
  }

  async deleteAnimal(id: number): Promise<void> {
    await this.client.delete(`/animais/${id}`)
  }

  /**
   * Pesagem Service
   */
  async getPesagens(animalId: number): Promise<Pesagem[]> {
    const response = await this.client.get<Pesagem[]>(`/pesagens`, {
      params: { animal_id: animalId },
    })
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

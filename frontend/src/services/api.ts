import axios, { AxiosInstance } from 'axios'
import { Animal, Pesagem, Cotacao, DashboardData, PaginatedResponse, MLModel, PredictionResult, Property } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

interface ApiAnimal {
  id: number
  name: string
  breed: string
  ear_tag: string
  birth_date?: string
  lote_id?: number
  status: Animal['status']
  peso_inicial?: number
  created_at: string
  updated_at: string
}

interface ListAnimalsResponse {
  count?: number
  data?: ApiAnimal[]
}

type GenericObject = Record<string, unknown>

interface VisionResultsResponse {
  results?: GenericObject[]
}

interface MLModelsResponse {
  models?: MLModel[]
}

interface MLPredictionsResponse {
  predictions?: PredictionResult[]
}

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
   * Mapear dados da API para o tipo Animal esperado pelo frontend
   */
  private mapApiAnimalToAnimal(apiAnimal: ApiAnimal): Animal {
    return {
      id: apiAnimal.id,
      nome: apiAnimal.name,
      raca: apiAnimal.breed,
      rfid: apiAnimal.ear_tag,
      data_nascimento: apiAnimal.birth_date || '',
      lote_id: apiAnimal.lote_id || 0,
      status: apiAnimal.status,
      peso_inicial: apiAnimal.peso_inicial || 0,
      data_entrada: apiAnimal.created_at,
      created_at: apiAnimal.created_at,
      updated_at: apiAnimal.updated_at,
    }
  }

  /**
   * Animal Service
   */
  async getAnimals(): Promise<PaginatedResponse<Animal>> {
    const response = await this.client.get<ListAnimalsResponse>('/animals')
    const { count, data } = response.data
    return {
      items: (data || []).map((animal) => this.mapApiAnimalToAnimal(animal)),
      total: count || 0,
      page: 1,
      size: count || 0
    }
  }

  async getAnimal(id: number): Promise<Animal> {
    const response = await this.client.get<ApiAnimal>(`/animals/${id}`)
    return this.mapApiAnimalToAnimal(response.data)
  }

  async getAnimalByRfid(rfid: string): Promise<Animal> {
    const response = await this.client.get<ApiAnimal>(`/animals/ear-tag/${rfid}`)
    return this.mapApiAnimalToAnimal(response.data)
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
   * Property Service
   */
  async getProperties(): Promise<Property[]> {
    const response = await this.client.get<Property[] | { properties?: Property[] }>('/properties')
    if (Array.isArray(response.data)) {
      return response.data
    }
    return response.data.properties || []
  }

  async getProperty(id: string): Promise<Property> {
    const response = await this.client.get<Property>(`/properties/${id}`)
    return response.data
  }

  async createProperty(data: Omit<Property, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<Property> {
    const response = await this.client.post<Property>('/properties', data)
    return response.data
  }

  async updateProperty(id: string, data: Omit<Property, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<Property> {
    const response = await this.client.put<Property>(`/properties/${id}`, data)
    return response.data
  }

  async deleteProperty(id: string): Promise<void> {
    await this.client.delete(`/properties/${id}`)
  }

  /**
   * Vision Service
   */
  async detectAnimals(formData: FormData): Promise<GenericObject> {
    const response = await this.client.post<GenericObject>('/vision/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async getVisionResult(resultId: string): Promise<GenericObject> {
    const response = await this.client.get<GenericObject>(`/vision/results/${resultId}`)
    return response.data
  }

  async listVisionResults(): Promise<GenericObject[]> {
    const response = await this.client.get<VisionResultsResponse>('/vision/results')
    return response.data.results || []
  }

  /**
   * ML Service
   */
  async getMLModels(): Promise<MLModel[]> {
    const response = await this.client.get<MLModelsResponse>('/ml/models')
    return response.data.models || []
  }

  async getMLModel(modelId: string): Promise<GenericObject> {
    const response = await this.client.get<GenericObject>(`/ml/models/${modelId}`)
    return response.data
  }

  async trainModel(modelId: string, params: {
    epochs: number
    batch_size: number
    learning_rate: number
  }): Promise<GenericObject> {
    const response = await this.client.post<GenericObject>('/ml/train', {
      model_id: modelId,
      ...params,
    })
    return response.data
  }

  async predict(modelId: string, input: string): Promise<PredictionResult> {
    const response = await this.client.post<PredictionResult>('/ml/predict', {
      model_id: modelId,
      input,
    })
    return response.data
  }

  async getMLPredictions(): Promise<PredictionResult[]> {
    const response = await this.client.get<MLPredictionsResponse>('/ml/predictions')
    return response.data.predictions || []
  }

  async getMLPrediction(predictionId: string): Promise<GenericObject> {
    const response = await this.client.get<GenericObject>(`/ml/predictions/${predictionId}`)
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

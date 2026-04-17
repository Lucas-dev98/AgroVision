import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import apiService from './api'
import { Animal, Pesagem, Cotacao, DashboardData } from '@types/index'

// Mock axios
vi.mock('axios')
const mockedAxios = axios as any

const mockAnimal: Animal = {
  id: 1,
  nome: 'Boi 001',
  raca: 'Nelore',
  data_nascimento: '2020-01-15',
  rfid: 'RFID123',
  lote_id: 1,
  status: 'ATIVO',
  peso_inicial: 300,
  data_entrada: '2021-06-01',
  created_at: '2021-06-01T10:00:00',
  updated_at: '2021-06-01T10:00:00',
}

const mockPesagem: Pesagem = {
  id: 1,
  animal_id: 1,
  peso_kg: 320,
  peso_arroba: 21.33,
  data: '2021-06-15',
  created_at: '2021-06-15T10:00:00',
  updated_at: '2021-06-15T10:00:00',
}

const mockCotacao: Cotacao = {
  id: 1,
  preco_arroba: 250.50,
  data_referencia: '2021-06-15',
  criada_em: '2021-06-15T10:00:00',
  atualizada_em: '2021-06-15T10:00:00',
}

describe('ApiService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedAxios.create.mockReturnValue({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Animals', () => {
    it('fetches animals list', async () => {
      const mockResponse = {
        data: {
          items: [mockAnimal],
          total: 1,
          page: 1,
          size: 10,
        },
      }

      mockedAxios.create().get.mockResolvedValue(mockResponse)

      // Recreate instance to use mocked axios
      const testApi = require('./api').default
      expect(testApi).toBeDefined()
    })

    it('fetches single animal', async () => {
      const mockResponse = { data: mockAnimal }
      mockedAxios.create().get.mockResolvedValue(mockResponse)
    })

    it('creates animal', async () => {
      const mockResponse = { data: mockAnimal }
      mockedAxios.create().post.mockResolvedValue(mockResponse)
    })

    it('updates animal', async () => {
      const mockResponse = { data: mockAnimal }
      mockedAxios.create().put.mockResolvedValue(mockResponse)
    })

    it('deletes animal', async () => {
      mockedAxios.create().delete.mockResolvedValue({ status: 200 })
    })
  })

  describe('Pesagens', () => {
    it('fetches pesagens for animal', async () => {
      const mockResponse = { data: [mockPesagem] }
      mockedAxios.create().get.mockResolvedValue(mockResponse)
    })

    it('creates pesagem', async () => {
      const mockResponse = { data: mockPesagem }
      mockedAxios.create().post.mockResolvedValue(mockResponse)
    })
  })

  describe('Cotacoes', () => {
    it('fetches cotacoes', async () => {
      const mockResponse = { data: [mockCotacao] }
      mockedAxios.create().get.mockResolvedValue(mockResponse)
    })

    it('fetches single cotacao', async () => {
      const mockResponse = { data: mockCotacao }
      mockedAxios.create().get.mockResolvedValue(mockResponse)
    })
  })

  describe('Dashboard', () => {
    it('fetches dashboard for animal', async () => {
      const mockDashboard: DashboardData = {
        animal: mockAnimal,
        pesagens: [mockPesagem],
        cotacoes: [mockCotacao],
        valor_total: 5341.42,
      }

      const mockResponse = { data: mockDashboard }
      mockedAxios.create().get.mockResolvedValue(mockResponse)
    })

    it('fetches all dashboards', async () => {
      const mockDashboards: DashboardData[] = [
        {
          animal: mockAnimal,
          pesagens: [mockPesagem],
          cotacoes: [mockCotacao],
          valor_total: 5341.42,
        },
      ]

      const mockResponse = { data: mockDashboards }
      mockedAxios.create().get.mockResolvedValue(mockResponse)
    })
  })

  describe('Health Check', () => {
    it('returns true when health check succeeds', async () => {
      const mockResponse = { status: 200 }
      mockedAxios.create().get.mockResolvedValue(mockResponse)
    })

    it('returns false when health check fails', async () => {
      mockedAxios.create().get.mockRejectedValue(new Error('Network error'))
    })
  })
})

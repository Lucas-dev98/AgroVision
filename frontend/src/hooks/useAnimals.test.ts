import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useAnimals, useAnimal } from './useAnimals'
import * as apiService from '@services/api'

// Mock do serviço de API
vi.mock('@services/api', () => ({
  default: {
    getAnimals: vi.fn(),
    getAnimal: vi.fn(),
  },
}))

const mockAnimal = {
  id: 1,
  nome: 'Boi 001',
  raca: 'Nelore',
  data_nascimento: '2020-01-15',
  rfid: 'RFID123',
  lote_id: 1,
  status: 'ATIVO' as const,
  peso_inicial: 300,
  data_entrada: '2021-06-01',
  created_at: '2021-06-01T10:00:00',
  updated_at: '2021-06-01T10:00:00',
}

const mockAnimalsResponse = {
  items: [mockAnimal],
  total: 1,
  page: 1,
  size: 10,
}

describe('useAnimals Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches animals on mount', async () => {
    const getAnimalsMock = vi.spyOn(apiService.default, 'getAnimals').mockResolvedValue(mockAnimalsResponse)

    const { result } = renderHook(() => useAnimals())

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(getAnimalsMock).toHaveBeenCalledTimes(1)
    expect(result.current.animals).toEqual([mockAnimal])
    expect(result.current.error).toBe(null)
  })

  it('handles fetch error', async () => {
    const error = new Error('API Error')
    vi.spyOn(apiService.default, 'getAnimals').mockRejectedValue(error)

    const { result } = renderHook(() => useAnimals())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.animals).toEqual([])
    expect(result.current.error).toBe('API Error')
  })

  it('refetches animals on demand', async () => {
    const getAnimalsMock = vi.spyOn(apiService.default, 'getAnimals').mockResolvedValue(mockAnimalsResponse)

    const { result } = renderHook(() => useAnimals())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(getAnimalsMock).toHaveBeenCalledTimes(1)

    await result.current.refetch()

    expect(getAnimalsMock).toHaveBeenCalledTimes(2)
  })
})

describe('useAnimal Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches single animal on mount with valid id', async () => {
    const getAnimalMock = vi.spyOn(apiService.default, 'getAnimal').mockResolvedValue(mockAnimal)

    const { result } = renderHook(() => useAnimal(1))

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(getAnimalMock).toHaveBeenCalledWith(1)
    expect(result.current.animal).toEqual(mockAnimal)
    expect(result.current.error).toBe(null)
  })

  it('does not fetch with null id', () => {
    const getAnimalMock = vi.spyOn(apiService.default, 'getAnimal')

    const { result } = renderHook(() => useAnimal(null))

    expect(result.current.loading).toBe(false)
    expect(result.current.animal).toBe(null)
    expect(getAnimalMock).not.toHaveBeenCalled()
  })

  it('handles fetch error for single animal', async () => {
    const error = new Error('Animal not found')
    vi.spyOn(apiService.default, 'getAnimal').mockRejectedValue(error)

    const { result } = renderHook(() => useAnimal(999))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.animal).toBe(null)
    expect(result.current.error).toBe('Animal not found')
  })

  it('refetches animal on demand', async () => {
    const getAnimalMock = vi.spyOn(apiService.default, 'getAnimal').mockResolvedValue(mockAnimal)

    const { result } = renderHook(() => useAnimal(1))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(getAnimalMock).toHaveBeenCalledTimes(1)

    await result.current.refetch()

    expect(getAnimalMock).toHaveBeenCalledTimes(2)
  })

  it('handles id change', async () => {
    const getAnimalMock = vi.spyOn(apiService.default, 'getAnimal').mockResolvedValue(mockAnimal)

    const { result, rerender } = renderHook(({ id }) => useAnimal(id), {
      initialProps: { id: 1 },
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(getAnimalMock).toHaveBeenCalledWith(1)

    rerender({ id: 2 })

    await waitFor(() => {
      expect(getAnimalMock).toHaveBeenCalledWith(2)
    })
  })
})

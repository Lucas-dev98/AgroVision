import { useState, useEffect, useCallback } from 'react'
import { Animal, PaginatedResponse } from '@types/index'
import apiService from '@services/api'

interface UseAnimalsReturn {
  animals: Animal[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

/**
 * Hook para buscar lista de animais da API
 * 
 * @returns {UseAnimalsReturn} animals, loading, error, refetch
 * 
 * @example
 * const { animals, loading, error } = useAnimals()
 */
export function useAnimals(): UseAnimalsReturn {
  const [animals, setAnimals] = useState<Animal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAnimals = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response: PaginatedResponse<Animal> = await apiService.getAnimals()
      setAnimals(response.items)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch animals'
      setError(message)
      setAnimals([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAnimals()
  }, [fetchAnimals])

  return {
    animals,
    loading,
    error,
    refetch: fetchAnimals,
  }
}

interface UseAnimalReturn {
  animal: Animal | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

/**
 * Hook para buscar um animal específico da API
 * 
 * @param {number} id - ID do animal
 * @returns {UseAnimalReturn} animal, loading, error, refetch
 * 
 * @example
 * const { animal, loading } = useAnimal(1)
 */
export function useAnimal(id: number | null): UseAnimalReturn {
  const [animal, setAnimal] = useState<Animal | null>(null)
  const [loading, setLoading] = useState(!!id)
  const [error, setError] = useState<string | null>(null)

  const fetchAnimal = useCallback(async () => {
    if (!id) {
      setAnimal(null)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await apiService.getAnimal(id)
      setAnimal(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch animal'
      setError(message)
      setAnimal(null)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    fetchAnimal()
  }, [fetchAnimal])

  return {
    animal,
    loading,
    error,
    refetch: fetchAnimal,
  }
}

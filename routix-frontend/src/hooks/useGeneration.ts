import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useGenerationStore } from '@/lib/store'
import { generationAPI } from '@/lib/api'
import { Generation, Algorithm, GenerationStats } from '@/types'

export function useGenerations() {
  const { activeGenerations, completedGenerations, setGenerations, addGeneration, updateGeneration } = useGenerationStore()
  const queryClient = useQueryClient()

  const generationsQuery = useQuery({
    queryKey: ['generations'],
    queryFn: () => generationAPI.getGenerations().then(res => res.data.generations),
    onSuccess: (data: Generation[]) => {
      setGenerations(data)
    },
  })

  const createGenerationMutation = useMutation({
    mutationFn: generationAPI.createGeneration,
    onSuccess: (data) => {
      const newGeneration = data.data
      addGeneration(newGeneration)
      queryClient.invalidateQueries({ queryKey: ['generations'] })
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })

  const cancelGenerationMutation = useMutation({
    mutationFn: generationAPI.cancelGeneration,
    onSuccess: (_, generationId) => {
      updateGeneration(generationId, { status: 'cancelled' })
      queryClient.invalidateQueries({ queryKey: ['generations'] })
    },
  })

  return {
    activeGenerations,
    completedGenerations,
    allGenerations: [...activeGenerations, ...completedGenerations],
    isLoading: generationsQuery.isLoading,
    error: generationsQuery.error,
    createGeneration: createGenerationMutation.mutate,
    cancelGeneration: cancelGenerationMutation.mutate,
    isCreating: createGenerationMutation.isPending,
    isCancelling: cancelGenerationMutation.isPending,
    refetch: generationsQuery.refetch,
  }
}

export function useGeneration(generationId: string | null) {
  const { updateGeneration } = useGenerationStore()
  const queryClient = useQueryClient()

  const generationQuery = useQuery({
    queryKey: ['generation', generationId],
    queryFn: () => generationId ? generationAPI.getGeneration(generationId).then(res => res.data) : null,
    enabled: !!generationId,
  })

  const statusQuery = useQuery({
    queryKey: ['generation-status', generationId],
    queryFn: () => generationId ? generationAPI.getGenerationStatus(generationId).then(res => res.data) : null,
    enabled: !!generationId,
    refetchInterval: (data) => {
      // Stop polling if generation is completed or failed
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false
      }
      return 2000 // Poll every 2 seconds
    },
    onSuccess: (data) => {
      if (data && generationId) {
        updateGeneration(generationId, {
          status: data.status,
          progress: data.progress,
          error_message: data.message
        })
      }
    },
  })

  return {
    generation: generationQuery.data,
    status: statusQuery.data,
    isLoading: generationQuery.isLoading,
    error: generationQuery.error,
    refetch: generationQuery.refetch,
  }
}

export function useAlgorithms() {
  const algorithmsQuery = useQuery({
    queryKey: ['algorithms'],
    queryFn: () => generationAPI.getAlgorithms().then(res => res.data),
  })

  return {
    algorithms: algorithmsQuery.data || [],
    isLoading: algorithmsQuery.isLoading,
    error: algorithmsQuery.error,
  }
}

export function useGenerationStats() {
  const statsQuery = useQuery({
    queryKey: ['generation-stats'],
    queryFn: () => generationAPI.getStats().then(res => res.data),
  })

  return {
    stats: statsQuery.data,
    isLoading: statsQuery.isLoading,
    error: statsQuery.error,
    refetch: statsQuery.refetch,
  }
}

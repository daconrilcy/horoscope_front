import { useAstrologers as useAstrologersApi } from '../api/astrologers'

/**
 * Hook for astrologers data (Story 55.3).
 * Centralizes fetching and state management for astrologers list.
 */
export function useAstrologers() {
  const { data, isPending, error } = useAstrologersApi()

  return {
    astrologers: data ?? [],
    isLoading: isPending,
    error,
  }
}

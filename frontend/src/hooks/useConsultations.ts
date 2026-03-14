import { useConsultation } from '../state/consultationStore'

/**
 * Hook for consultations history (Story 55.3).
 */
export function useConsultations() {
  const { state } = useConsultation()

  return {
    history: state.history,
    isLoading: false, // Since it's from local store for now
    error: null,
  }
}

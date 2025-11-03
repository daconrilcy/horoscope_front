import { useQuery } from '@tanstack/react-query';
import { horoscopeService } from '@/shared/api/horoscope.service';
import { NetworkError } from '@/shared/api/errors';

/**
 * Interface du résultat du hook useToday
 */
export interface UseTodayResult {
  /** Contenu du Today (free) */
  data: { content: string; generated_at?: string } | undefined;
  /** Indique si la query est en cours */
  isLoading: boolean;
  /** Indique s'il y a une erreur */
  isError: boolean;
  /** Erreur de la query */
  error: Error | null;
  /** Fonction pour refetch manuel */
  refetch: () => void;
}

/**
 * Hook React Query pour récupérer l'horoscope Today
 * Retry conditionnel : retry 0 si ApiError (4xx/5xx), retry 1 si NetworkError
 * staleTime: 300000 (5 min)
 */
export function useToday(chartId: string | null): UseTodayResult {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['horo', 'today', chartId],
    queryFn: async () => {
      if (!chartId) {
        throw new Error('Chart ID is required');
      }
      return await horoscopeService.getToday(chartId);
    },
    enabled: !!chartId,
    staleTime: 300000, // 5 min
    retry: (failureCount, error) => {
      // Retry 0 si ApiError (4xx/5xx), retry 1 si NetworkError
      if (error instanceof NetworkError) {
        return failureCount < 1;
      }
      return false;
    },
  });

  const safeRefetch = (): void => {
    void refetch();
  };

  return {
    data,
    isLoading,
    isError,
    error: error ?? null,
    refetch: safeRefetch,
  };
}

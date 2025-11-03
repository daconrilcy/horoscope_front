import { useQuery } from '@tanstack/react-query';
import { horoscopeService } from '@/shared/api/horoscope.service';
import { NetworkError } from '@/shared/api/errors';

/**
 * Interface du résultat du hook useTodayPremium
 */
export interface UseTodayPremiumResult {
  /** Contenu du Today Premium */
  data:
    | { content: string; premium_insights?: string; generated_at?: string }
    | undefined;
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
 * Hook React Query pour récupérer l'horoscope Today Premium
 * Retry conditionnel : retry 0 si ApiError (4xx/5xx), retry 1 si NetworkError
 * staleTime: 300000 (5 min)
 * Note : query déclenchée uniquement à l'intérieur de PaywallGate
 */
export function useTodayPremium(chartId: string | null): UseTodayPremiumResult {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['horo', 'today-premium', chartId],
    queryFn: async () => {
      if (!chartId) {
        throw new Error('Chart ID is required');
      }
      return await horoscopeService.getTodayPremium(chartId);
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

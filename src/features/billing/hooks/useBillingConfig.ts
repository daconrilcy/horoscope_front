import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import {
  billingConfigService,
  type BillingConfig,
} from '@/shared/api/billingConfig.service';

/**
 * Clé Query pour le cache React Query
 */
export const BILLING_CONFIG_QUERY_KEY = ['billingConfig'] as const;

/**
 * Options de la query React Query pour le billing config
 */
const queryOptions = {
  queryKey: BILLING_CONFIG_QUERY_KEY,
  queryFn: () => billingConfigService.getConfig(),
  staleTime: 5 * 60 * 1000, // 5 minutes (identique au cache service)
  refetchOnWindowFocus: import.meta.env.DEV ? ('always' as const) : false, // En dev, refetch au focus
  refetchOnMount: false, // Utiliser le cache si disponible
};

/**
 * Hook React Query pour récupérer la configuration billing
 * @returns Requête React Query avec la config billing
 */
export function useBillingConfig(): UseQueryResult<BillingConfig, Error> {
  return useQuery(queryOptions);
}

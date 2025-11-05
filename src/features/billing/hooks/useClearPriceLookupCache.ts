import { useMutation, useQueryClient, type UseMutationResult } from '@tanstack/react-query';
import { adminService, type ClearPriceLookupCacheResponse } from '@/shared/api/admin.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { BILLING_CONFIG_QUERY_KEY } from './useBillingConfig';
import { billingConfigService } from '@/shared/api/billingConfig.service';
import { eventBus } from '@/shared/api/eventBus';

/**
 * Hook React Query pour clear le cache price_lookup
 * @returns Mutation pour déclencher le clear cache
 */
export function useClearPriceLookupCache(): UseMutationResult<
  ClearPriceLookupCacheResponse,
  Error,
  void
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      return await adminService.clearPriceLookupCache();
    },
    onSuccess: (data) => {
      // Émettre l'événement pour l'observabilité
      eventBus.emit('admin:clear-price-lookup-cache', {
        cleared: data.cleared,
        timestamp: Date.now(),
      });

      // Invalider le cache React Query pour forcer le refetch
      void queryClient.invalidateQueries({
        queryKey: BILLING_CONFIG_QUERY_KEY,
      });

      // Clear aussi le cache du service billingConfigService
      billingConfigService.clearCache();

      // Afficher un toast de succès
      toast.success(
        data.message != null && data.message !== ''
          ? data.message
          : 'Cache price_lookup cleared successfully'
      );
    },
    onError: (error) => {
      if (error instanceof NetworkError) {
        toast.error('Service indisponible, réessayez.');
      } else if (error instanceof ApiError) {
        if (error.status === 401) {
          toast.error('Vous devez être connecté pour effectuer cette action.');
        } else if (error.status === 403) {
          toast.error('Vous n\'avez pas les permissions nécessaires.');
        } else {
          toast.error(
            error.message || 'Erreur lors du clear du cache price_lookup.'
          );
        }
      } else {
        toast.error('Une erreur inattendue est survenue.');
      }

      if (error instanceof ApiError && error.requestId !== undefined) {
        console.error('[ClearPriceLookupCache] request_id:', error.requestId);
      }
    },
  });
}

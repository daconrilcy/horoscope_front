import { useMutation } from '@tanstack/react-query';
import { adminService } from '@/shared/api/admin.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';

/**
 * Hook React Query pour vider le cache price_lookup
 * Dev-only, protection double-clic intégrée
 */
export function useClearPriceLookupCache(): {
  clearCache: () => Promise<void>;
  isPending: boolean;
  error: Error | null;
} {
  const { mutateAsync, isPending, error } = useMutation<void, Error>({
    mutationFn: async () => {
      return await adminService.clearPriceLookupCache();
    },
    onSuccess: () => {
      toast.success('Cache price_lookup vidé avec succès');
    },
    onError: (err) => {
      // Gestion erreurs réaliste
      if (err instanceof ApiError) {
        const message =
          err.message || 'Erreur lors du vidage du cache price_lookup.';
        toast.error(message);
      } else if (err instanceof NetworkError) {
        const message =
          err.reason === 'timeout' || err.reason === 'offline'
            ? 'Service indisponible, réessayez.'
            : 'Erreur réseau lors du vidage du cache.';
        toast.error(message);
      } else {
        toast.error('Une erreur inattendue est survenue.');
      }

      // Journalisation légère : log request_id si présent
      if (err instanceof ApiError && err.requestId !== undefined) {
        console.error('[Admin] request_id:', err.requestId);
      }
    },
  });

  /**
   * Fonction pour vider le cache avec protection double-clic
   */
  const clearCache = async (): Promise<void> => {
    // Protection double-clic : bloquer un second appel tant que isPending est true
    if (isPending) {
      return;
    }

    // Les erreurs sont déjà gérées dans onError
    await mutateAsync();
  };

  return {
    clearCache,
    isPending,
    error: error ?? null,
  };
}

import { useMutation } from '@tanstack/react-query';
import { billingService } from '@/shared/api/billing.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';

/**
 * Interface du résultat du hook usePortal
 */
export interface UsePortalResult {
  /** Fonction pour ouvrir le portal Stripe */
  openPortal: () => Promise<void>;
  /** Indique si une mutation est en cours */
  isPending: boolean;
  /** Erreur de la dernière mutation */
  error: Error | null;
}

/**
 * Hook React Query pour créer une session portal Stripe
 * Protection double-clic intégrée (bloque si isPending)
 * Gestion d'erreurs réaliste (401, NetworkError)
 */
export function usePortal(): UsePortalResult {
  const { mutateAsync, isPending, error } = useMutation<string, Error>({
    mutationFn: async () => {
      return await billingService.createPortalSession();
    },
    onSuccess: (portalUrl) => {
      // Redirection via window.location.assign (meilleur pour l'historique)
      window.location.assign(portalUrl);
    },
    onError: (err) => {
      // Gestion erreurs réaliste
      if (err instanceof ApiError) {
        // 401 → laisse le wrapper déclencher l'unauthorized (redir login via callback global)
        // Pas de traitement spécial ici
        if (err.status !== 401) {
          // Autres erreurs API (sauf 401 déjà gérée)
          const message =
            err.message || "Une erreur est survenue lors de l'accès au portal.";
          toast.error(message);
        }
      } else if (err instanceof NetworkError) {
        // NetworkError/timeout → toast clair
        const message =
          err.reason === 'timeout' || err.reason === 'offline'
            ? 'Service Billing indisponible, réessayez.'
            : "Erreur réseau lors de l'accès au portal.";
        toast.error(message);
      } else {
        // Erreur inconnue
        toast.error('Une erreur inattendue est survenue.');
      }

      // Journalisation légère : log request_id si présent (utile en support)
      if (err instanceof ApiError && err.requestId !== undefined) {
        console.error('[Portal] request_id:', err.requestId);
      }
    },
  });

  /**
   * Fonction pour ouvrir le portal avec protection double-clic
   */
  const openPortal = async (): Promise<void> => {
    // Protection double-clic : bloquer un second appel tant que isPending est true
    if (isPending) {
      return;
    }

    // Les erreurs sont déjà gérées dans onError
    await mutateAsync();
  };

  return {
    openPortal,
    isPending,
    error: error ?? null,
  };
}

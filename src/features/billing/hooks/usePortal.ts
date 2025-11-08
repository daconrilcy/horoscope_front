import { useMutation } from '@tanstack/react-query';
import { billingService } from '@/shared/api/billing.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { useBillingConfig } from './useBillingConfig';

/**
 * Interface du résultat du hook usePortal
 */
export interface UsePortalResult {
  /** Fonction pour ouvrir le portal Stripe */
  openPortal: (return_url?: string) => Promise<void>;
  /** Indique si une mutation est en cours */
  isPending: boolean;
  /** Erreur de la dernière mutation */
  error: Error | null;
}

/**
 * Vérifie si une erreur est liée à la whitelist du return_url
 */
function isWhitelistError(error: ApiError): boolean {
  // Erreurs 400/422 avec message contenant "whitelist", "return_url", "not allowed"
  if (error.status !== 400 && error.status !== 422) {
    return false;
  }

  const message = error.message.toLowerCase();
  const detailsMessage =
    error.details &&
    typeof error.details === 'object' &&
    'message' in error.details &&
    typeof error.details.message === 'string'
      ? error.details.message.toLowerCase()
      : '';

  return (
    message.includes('whitelist') ||
    message.includes('return_url') ||
    message.includes('not allowed') ||
    detailsMessage.includes('whitelist') ||
    detailsMessage.includes('return_url') ||
    detailsMessage.includes('not allowed')
  );
}

/**
 * Hook React Query pour créer une session portal Stripe
 * Protection double-clic intégrée (bloque si isPending)
 * Gestion d'erreurs réaliste (401, whitelist, NetworkError)
 * Utilise portal_return_url depuis billingConfig si disponible
 */
export function usePortal(): UsePortalResult {
  const { data: billingConfig } = useBillingConfig();

  const { mutateAsync, isPending, error } = useMutation<string, Error, string | undefined>({
    mutationFn: async (return_url?: string) => {
      return await billingService.createPortalSession(return_url);
    },
    onSuccess: (portalUrl) => {
      // Redirection via window.location.assign (meilleur pour l'historique)
      window.location.assign(portalUrl);
    },
    onError: (err, return_url) => {
      // Gestion erreurs réaliste
      if (err instanceof ApiError) {
        // 401 → laisse le wrapper déclencher l'unauthorized (redir login via callback global)
        if (err.status === 401) {
          return;
        }

        // Erreur de whitelist : réessayer sans return_url si on en avait fourni un
        if (isWhitelistError(err) && return_url != null && return_url !== '') {
          console.warn(
            '[Portal] return_url not whitelisted, retrying without return_url',
            return_url
          );
          // Réessayer sans return_url (fallback) - appel direct pour éviter récursion
          billingService
            .createPortalSession(undefined)
            .then((portalUrl) => {
              window.location.assign(portalUrl);
            })
            .catch((fallbackError) => {
              // Si le fallback échoue aussi, afficher l'erreur
              toast.error(
                "L'URL de retour n'est pas autorisée. Le portal s'ouvrira sans redirection automatique."
              );
              console.error('[Portal] Fallback failed:', fallbackError);
            });
          return;
        }

        // Autres erreurs API (sauf 401 et whitelist déjà gérées)
        const message =
          err.message || "Une erreur est survenue lors de l'accès au portal.";
        toast.error(message);
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
   * Utilise portal_return_url depuis billingConfig si disponible
   */
  const openPortal = async (return_url?: string): Promise<void> => {
    // Protection double-clic : bloquer un second appel tant que isPending est true
    if (isPending) {
      return;
    }

    // Utiliser portal_return_url depuis billingConfig si disponible et si return_url non fourni
    const finalReturnUrl =
      return_url ?? billingConfig?.portalReturnUrl ?? undefined;

    // Les erreurs sont déjà gérées dans onError (avec fallback pour whitelist)
    await mutateAsync(finalReturnUrl);
  };

  return {
    openPortal,
    isPending,
    error: error ?? null,
  };
}

import { useMutation } from '@tanstack/react-query';
import { billingService } from '@/shared/api/billing.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { useBillingConfig } from './useBillingConfig';

/**
 * Interface du résultat du hook usePortal
 */
export interface UsePortalResult {
  /** Fonction pour ouvrir le portal Stripe avec return_url optionnel */
  openPortal: (return_url?: string) => Promise<void>;
  /** Indique si une mutation est en cours */
  isPending: boolean;
  /** Erreur de la dernière mutation */
  error: Error | null;
}

/**
 * Détecte si une erreur est liée au whitelist
 */
function isWhitelistError(error: ApiError): boolean {
  // Erreur 400/403 avec message/code indiquant whitelist
  if (error.status === 400 || error.status === 403) {
    const message = error.message.toLowerCase();
    return (
      message.includes('whitelist') ||
      message.includes('not allowed') ||
      message.includes('not authorized') ||
      message.includes('unauthorized url')
    );
  }
  return false;
}

/**
 * Hook React Query pour créer une session portal Stripe
 * Protection double-clic intégrée (bloque si isPending)
 * Gestion d'erreurs réaliste (401, NetworkError, whitelist)
 * Support return_url optionnel avec fallback depuis billingConfig
 */
export function usePortal(): UsePortalResult {
  const { data: billingConfig } = useBillingConfig();

  const { mutateAsync, isPending, error } = useMutation<
    string,
    Error,
    string | undefined
  >({
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

        // Erreur whitelist : retry avec fallback si return_url était fourni
        if (isWhitelistError(err) && return_url != null && return_url !== '') {
          console.warn(
            '[Portal] return_url not whitelisted, retrying without return_url',
            return_url
          );
          // Relancer avec fallback (sans return_url ou avec portalReturnUrl de la config)
          const fallbackReturnUrl =
            billingConfig?.portalReturnUrl != null &&
            billingConfig.portalReturnUrl !== ''
              ? billingConfig.portalReturnUrl
              : undefined;
          // Appel direct pour éviter récursion dans mutationFn
          // Ne pas attendre pour éviter de bloquer le handler d'erreur
          void billingService
            .createPortalSession(fallbackReturnUrl)
            .then((portalUrl) => {
              window.location.assign(portalUrl);
            })
            .catch((fallbackError) => {
              toast.error(
                "L'URL de retour n'est pas autorisée. Le portal s'ouvrira sans redirection automatique."
              );
              console.error('[Portal] Fallback failed:', fallbackError);
            });
          // Ne pas propager l'erreur whitelist si on a un fallback
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
   * @param return_url URL de retour optionnelle (utilise portalReturnUrl de billingConfig si non fournie)
   */
  const openPortal = async (return_url?: string): Promise<void> => {
    // Protection double-clic : bloquer un second appel tant que isPending est true
    if (isPending) {
      return;
    }

    // Déterminer le return_url final : paramètre explicite > billingConfig > undefined
    const finalReturnUrl =
      return_url ??
      (billingConfig?.portalReturnUrl != null &&
      billingConfig.portalReturnUrl !== ''
        ? billingConfig.portalReturnUrl
        : undefined);

    // Les erreurs sont déjà gérées dans onError
    await mutateAsync(finalReturnUrl);
  };

  return {
    openPortal,
    isPending,
    error: error ?? null,
  };
}

import { useMutation } from '@tanstack/react-query';
import { v4 as uuidv4 } from 'uuid';
import { billingService } from '@/shared/api/billing.service';
import { assertValidPlan, type BillingPlan } from '@/shared/config/plans';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';

/**
 * Interface du résultat du hook useCheckout
 */
export interface UseCheckoutResult {
  /** Fonction pour démarrer le checkout */
  startCheckout: (plan: BillingPlan) => Promise<void>;
  /** Indique si une mutation est en cours */
  isPending: boolean;
  /** Erreur de la dernière mutation */
  error: Error | null;
}

/**
 * Hook React Query pour créer une session checkout Stripe
 * Protection double-clic intégrée (bloque si isPending)
 * Gestion d'erreurs réaliste (401, 409/400, NetworkError)
 */
export function useCheckout(): UseCheckoutResult {
  const { mutateAsync, isPending, error } = useMutation<
    string,
    Error,
    { plan: BillingPlan; idemKey: string }
  >({
    mutationFn: async ({ plan, idemKey }) => {
      return await billingService.createCheckoutSession(plan, idemKey);
    },
    onSuccess: (checkoutUrl) => {
      // Redirection via window.location.assign (meilleur pour l'historique)
      window.location.assign(checkoutUrl);
    },
    onError: (err) => {
      // Gestion erreurs réaliste
      if (err instanceof ApiError) {
        // 401 → laisse le wrapper déclencher l'unauthorized (redir login via callback global)
        // Pas de traitement spécial ici

        // 409/400 "déjà abonné" → propose le Portal
        if (
          err.status === 409 ||
          (err.status === 400 &&
            typeof err.details === 'object' &&
            err.details !== null &&
            'message' in err.details &&
            typeof (err.details as { message?: string }).message === 'string' &&
            ((err.details as { message: string }).message.includes(
              'abonnement'
            ) ||
              (err.details as { message: string }).message.includes('déjà')))
        ) {
          toast.error(
            "Vous avez déjà un abonnement actif. Utilisez le bouton 'Gérer mon abonnement'."
          );
        } else if (err.status !== 401) {
          // Autres erreurs API (sauf 401 déjà gérée)
          const message =
            err.message || 'Une erreur est survenue lors du checkout.';
          toast.error(message);
        }
      } else if (err instanceof NetworkError) {
        // NetworkError/timeout → toast clair
        const message =
          err.reason === 'timeout' || err.reason === 'offline'
            ? 'Service Billing indisponible, réessayez.'
            : 'Erreur réseau lors du checkout.';
        toast.error(message);
      } else {
        // Erreur inconnue
        toast.error('Une erreur inattendue est survenue.');
      }

      // Journalisation légère : log request_id si présent (utile en support)
      if (err instanceof ApiError && err.requestId !== undefined) {
        console.error('[Checkout] request_id:', err.requestId);
      }
    },
  });

  /**
   * Fonction pour démarrer le checkout avec protection double-clic
   */
  const startCheckout = async (plan: BillingPlan): Promise<void> => {
    // Protection double-clic : bloquer un second appel tant que isPending est true
    if (isPending) {
      return;
    }

    // Validation plan en dev
    assertValidPlan(plan);

    // Génération Idempotency-Key au clic (UUID v4)
    const idemKey = uuidv4();

    // Les erreurs sont déjà gérées dans onError
    await mutateAsync({ plan, idemKey });
  };

  return {
    startCheckout,
    isPending,
    error: error ?? null,
  };
}

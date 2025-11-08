import { useMutation } from '@tanstack/react-query';
import { v4 as uuidv4 } from 'uuid';
import {
  billingService,
  type CheckoutSessionPayload,
} from '@/shared/api/billing.service';
import { assertValidPlan, type BillingPlan } from '@/shared/config/plans';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';

export interface UseCheckoutResult {
  startCheckout: (
    plan: BillingPlan,
    options?: Partial<CheckoutSessionPayload>
  ) => Promise<void>;
  isPending: boolean;
  error: Error | null;
}

export function useCheckout(): UseCheckoutResult {
  const { mutateAsync, isPending, error } = useMutation<
    string,
    Error,
    {
      plan: BillingPlan;
      idemKey: string;
      options?: Partial<CheckoutSessionPayload>;
    }
  >({
    mutationFn: async ({ plan, idemKey, options }) => {
      return await billingService.createCheckoutSession(plan, idemKey, options);
    },
    onSuccess: (checkoutUrl) => {
      window.location.assign(checkoutUrl);
    },
    onError: (err) => {
      if (err instanceof ApiError) {
        if (
          err.status === 409 ||
          (err.status === 400 &&
            typeof err.details === 'object' &&
            err.details !== null &&
            'message' in err.details &&
            typeof (err.details as { message?: string }).message === 'string' &&
            ((err.details as { message: string }).message.includes('abonnement') ||
              (err.details as { message: string }).message.includes('déjà')))
        ) {
          toast.error(
            "Vous avez déjà un abonnement actif. Utilisez le bouton 'Gérer mon abonnement'."
          );
        } else if (err.status !== 401) {
          const message =
            err.message || 'Une erreur est survenue lors du checkout.';
          toast.error(message);
        }
      } else if (err instanceof NetworkError) {
        const message =
          err.reason === 'timeout' || err.reason === 'offline'
            ? 'Service Billing indisponible, réessayez.'
            : 'Erreur réseau lors du checkout.';
        toast.error(message);
      } else {
        toast.error('Une erreur inattendue est survenue.');
      }

      if (err instanceof ApiError && err.requestId !== undefined) {
        console.error('[Checkout] request_id:', err.requestId);
      }
    },
  });

  const startCheckout = async (
    plan: BillingPlan,
    options?: Partial<CheckoutSessionPayload>
  ): Promise<void> => {
    if (isPending) {
      return;
    }

    assertValidPlan(plan);

    const idemKey = uuidv4();

    await mutateAsync({ plan, idemKey, options });
  };

  return {
    startCheckout,
    isPending,
    error: error ?? null,
  };
}

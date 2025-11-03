import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCheckout } from './useCheckout';
import { billingService } from '@/shared/api/billing.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { PLANS } from '@/shared/config/plans';
import { toast } from '@/app/AppProviders';
import React from 'react';

// Mock billingService
vi.mock('@/shared/api/billing.service', () => ({
  billingService: {
    createCheckoutSession: vi.fn(),
  },
}));

// Mock toast
vi.mock('@/app/AppProviders', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

// Mock window.location.assign
const mockAssign = vi.fn();
Object.defineProperty(window, 'location', {
  value: {
    assign: mockAssign,
  },
  writable: true,
});

describe('useCheckout', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
        mutations: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
    mockAssign.mockClear();
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('devrait appeler createCheckoutSession et rediriger avec window.location.assign', async () => {
    const checkoutUrl = 'https://checkout.stripe.com/pay/cs_test_123';

    (
      billingService.createCheckoutSession as ReturnType<typeof vi.fn>
    ).mockResolvedValue(checkoutUrl);

    const { result } = renderHook(() => useCheckout(), { wrapper });

    await result.current.startCheckout(PLANS.PLUS);

    await waitFor(() => {
      expect(mockAssign).toHaveBeenCalledWith(checkoutUrl);
    });

    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(billingService.createCheckoutSession).toHaveBeenCalledWith(
      PLANS.PLUS,
      expect.any(String)
    );
  });

  it('devrait générer une Idempotency-Key différente à chaque appel', async () => {
    const checkoutUrl = 'https://checkout.stripe.com/pay/cs_test_123';

    const mockCreateCheckoutSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createCheckoutSession
    );
    mockCreateCheckoutSession.mockResolvedValue(checkoutUrl);

    const { result } = renderHook(() => useCheckout(), { wrapper });

    // Premier appel
    await result.current.startCheckout(PLANS.PLUS);

    const firstCall = mockCreateCheckoutSession.mock.calls[0];

    const firstKey = firstCall[1];

    // Deuxième appel
    mockCreateCheckoutSession.mockClear();
    await result.current.startCheckout(PLANS.PRO);

    const secondCall = mockCreateCheckoutSession.mock.calls[0];

    const secondKey = secondCall[1];

    // Les clés doivent être différentes (UUID v4)
    expect(firstKey).toBeDefined();
    expect(secondKey).toBeDefined();
    expect(firstKey).not.toBe(secondKey);
  });

  it('devrait bloquer les appels supplémentaires si isPending (double-clic)', async () => {
    let resolvePromise: (value: string) => void;
    const checkoutUrl = 'https://checkout.stripe.com/pay/cs_test_123';

    const mockCreateCheckoutSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createCheckoutSession
    );
    mockCreateCheckoutSession.mockImplementation(
      () =>
        new Promise<string>((resolve) => {
          resolvePromise = resolve;
        })
    );

    const { result } = renderHook(() => useCheckout(), { wrapper });

    // Premier appel (en cours)
    void result.current.startCheckout(PLANS.PLUS);

    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Deuxième appel (doit être ignoré)
    await result.current.startCheckout(PLANS.PLUS);

    // Vérifier qu'un seul appel a été fait
    expect(mockCreateCheckoutSession).toHaveBeenCalledTimes(1);

    // Résoudre le premier appel
    resolvePromise!(checkoutUrl);

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });
  });

  it('devrait afficher toast et ne pas rediriger sur NetworkError', async () => {
    const networkError = new NetworkError('timeout', 'Request timeout');

    (
      billingService.createCheckoutSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(networkError);

    const { result } = renderHook(() => useCheckout(), { wrapper });

    await expect(result.current.startCheckout(PLANS.PLUS)).rejects.toThrow();

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Service Billing indisponible, réessayez.'
      );
    });

    // Pas de redirection
    expect(mockAssign).not.toHaveBeenCalled();
  });

  it('devrait ne pas rediriger sur 401 (laisse wrapper gérer)', async () => {
    const apiError = new ApiError('Unauthorized', 401);

    (
      billingService.createCheckoutSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(apiError);

    const { result } = renderHook(() => useCheckout(), { wrapper });

    await expect(result.current.startCheckout(PLANS.PLUS)).rejects.toThrow();

    // Pas de toast pour 401 (géré par wrapper)
    expect(toast.error).not.toHaveBeenCalled();

    // Pas de redirection
    expect(mockAssign).not.toHaveBeenCalled();
  });

  it('devrait afficher toast pour 409/400 "déjà abonné"', async () => {
    const apiError = new ApiError(
      'Already subscribed',
      409,
      undefined,
      undefined,
      {
        message: 'Vous avez déjà un abonnement actif',
      }
    );

    (
      billingService.createCheckoutSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(apiError);

    const { result } = renderHook(() => useCheckout(), { wrapper });

    await expect(result.current.startCheckout(PLANS.PLUS)).rejects.toThrow();

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        "Vous avez déjà un abonnement actif. Utilisez le bouton 'Gérer mon abonnement'."
      );
    });
  });

  it('devrait afficher toast pour autres erreurs API (sauf 401)', async () => {
    const apiError = new ApiError('Forbidden', 403);

    (
      billingService.createCheckoutSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(apiError);

    const { result } = renderHook(() => useCheckout(), { wrapper });

    await expect(result.current.startCheckout(PLANS.PLUS)).rejects.toThrow();

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Forbidden');
    });
  });

  it('devrait retourner isPending: true pendant la mutation', async () => {
    let resolvePromise: (value: string) => void;
    const checkoutUrl = 'https://checkout.stripe.com/pay/cs_test_123';

    (
      billingService.createCheckoutSession as ReturnType<typeof vi.fn>
    ).mockImplementation(
      () =>
        new Promise<string>((resolve) => {
          resolvePromise = resolve;
        })
    );

    const { result } = renderHook(() => useCheckout(), { wrapper });

    // Démarrer la mutation
    void result.current.startCheckout(PLANS.PLUS);

    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Résoudre
    resolvePromise!(checkoutUrl);

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });
  });

  it('devrait retourner error après échec', async () => {
    const apiError = new ApiError('Bad Request', 400);

    (
      billingService.createCheckoutSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(apiError);

    const { result } = renderHook(() => useCheckout(), { wrapper });

    await expect(result.current.startCheckout(PLANS.PLUS)).rejects.toThrow();

    await waitFor(() => {
      expect(result.current.error).toBe(apiError);
    });
  });
});

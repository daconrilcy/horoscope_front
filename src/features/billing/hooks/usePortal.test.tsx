import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePortal } from './usePortal';
import { billingService } from '@/shared/api/billing.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { useBillingConfig } from './useBillingConfig';
import React from 'react';

// Mock billingService
vi.mock('@/shared/api/billing.service', () => ({
  billingService: {
    createPortalSession: vi.fn(),
  },
}));

// Mock useBillingConfig
vi.mock('./useBillingConfig', () => ({
  useBillingConfig: vi.fn(),
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

describe('usePortal', () => {
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

    // Mock useBillingConfig par défaut (pas de config)
    vi.mocked(useBillingConfig).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useBillingConfig>);
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('devrait appeler createPortalSession et rediriger avec window.location.assign', async () => {
    const portalUrl = 'https://billing.stripe.com/p/session_123';

    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );
    mockCreatePortalSession.mockResolvedValue(portalUrl);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await result.current.openPortal();

    await waitFor(() => {
      expect(mockAssign).toHaveBeenCalledWith(portalUrl);
    });

    expect(mockCreatePortalSession).toHaveBeenCalledTimes(1);
  });

  it('devrait bloquer les appels supplémentaires si isPending (double-clic)', async () => {
    let resolvePromise: (value: string) => void;
    const portalUrl = 'https://billing.stripe.com/p/session_123';

    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );
    mockCreatePortalSession.mockImplementation(
      () =>
        new Promise<string>((resolve) => {
          resolvePromise = resolve;
        })
    );

    const { result } = renderHook(() => usePortal(), { wrapper });

    // Premier appel (en cours)
    void result.current.openPortal();

    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Deuxième appel (doit être ignoré)
    await result.current.openPortal();

    // Vérifier qu'un seul appel a été fait
    expect(mockCreatePortalSession).toHaveBeenCalledTimes(1);

    // Résoudre le premier appel
    resolvePromise!(portalUrl);

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });
  });

  it('devrait afficher toast et ne pas rediriger sur NetworkError', async () => {
    const networkError = new NetworkError('offline', 'Network error');

    (
      billingService.createPortalSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(networkError);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await expect(result.current.openPortal()).rejects.toThrow();

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
      billingService.createPortalSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(apiError);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await expect(result.current.openPortal()).rejects.toThrow();

    // Pas de toast pour 401 (géré par wrapper)
    expect(toast.error).not.toHaveBeenCalled();

    // Pas de redirection
    expect(mockAssign).not.toHaveBeenCalled();
  });

  it('devrait afficher toast pour autres erreurs API (sauf 401)', async () => {
    const apiError = new ApiError('Forbidden', 403);

    (
      billingService.createPortalSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(apiError);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await expect(result.current.openPortal()).rejects.toThrow();

    await waitFor(() => {
      // Le code utilise err.message si disponible, sinon le message par défaut
      expect(toast.error).toHaveBeenCalledWith('Forbidden');
    });
  });

  it('devrait retourner isPending: true pendant la mutation', async () => {
    let resolvePromise: (value: string) => void;
    const portalUrl = 'https://billing.stripe.com/p/session_123';

    (
      billingService.createPortalSession as ReturnType<typeof vi.fn>
    ).mockImplementation(
      () =>
        new Promise<string>((resolve) => {
          resolvePromise = resolve;
        })
    );

    const { result } = renderHook(() => usePortal(), { wrapper });

    // Démarrer la mutation
    void result.current.openPortal();

    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Résoudre
    resolvePromise!(portalUrl);

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });
  });

  it('devrait retourner error après échec', async () => {
    const apiError = new ApiError('Bad Request', 400);

    (
      billingService.createPortalSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(apiError);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await expect(result.current.openPortal()).rejects.toThrow();

    await waitFor(() => {
      expect(result.current.error).toBe(apiError);
    });
  });

  it('devrait utiliser portal_return_url depuis billingConfig si disponible', async () => {
    const portalUrl = 'https://billing.stripe.com/p/session_123';
    const configReturnUrl = 'https://example.com/app/account';

    vi.mocked(useBillingConfig).mockReturnValue({
      data: {
        portalReturnUrl: configReturnUrl,
      } as ReturnType<typeof useBillingConfig>['data'],
      isLoading: false,
      error: null,
    } as ReturnType<typeof useBillingConfig>);

    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );
    mockCreatePortalSession.mockResolvedValue(portalUrl);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await result.current.openPortal();

    await waitFor(() => {
      expect(mockCreatePortalSession).toHaveBeenCalledWith(configReturnUrl);
      expect(mockAssign).toHaveBeenCalledWith(portalUrl);
    });
  });

  it('devrait utiliser return_url explicite plutôt que billingConfig', async () => {
    const portalUrl = 'https://billing.stripe.com/p/session_123';
    const configReturnUrl = 'https://example.com/app/account';
    const explicitReturnUrl = 'https://example.com/custom';

    vi.mocked(useBillingConfig).mockReturnValue({
      data: {
        portalReturnUrl: configReturnUrl,
      } as ReturnType<typeof useBillingConfig>['data'],
      isLoading: false,
      error: null,
    } as ReturnType<typeof useBillingConfig>);

    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );
    mockCreatePortalSession.mockResolvedValue(portalUrl);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await result.current.openPortal(explicitReturnUrl);

    await waitFor(() => {
      expect(mockCreatePortalSession).toHaveBeenCalledWith(explicitReturnUrl);
      expect(mockCreatePortalSession).not.toHaveBeenCalledWith(configReturnUrl);
    });
  });

  it('devrait réessayer sans return_url en cas d\'erreur de whitelist', async () => {
    const portalUrl = 'https://billing.stripe.com/p/session_123';
    const whitelistError = new ApiError('return_url not whitelisted', 400, undefined, undefined, {
      message: 'return_url not whitelisted',
    });

    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );

    // Premier appel avec return_url échoue (whitelist)
    mockCreatePortalSession.mockRejectedValueOnce(whitelistError);
    // Deuxième appel sans return_url réussit (fallback)
    mockCreatePortalSession.mockResolvedValueOnce(portalUrl);

    const { result } = renderHook(() => usePortal(), { wrapper });

    // Le premier appel échoue mais le fallback s'exécute en arrière-plan
    await expect(result.current.openPortal('https://invalid-url.com/return')).rejects.toThrow();

    // Attendre que le fallback se termine
    await waitFor(
      () => {
        // Doit appeler deux fois : une fois avec return_url, une fois sans
        expect(mockCreatePortalSession).toHaveBeenCalledTimes(2);
        expect(mockCreatePortalSession).toHaveBeenNthCalledWith(
          1,
          'https://invalid-url.com/return'
        );
        expect(mockCreatePortalSession).toHaveBeenNthCalledWith(2, undefined);
        // Doit rediriger avec le portalUrl du fallback
        expect(mockAssign).toHaveBeenCalledWith(portalUrl);
      },
      { timeout: 2000 }
    );
  });

  it('devrait afficher un toast si le fallback échoue aussi', async () => {
    const whitelistError = new ApiError('return_url not whitelisted', 400, undefined, undefined, {
      message: 'return_url not whitelisted',
    });
    const fallbackError = new ApiError('Server Error', 500);

    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );

    // Les deux appels échouent
    mockCreatePortalSession.mockRejectedValueOnce(whitelistError);
    mockCreatePortalSession.mockRejectedValueOnce(fallbackError);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await expect(result.current.openPortal('https://invalid-url.com/return')).rejects.toThrow();

    await waitFor(
      () => {
        expect(mockCreatePortalSession).toHaveBeenCalledTimes(2);
        expect(toast.error).toHaveBeenCalledWith(
          "L'URL de retour n'est pas autorisée. Le portal s'ouvrira sans redirection automatique."
        );
      },
      { timeout: 2000 }
    );
  });
});

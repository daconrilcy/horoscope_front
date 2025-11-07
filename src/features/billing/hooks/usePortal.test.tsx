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
    } as never);
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

  it('devrait utiliser portalReturnUrl depuis billingConfig si return_url non fourni', async () => {
    const portalUrl = 'https://billing.stripe.com/p/session_123';
    const configReturnUrl = 'https://example.com/app/account';

    vi.mocked(useBillingConfig).mockReturnValue({
      data: {
        portalReturnUrl: configReturnUrl,
      },
      isLoading: false,
      error: null,
    } as never);

    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );
    mockCreatePortalSession.mockResolvedValue(portalUrl);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await result.current.openPortal();

    await waitFor(() => {
      expect(mockCreatePortalSession).toHaveBeenCalledWith(configReturnUrl);
    });
  });

  it('devrait utiliser return_url explicite même si billingConfig existe', async () => {
    const portalUrl = 'https://billing.stripe.com/p/session_123';
    const explicitReturnUrl = 'https://example.com/custom-return';
    const configReturnUrl = 'https://example.com/app/account';

    vi.mocked(useBillingConfig).mockReturnValue({
      data: {
        portalReturnUrl: configReturnUrl,
      },
      isLoading: false,
      error: null,
    } as never);

    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );
    mockCreatePortalSession.mockResolvedValue(portalUrl);

    const { result } = renderHook(() => usePortal(), { wrapper });

    await result.current.openPortal(explicitReturnUrl);

    await waitFor(() => {
      expect(mockCreatePortalSession).toHaveBeenCalledWith(explicitReturnUrl);
    });
  });

  it("devrait réessayer sans return_url en cas d'erreur de whitelist", async () => {
    const portalUrl = 'https://billing.stripe.com/p/session_123';
    const customReturnUrl = 'https://not-whitelisted.com/return';

    const whitelistError = new ApiError('return_url not whitelisted', 400);
    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );

    // Premier appel avec return_url → erreur whitelist
    mockCreatePortalSession.mockRejectedValueOnce(whitelistError);
    // Deuxième appel sans return_url → succès (fallback direct depuis onError)
    mockCreatePortalSession.mockResolvedValueOnce(portalUrl);

    const { result } = renderHook(() => usePortal(), { wrapper });

    // Le premier appel échoue, mais le fallback est géré dans onError (ne rejette pas)
    void result.current.openPortal(customReturnUrl);

    // Attendre que le fallback soit appelé (appel direct depuis onError)
    await waitFor(
      () => {
        expect(mockCreatePortalSession).toHaveBeenCalledTimes(2);
        // Premier appel avec return_url custom (via mutateAsync)
        expect(mockCreatePortalSession).toHaveBeenNthCalledWith(
          1,
          customReturnUrl
        );
        // Deuxième appel sans return_url (fallback direct depuis onError)
        expect(mockCreatePortalSession).toHaveBeenNthCalledWith(2, undefined);
      },
      { timeout: 3000 }
    );

    // Vérifier que la redirection a eu lieu après le fallback
    await waitFor(() => {
      expect(mockAssign).toHaveBeenCalledWith(portalUrl);
    });
  });

  it("devrait utiliser portalReturnUrl de config comme fallback en cas d'erreur whitelist", async () => {
    const portalUrl = 'https://billing.stripe.com/p/session_123';
    const customReturnUrl = 'https://not-whitelisted.com/return';
    const configReturnUrl = 'https://example.com/app/account';

    vi.mocked(useBillingConfig).mockReturnValue({
      data: {
        portalReturnUrl: configReturnUrl,
      },
      isLoading: false,
      error: null,
    } as never);

    const whitelistError = new ApiError('return_url not whitelisted', 400);
    const mockCreatePortalSession = vi.mocked(
      // eslint-disable-next-line @typescript-eslint/unbound-method
      billingService.createPortalSession
    );

    // Premier appel avec return_url custom → erreur whitelist
    mockCreatePortalSession.mockRejectedValueOnce(whitelistError);
    // Deuxième appel avec portalReturnUrl de config → succès (fallback direct)
    mockCreatePortalSession.mockResolvedValueOnce(portalUrl);

    const { result } = renderHook(() => usePortal(), { wrapper });

    // Le premier appel échoue, mais le fallback est géré dans onError (ne rejette pas)
    void result.current.openPortal(customReturnUrl);

    // Attendre que le fallback soit appelé avec configReturnUrl (appel direct depuis onError)
    await waitFor(
      () => {
        expect(mockCreatePortalSession).toHaveBeenCalledTimes(2);
        expect(mockCreatePortalSession).toHaveBeenNthCalledWith(
          2,
          configReturnUrl
        );
      },
      { timeout: 3000 }
    );

    // Vérifier que la redirection a eu lieu après le fallback
    await waitFor(() => {
      expect(mockAssign).toHaveBeenCalledWith(portalUrl);
    });
  });
});

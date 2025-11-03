import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { useDeleteAccount } from './useDeleteAccount';
import { accountService } from '@/shared/api/account.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { useAuthStore } from '@/stores/authStore';
import { useHoroscopeStore } from '@/stores/horoscopeStore';
import { usePaywallStore } from '@/stores/paywallStore';
import React from 'react';

// Mock accountService
vi.mock('@/shared/api/account.service', () => ({
  accountService: {
    deleteAccount: vi.fn(),
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

// Mock stores
vi.mock('@/stores/authStore', () => ({
  useAuthStore: {
    getState: vi.fn(() => ({
      logout: vi.fn(),
    })),
  },
}));

vi.mock('@/stores/chatStore', () => ({
  useChatStore: {
    getState: vi.fn(() => ({
      byChart: {},
    })),
  },
}));

vi.mock('@/stores/horoscopeStore', () => ({
  useHoroscopeStore: {
    getState: vi.fn(() => ({
      clearCharts: vi.fn(),
    })),
  },
}));

vi.mock('@/stores/paywallStore', () => ({
  usePaywallStore: {
    getState: vi.fn(() => ({
      hidePaywall: vi.fn(),
    })),
  },
}));

// Mock localStorage helpers
vi.mock('@/shared/auth/chatHistory', () => ({
  clearChatHistory: vi.fn(),
}));

vi.mock('@/shared/auth/charts', () => ({
  clearPersistedCharts: vi.fn(),
}));

vi.mock('@/shared/auth/token', () => ({
  clearPersistedToken: vi.fn(),
}));

// Mock window.location.assign
const mockAssign = vi.fn();
Object.defineProperty(window, 'location', {
  value: {
    assign: mockAssign,
  },
  writable: true,
});

describe('useDeleteAccount', () => {
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
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </MemoryRouter>
  );

  it('devrait appeler deleteAccount, purger les stores et rediriger', async () => {
    (
      accountService.deleteAccount as ReturnType<typeof vi.fn>
    ).mockResolvedValue(undefined);

    const mockLogout = vi.fn();
     
    (useAuthStore.getState as ReturnType<typeof vi.fn>).mockReturnValue({
      logout: mockLogout,
    });

    const mockClearCharts = vi.fn();
     
    (useHoroscopeStore.getState as ReturnType<typeof vi.fn>).mockReturnValue({
      clearCharts: mockClearCharts,
    });

    const mockHidePaywall = vi.fn();
    (usePaywallStore.getState as ReturnType<typeof vi.fn>).mockReturnValue({
      hidePaywall: mockHidePaywall,
    });

    const { result } = renderHook(() => useDeleteAccount(), { wrapper });

    await result.current.deleteAccount();

    await waitFor(() => {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      expect(accountService.deleteAccount).toHaveBeenCalled();
      expect(mockLogout).toHaveBeenCalledWith(queryClient);
      // Vérifier que le cache est vidé
       
      const queryCache = queryClient.getQueryCache();
       
      expect(queryCache.getAll().length).toBe(0); // Cache cleared
      expect(mockClearCharts).toHaveBeenCalled();
      expect(mockHidePaywall).toHaveBeenCalled();
      expect(toast.success).toHaveBeenCalledWith(
        'Compte supprimé avec succès'
      );
      expect(mockAssign).toHaveBeenCalledWith('/');
    });
  });

  it('devrait bloquer double-clic pendant la mutation', async () => {
    let resolvePromise: () => void;
    const promise = new Promise<void>((resolve) => {
      resolvePromise = resolve;
    });

    (
      accountService.deleteAccount as ReturnType<typeof vi.fn>
    ).mockReturnValue(promise);

    const { result } = renderHook(() => useDeleteAccount(), { wrapper });

    // Premier appel
    void result.current.deleteAccount();

    // Attendre que isPending soit true
    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Deuxième appel (doit être bloqué)
    await result.current.deleteAccount();

    // Vérifier que deleteAccount n'a été appelé qu'une fois
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(accountService.deleteAccount).toHaveBeenCalledTimes(1);

    // Résoudre la promesse
    resolvePromise!();

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });
  });

  it('devrait gérer ApiError 401 (pas de toast, laisser wrapper gérer)', async () => {
    const mockError = new ApiError('Unauthorized', 401, undefined, undefined);

    (
      accountService.deleteAccount as ReturnType<typeof vi.fn>
    ).mockRejectedValue(mockError);

    const { result } = renderHook(() => useDeleteAccount(), { wrapper });

    try {
      await result.current.deleteAccount();
    } catch {
      // Ignorer l'erreur rejetée
    }

    await waitFor(() => {
      expect(toast.error).not.toHaveBeenCalled();
      expect(toast.success).not.toHaveBeenCalled();
      expect(mockAssign).not.toHaveBeenCalled();
      expect(result.current.error).toBeInstanceOf(ApiError);
    });
  });

  it('devrait gérer ApiError 409 avec toast métier spécifique (pas de logout)', async () => {
    const mockError = new ApiError(
      'Suppression impossible pour le moment',
      409,
      'conflict',
      'req-123'
    );

    (
      accountService.deleteAccount as ReturnType<typeof vi.fn>
    ).mockRejectedValue(mockError);

    const { result } = renderHook(() => useDeleteAccount(), { wrapper });

    try {
      await result.current.deleteAccount();
    } catch {
      // Ignorer l'erreur rejetée
    }

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        expect.stringContaining('Suppression impossible')
      );
      expect(mockAssign).not.toHaveBeenCalled();
      expect(result.current.error).toBeInstanceOf(ApiError);
    });
  });

  it('devrait gérer ApiError 500 avec toast spécifique', async () => {
    const mockError = new ApiError(
      'Internal Server Error',
      500,
      undefined,
      'req-123'
    );

    (
      accountService.deleteAccount as ReturnType<typeof vi.fn>
    ).mockRejectedValue(mockError);

    const { result } = renderHook(() => useDeleteAccount(), { wrapper });

    try {
      await result.current.deleteAccount();
    } catch {
      // Ignorer l'erreur rejetée
    }

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Erreur serveur lors de la suppression'
      );
      expect(mockAssign).not.toHaveBeenCalled();
      expect(result.current.error).toBeInstanceOf(ApiError);
    });
  });

  it('devrait gérer NetworkError timeout avec toast spécifique', async () => {
    const mockError = new NetworkError('timeout', 'Request timeout');

    (
      accountService.deleteAccount as ReturnType<typeof vi.fn>
    ).mockRejectedValue(mockError);

    const { result } = renderHook(() => useDeleteAccount(), { wrapper });

    try {
      await result.current.deleteAccount();
    } catch {
      // Ignorer l'erreur rejetée
    }

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Service indisponible, réessayez.'
      );
      expect(mockAssign).not.toHaveBeenCalled();
      expect(result.current.error).toBeInstanceOf(NetworkError);
    });
  });

  it('devrait rediriger même si la purge échoue partiellement', async () => {
    (
      accountService.deleteAccount as ReturnType<typeof vi.fn>
    ).mockResolvedValue(undefined);

    const mockLogout = vi.fn(() => {
      throw new Error('Erreur purge');
    });
    (useAuthStore.getState as ReturnType<typeof vi.fn>).mockReturnValue({
      logout: mockLogout,
    });

    const { result } = renderHook(() => useDeleteAccount(), { wrapper });

    await result.current.deleteAccount();

    await waitFor(() => {
      // Même si la purge échoue, la redirection doit se faire
      expect(mockAssign).toHaveBeenCalledWith('/');
    });
  });
});

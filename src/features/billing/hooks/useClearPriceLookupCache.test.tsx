import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useClearPriceLookupCache } from './useClearPriceLookupCache';
import { adminService } from '@/shared/api/admin.service';
import { billingConfigService } from '@/shared/api/billingConfig.service';
import { eventBus } from '@/shared/api/eventBus';
import { toast } from '@/app/AppProviders';
import React from 'react';

// Mock dependencies
vi.mock('@/shared/api/admin.service', () => ({
  adminService: {
    clearPriceLookupCache: vi.fn(),
  },
}));

vi.mock('@/shared/api/billingConfig.service', () => ({
  billingConfigService: {
    clearCache: vi.fn(),
  },
}));

vi.mock('@/shared/api/eventBus', () => ({
  eventBus: {
    emit: vi.fn(),
  },
}));

vi.mock('@/app/AppProviders', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('useClearPriceLookupCache', () => {
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
  });

  const wrapper = ({ children }: { children: React.ReactNode }): JSX.Element => {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };

  it('devrait clear le cache avec succès', async () => {
    const mockResponse = {
      cleared: true,
      message: 'Cache cleared successfully',
    };
    // eslint-disable-next-line @typescript-eslint/unbound-method
    vi.mocked(adminService.clearPriceLookupCache).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => useClearPriceLookupCache(), {
      wrapper,
    });

    result.current.mutate();

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(adminService.clearPriceLookupCache).toHaveBeenCalledTimes(1);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(billingConfigService.clearCache).toHaveBeenCalledTimes(1);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(eventBus.emit).toHaveBeenCalledWith(
      'admin:clear-price-lookup-cache',
      expect.objectContaining({
        cleared: true,
      })
    );
    expect(toast.success).toHaveBeenCalledWith('Cache cleared successfully');
  });

  it('devrait afficher un toast de succès avec message par défaut', async () => {
    const mockResponse = {
      cleared: true,
    };
    // eslint-disable-next-line @typescript-eslint/unbound-method
    vi.mocked(adminService.clearPriceLookupCache).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => useClearPriceLookupCache(), {
      wrapper,
    });

    result.current.mutate();

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(toast.success).toHaveBeenCalledWith(
      'Cache price_lookup cleared successfully'
    );
  });

  it('devrait invalider les queries billingConfig', async () => {
    const mockResponse = {
      cleared: true,
    };
    // eslint-disable-next-line @typescript-eslint/unbound-method
    vi.mocked(adminService.clearPriceLookupCache).mockResolvedValue(
      mockResponse
    );

    const invalidateQueriesSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const { result } = renderHook(() => useClearPriceLookupCache(), {
      wrapper,
    });

    result.current.mutate();

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(invalidateQueriesSpy).toHaveBeenCalledWith({
      queryKey: ['billingConfig'],
    });
  });

  it('devrait gérer les erreurs 401', async () => {
    const { ApiError } = await import('@/shared/api/errors');
    const apiError = new ApiError('Unauthorized', 401);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    vi.mocked(adminService.clearPriceLookupCache).mockRejectedValue(apiError);

    const { result } = renderHook(() => useClearPriceLookupCache(), {
      wrapper,
    });

    result.current.mutate();

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(toast.error).toHaveBeenCalledWith(
      'Vous devez être connecté pour effectuer cette action.'
    );
  });

  it('devrait gérer les erreurs 403', async () => {
    const { ApiError } = await import('@/shared/api/errors');
    const apiError = new ApiError('Forbidden', 403);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    vi.mocked(adminService.clearPriceLookupCache).mockRejectedValue(apiError);

    const { result } = renderHook(() => useClearPriceLookupCache(), {
      wrapper,
    });

    result.current.mutate();

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(toast.error).toHaveBeenCalledWith(
      "Vous n'avez pas les permissions nécessaires."
    );
  });

  it('devrait gérer les erreurs réseau', async () => {
    const { NetworkError } = await import('@/shared/api/errors');
    const networkError = new NetworkError('Network error', 'timeout');
    // eslint-disable-next-line @typescript-eslint/unbound-method
    vi.mocked(adminService.clearPriceLookupCache).mockRejectedValue(
      networkError
    );

    const { result } = renderHook(() => useClearPriceLookupCache(), {
      wrapper,
    });

    result.current.mutate();

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(toast.error).toHaveBeenCalledWith(
      'Service indisponible, réessayez.'
    );
  });

  it('devrait logger request_id en cas d\'erreur API', async () => {
    const { ApiError } = await import('@/shared/api/errors');
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const apiError = new ApiError('Server Error', 500, undefined, 'req-123');
    // eslint-disable-next-line @typescript-eslint/unbound-method
    vi.mocked(adminService.clearPriceLookupCache).mockRejectedValue(apiError);

    const { result } = renderHook(() => useClearPriceLookupCache(), {
      wrapper,
    });

    result.current.mutate();

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(consoleSpy).toHaveBeenCalledWith(
      '[ClearPriceLookupCache] request_id:',
      'req-123'
    );

    consoleSpy.mockRestore();
  });
});

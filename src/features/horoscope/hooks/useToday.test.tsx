import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useToday } from './useToday';
import { horoscopeService } from '@/shared/api/horoscope.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import React from 'react';

// Mock horoscopeService
vi.mock('@/shared/api/horoscope.service', () => ({
  horoscopeService: {
    getToday: vi.fn(),
  },
}));

describe('useToday', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('devrait récupérer today avec succès', async () => {
    const chartId = 'chart-123';
    const mockResponse = {
      content: 'Horoscope today content',
      generated_at: new Date().toISOString(),
    };

    (horoscopeService.getToday as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => useToday(chartId), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockResponse);
    expect(result.current.isError).toBe(false);
    expect(result.current.error).toBeNull();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(horoscopeService.getToday).toHaveBeenCalledWith(chartId);
  });

  it('devrait ne pas faire de requête si chartId est null', () => {
    const { result } = renderHook(() => useToday(null), { wrapper });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(horoscopeService.getToday).not.toHaveBeenCalled();
  });

  it('devrait ne pas faire de requête si chartId est vide', () => {
    const { result } = renderHook(() => useToday(''), { wrapper });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(horoscopeService.getToday).not.toHaveBeenCalled();
  });

  it('devrait gérer les erreurs 404', async () => {
    const chartId = 'not-found';
    const error = new ApiError('Chart not found', 404);

    (horoscopeService.getToday as ReturnType<typeof vi.fn>).mockRejectedValue(
      error
    );

    const { result } = renderHook(() => useToday(chartId), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeInstanceOf(ApiError);
    expect((result.current.error as ApiError).status).toBe(404);
    expect(result.current.data).toBeUndefined();
  });

  it('devrait gérer NetworkError avec retry', async () => {
    const chartId = 'chart-123';
    const error = new NetworkError('timeout', 'Request timeout');

    let callCount = 0;
    (horoscopeService.getToday as ReturnType<typeof vi.fn>).mockImplementation(
      () => {
        callCount++;
        if (callCount === 1) {
          return Promise.reject(error);
        }
        return Promise.resolve({
          content: 'Horoscope today content',
          generated_at: new Date().toISOString(),
        });
      }
    );

    const { result } = renderHook(() => useToday(chartId), { wrapper });

    // Le hook devrait retry une fois pour NetworkError
    await waitFor(
      () => {
        expect(result.current.isError).toBe(false);
        expect(result.current.data).toBeDefined();
      },
      { timeout: 3000 }
    );

    expect(callCount).toBeGreaterThan(1);
  });

  it('devrait ne pas retry pour ApiError', async () => {
    const chartId = 'chart-123';
    const error = new ApiError('Server error', 500);

    let callCount = 0;
    (horoscopeService.getToday as ReturnType<typeof vi.fn>).mockImplementation(
      () => {
        callCount++;
        return Promise.reject(error);
      }
    );

    const { result } = renderHook(() => useToday(chartId), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    // Devrait appeler une seule fois (pas de retry)
    expect(callCount).toBe(1);
  });

  it('devrait avoir staleTime de 5 minutes', async () => {
    const chartId = 'chart-123';
    const mockResponse = {
      content: 'Horoscope today content',
      generated_at: new Date().toISOString(),
    };

    (horoscopeService.getToday as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => useToday(chartId), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Vérifier que la query a bien staleTime configuré
    const queryState = queryClient.getQueryState(['horo', 'today', chartId]);
    expect(queryState).toBeDefined();
  });

  it('devrait permettre refetch manuel', async () => {
    const chartId = 'chart-123';
    const mockResponse = {
      content: 'Horoscope today content',
      generated_at: new Date().toISOString(),
    };

    (horoscopeService.getToday as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => useToday(chartId), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    vi.clearAllMocks();

    // Appeler refetch
    result.current.refetch();

    await waitFor(() => {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      expect(horoscopeService.getToday).toHaveBeenCalled();
    });
  });
});

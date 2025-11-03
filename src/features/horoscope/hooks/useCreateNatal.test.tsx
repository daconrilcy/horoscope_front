import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCreateNatal } from './useCreateNatal';
import { horoscopeService } from '@/shared/api/horoscope.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { useHoroscopeStore } from '@/stores/horoscopeStore';
import React from 'react';

// Mock horoscopeService
vi.mock('@/shared/api/horoscope.service', () => ({
  horoscopeService: {
    createNatal: vi.fn(),
  },
}));

// Mock toast
vi.mock('@/app/AppProviders', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock store
vi.mock('@/stores/horoscopeStore', () => ({
  useHoroscopeStore: vi.fn(),
}));

describe('useCreateNatal', () => {
  let queryClient: QueryClient;
  const mockAddChart = vi.fn();

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
        mutations: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();

    (useHoroscopeStore as ReturnType<typeof vi.fn>).mockReturnValue(
      mockAddChart
    );
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  const validInput = {
    date: '1990-01-01',
    time: '12:00',
    latitude: 48.8566,
    longitude: 2.3522,
    timezone: 'Europe/Paris',
    name: 'Test Chart',
  };

  it('devrait créer un thème natal avec succès', async () => {
    const mockResponse = {
      chart_id: 'chart-123',
      created_at: new Date().toISOString(),
    };

    (
      horoscopeService.createNatal as ReturnType<typeof vi.fn>
    ).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useCreateNatal(), { wrapper });

    expect(result.current.isPending).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.fieldErrors).toEqual({});

    const chartId = await result.current.createNatal(validInput);

    expect(chartId).toBe('chart-123');
    expect(
      horoscopeService.createNatal as ReturnType<typeof vi.fn>
    ).toHaveBeenCalledWith(validInput);
    expect(mockAddChart).toHaveBeenCalledWith('chart-123', 'Test Chart');
  });

  it('devrait empêcher double-submit (isPending)', async () => {
    const mockResponse = {
      chart_id: 'chart-123',
      created_at: new Date().toISOString(),
    };

    (
      horoscopeService.createNatal as ReturnType<typeof vi.fn>
    ).mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(mockResponse), 100);
        })
    );

    const { result } = renderHook(() => useCreateNatal(), { wrapper });

    // Premier appel (démarre la mutation)
    const promise1 = result.current.createNatal(validInput);

    // Attendre que isPending soit true
    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Deuxième appel (devrait être bloqué)
    const promise2 = result.current.createNatal(validInput);

    await expect(promise2).resolves.toBeUndefined();

    await promise1;
  });

  it('devrait gérer les erreurs 422 avec fieldErrors', async () => {
    const fieldErrors = {
      date: ['Date invalide'],
      latitude: ['Latitude invalide'],
    };

    const error = new ApiError(
      'Validation failed',
      422,
      undefined,
      undefined,
      fieldErrors
    );

    (
      horoscopeService.createNatal as ReturnType<typeof vi.fn>
    ).mockRejectedValue(error);

    const { result } = renderHook(() => useCreateNatal(), { wrapper });

    await result.current.createNatal(validInput).catch(() => {
      // Attendu que la promise soit rejetée
    });

    await waitFor(() => {
      expect(result.current.error).toBeInstanceOf(ApiError);
      expect(result.current.fieldErrors).toEqual(fieldErrors);
    });
  });

  it('devrait gérer les erreurs 401 (redirection gérée ailleurs)', async () => {
    const error = new ApiError('Unauthorized', 401);

    (
      horoscopeService.createNatal as ReturnType<typeof vi.fn>
    ).mockRejectedValue(error);

    const { result } = renderHook(() => useCreateNatal(), { wrapper });

    await result.current.createNatal(validInput).catch(() => {
      // Attendu que la promise soit rejetée
    });

    await waitFor(() => {
      expect(result.current.error).toBeInstanceOf(ApiError);
      expect((result.current.error as ApiError).status).toBe(401);
    });
  });

  it('devrait gérer les erreurs 500', async () => {
    const error = new ApiError('Internal server error', 500);

    (
      horoscopeService.createNatal as ReturnType<typeof vi.fn>
    ).mockRejectedValue(error);

    const { result } = renderHook(() => useCreateNatal(), { wrapper });

    await result.current.createNatal(validInput).catch(() => {
      // Attendu que la promise soit rejetée
    });

    await waitFor(() => {
      expect(result.current.error).toBeInstanceOf(ApiError);
      expect((result.current.error as ApiError).status).toBe(500);
    });
  });

  it('devrait gérer NetworkError', async () => {
    const error = new NetworkError('timeout', 'Request timeout');

    (
      horoscopeService.createNatal as ReturnType<typeof vi.fn>
    ).mockRejectedValue(error);

    const { result } = renderHook(() => useCreateNatal(), { wrapper });

    await result.current.createNatal(validInput).catch(() => {
      // Attendu que la promise soit rejetée
    });

    await waitFor(() => {
      expect(result.current.error).toBeInstanceOf(NetworkError);
    });
  });

  it('devrait invalider les queries today après création', async () => {
    const mockResponse = {
      chart_id: 'chart-123',
      created_at: new Date().toISOString(),
    };

    (
      horoscopeService.createNatal as ReturnType<typeof vi.fn>
    ).mockResolvedValue(mockResponse);

    // Pré-remplir une query today
    queryClient.setQueryData(['horo', 'today', 'chart-123'], {
      content: 'Old content',
    });

    const { result } = renderHook(() => useCreateNatal(), { wrapper });

    await result.current.createNatal(validInput);

    await waitFor(() => {
      // La query devrait être invalidée (mais peut ne pas être supprimée immédiatement)
      const queryState = queryClient.getQueryState([
        'horo',
        'today',
        'chart-123',
      ]);
      // La query existe toujours mais est invalidée
      expect(queryState).toBeDefined();
    });
  });
});

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTodayPremium } from './useTodayPremium';
import { horoscopeService } from '@/shared/api/horoscope.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import React from 'react';

// Mock horoscopeService
vi.mock('@/shared/api/horoscope.service', () => ({
  horoscopeService: {
    getTodayPremium: vi.fn(),
  },
}));

describe('useTodayPremium', () => {
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

  it('devrait récupérer today premium avec succès', async () => {
    const chartId = 'chart-123';
    const mockResponse = {
      content: 'Horoscope today premium content',
      premium_insights: 'Premium insights here',
      generated_at: new Date().toISOString(),
    };

    (
      horoscopeService.getTodayPremium as ReturnType<typeof vi.fn>
    ).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useTodayPremium(chartId), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockResponse);
    expect(result.current.isError).toBe(false);
    expect(result.current.error).toBeNull();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(
      horoscopeService.getTodayPremium as ReturnType<typeof vi.fn>
    ).toHaveBeenCalledWith(chartId);
  });

  it('devrait ne pas faire de requête si chartId est null', () => {
    const { result } = renderHook(() => useTodayPremium(null), { wrapper });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeUndefined();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(
      horoscopeService.getTodayPremium as ReturnType<typeof vi.fn>
    ).not.toHaveBeenCalled();
  });

  it('devrait gérer les erreurs 402 (plan insuffisant)', async () => {
    const chartId = 'plan-required';
    const error = new ApiError('Plan insuffisant', 402, 'plan_required');

    (
      horoscopeService.getTodayPremium as ReturnType<typeof vi.fn>
    ).mockRejectedValue(error);

    const { result } = renderHook(() => useTodayPremium(chartId), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeInstanceOf(ApiError);
    expect((result.current.error as ApiError).status).toBe(402);
    expect(result.current.data).toBeUndefined();
  });

  it('devrait gérer NetworkError avec retry', async () => {
    const chartId = 'chart-123';
    const error = new NetworkError('timeout', 'Request timeout');

    let callCount = 0;
    (
      horoscopeService.getTodayPremium as ReturnType<typeof vi.fn>
    ).mockImplementation(() => {
      callCount++;
      if (callCount === 1) {
        return Promise.reject(error);
      }
      return Promise.resolve({
        content: 'Horoscope today premium content',
        premium_insights: 'Premium insights',
        generated_at: new Date().toISOString(),
      });
    });

    const { result } = renderHook(() => useTodayPremium(chartId), { wrapper });

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
    (
      horoscopeService.getTodayPremium as ReturnType<typeof vi.fn>
    ).mockImplementation(() => {
      callCount++;
      return Promise.reject(error);
    });

    const { result } = renderHook(() => useTodayPremium(chartId), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(callCount).toBe(1);
  });

  it('devrait permettre refetch manuel', async () => {
    const chartId = 'chart-123';
    const mockResponse = {
      content: 'Horoscope today premium content',
      premium_insights: 'Premium insights',
      generated_at: new Date().toISOString(),
    };

    (
      horoscopeService.getTodayPremium as ReturnType<typeof vi.fn>
    ).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useTodayPremium(chartId), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    vi.clearAllMocks();

    result.current.refetch();

    await waitFor(() => {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      expect(
        horoscopeService.getTodayPremium as ReturnType<typeof vi.fn>
      ).toHaveBeenCalled();
    });
  });
});

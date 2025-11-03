import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useMultiPaywall } from './useMultiPaywall';
import { paywallService } from '@/shared/api/paywall.service';
import type { PaywallDecision } from '@/shared/api/paywall.service';

// Mock paywallService
vi.mock('@/shared/api/paywall.service', () => ({
  paywallService: {
    decision: vi.fn(),
  },
}));

describe('useMultiPaywall', () => {
  let queryClient: QueryClient;
  let wrapper: React.ComponentType<{ children: React.ReactNode }>;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    vi.clearAllMocks();
  });

  it('devrait faire des requêtes parallèles pour plusieurs features', async () => {
    const mockDecision1: PaywallDecision = { allowed: true };
    const mockDecision2: PaywallDecision = { allowed: false, reason: 'plan' };

    vi.mocked(paywallService.decision)
      .mockResolvedValueOnce(mockDecision1)
      .mockResolvedValueOnce(mockDecision2);

    const { result } = renderHook(
      () => useMultiPaywall(['feature1', 'feature2']),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isLoadingAny).toBe(false);
    });

    expect(paywallService.decision).toHaveBeenCalledTimes(2);
    expect(paywallService.decision).toHaveBeenCalledWith('feature1');
    expect(paywallService.decision).toHaveBeenCalledWith('feature2');
    expect(result.current.results).toHaveLength(2);
    expect(result.current.results[0].isAllowed).toBe(true);
    expect(result.current.results[1].isAllowed).toBe(false);
    expect(result.current.results[1].reason).toBe('plan');
  });

  it('devrait calculer isLoadingAny correctement', async () => {
    let resolve1: (value: PaywallDecision) => void;
    let resolve2: (value: PaywallDecision) => void;

    const promise1 = new Promise<PaywallDecision>((resolve) => {
      resolve1 = resolve;
    });
    const promise2 = new Promise<PaywallDecision>((resolve) => {
      resolve2 = resolve;
    });

    vi.mocked(paywallService.decision)
      .mockReturnValueOnce(promise1)
      .mockReturnValueOnce(promise2);

    const { result } = renderHook(
      () => useMultiPaywall(['feature1', 'feature2']),
      { wrapper }
    );

    // Pendant le chargement
    expect(result.current.isLoadingAny).toBe(true);

    // Résoudre les promesses
    resolve1!({ allowed: true });
    resolve2!({ allowed: true });

    await waitFor(() => {
      expect(result.current.isLoadingAny).toBe(false);
    });
  });

  it('devrait calculer isErrorAny correctement', async () => {
    const mockError = new Error('Network error');

    vi.mocked(paywallService.decision)
      .mockResolvedValueOnce({ allowed: true })
      .mockRejectedValueOnce(mockError);

    const { result } = renderHook(
      () => useMultiPaywall(['feature1', 'feature2']),
      { wrapper }
    );

    await waitFor(() => {
      expect(result.current.isErrorAny).toBe(true);
    });

    expect(result.current.results[0].error).toBeNull();
    expect(result.current.results[1].error).toBe(mockError);
  });

  it('devrait extraire retryAfter depuis data', async () => {
    const mockDecision: PaywallDecision = {
      allowed: false,
      reason: 'rate',
      retry_after: 60,
    };

    vi.mocked(paywallService.decision).mockResolvedValue(mockDecision);

    const { result } = renderHook(() => useMultiPaywall(['feature1']), {
      wrapper,
    });

    await waitFor(() => {
      expect(result.current.isLoadingAny).toBe(false);
    });

    expect(result.current.results[0].retryAfter).toBe(60);
  });

  it('devrait gérer un tableau vide', () => {
    const { result } = renderHook(() => useMultiPaywall([]), { wrapper });

    expect(result.current.results).toHaveLength(0);
    expect(result.current.isLoadingAny).toBe(false);
    expect(result.current.isErrorAny).toBe(false);
  });
});

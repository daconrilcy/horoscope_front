import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePaywall } from './usePaywall';
import { paywallService } from '@/shared/api/paywall.service';
import { ApiError } from '@/shared/api/errors';
import { FEATURES } from '@/shared/config/features';
import React from 'react';

// Mock paywallService
vi.mock('@/shared/api/paywall.service', () => ({
  paywallService: {
    decision: vi.fn(),
  },
}));

describe('usePaywall', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
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

  it('devrait retourner isAllowed: true quand allowed: true', async () => {
    const mockResponse = {
      allowed: true as const,
    };

    (paywallService.decision as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => usePaywall(FEATURES.CHAT_MSG_PER_DAY), {
      wrapper,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAllowed).toBe(true);
    expect(result.current.reason).toBeUndefined();
    expect(result.current.upgradeUrl).toBeUndefined();
    expect(result.current.data).toEqual(mockResponse);
  });

  it('devrait retourner isAllowed: false avec reason: plan et upgrade_url', async () => {
    const mockResponse = {
      allowed: false as const,
      reason: 'plan' as const,
      upgrade_url: 'https://example.com/upgrade',
    };

    (paywallService.decision as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => usePaywall(FEATURES.CHAT_MSG_PER_DAY), {
      wrapper,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAllowed).toBe(false);
    expect(result.current.reason).toBe('plan');
    expect(result.current.upgradeUrl).toBe('https://example.com/upgrade');
    expect(result.current.data).toEqual(mockResponse);
  });

  it('devrait retourner isAllowed: false sans upgrade_url (402)', async () => {
    const mockResponse = {
      allowed: false as const,
      reason: 'plan' as const,
    };

    (paywallService.decision as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => usePaywall(FEATURES.CHAT_MSG_PER_DAY), {
      wrapper,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAllowed).toBe(false);
    expect(result.current.reason).toBe('plan');
    expect(result.current.upgradeUrl).toBeUndefined();
  });

  it('devrait retourner isAllowed: false avec reason: rate et retry_after (429)', async () => {
    const mockResponse = {
      allowed: false as const,
      reason: 'rate' as const,
      retry_after: 3600,
      upgrade_url: 'https://example.com/upgrade',
    };

    (paywallService.decision as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse
    );

    const { result } = renderHook(() => usePaywall(FEATURES.CHAT_MSG_PER_DAY), {
      wrapper,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAllowed).toBe(false);
    expect(result.current.reason).toBe('rate');
    expect(result.current.upgradeUrl).toBe('https://example.com/upgrade');
    expect(result.current.retryAfter).toBe(3600);
  });

  it('devrait retourner isLoading: true pendant le chargement', () => {
    (paywallService.decision as ReturnType<typeof vi.fn>).mockImplementation(
      () =>
        new Promise((resolve) => {
          // Ne jamais résoudre pour tester isLoading
          setTimeout(() => {
            resolve({ allowed: true });
          }, 1000);
        })
    );

    const { result } = renderHook(() => usePaywall(FEATURES.CHAT_MSG_PER_DAY), {
      wrapper,
    });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.isAllowed).toBe(false);
  });

  it('devrait retourner error si la requête échoue', async () => {
    const mockError = new ApiError('Payment required', 402);

    (paywallService.decision as ReturnType<typeof vi.fn>).mockRejectedValue(
      mockError
    );

    const { result } = renderHook(() => usePaywall(FEATURES.CHAT_MSG_PER_DAY), {
      wrapper,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe(mockError);
    expect(result.current.isAllowed).toBe(false);
  });

  it('devrait retourner error si 429 avec ApiError', async () => {
    const mockError = new ApiError('Too many requests', 429);

    (paywallService.decision as ReturnType<typeof vi.fn>).mockRejectedValue(
      mockError
    );

    const { result } = renderHook(() => usePaywall(FEATURES.CHAT_MSG_PER_DAY), {
      wrapper,
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe(mockError);
    expect(result.current.isAllowed).toBe(false);
  });
});

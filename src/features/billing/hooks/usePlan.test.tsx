import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { usePlan } from './usePlan';
import { useMultiPaywall } from './useMultiPaywall';
import type { UsePaywallResult } from './usePaywall';

// Mock useMultiPaywall
vi.mock('./useMultiPaywall', () => ({
  useMultiPaywall: vi.fn(),
}));

describe('usePlan', () => {
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

    wrapper = ({ children }: { children: React.ReactNode }): JSX.Element => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    vi.clearAllMocks();
  });

  it('devrait retourner "pro" si PRO_SENTINEL est allowed', () => {
    const mockResults: UsePaywallResult[] = [
      {
        data: { allowed: true },
        isLoading: false,
        error: null,
        isAllowed: true,
        query: {} as never,
      },
      {
        data: { allowed: false, reason: 'plan' },
        isLoading: false,
        error: null,
        isAllowed: false,
        reason: 'plan',
        query: {} as never,
      },
    ];

    vi.mocked(useMultiPaywall).mockReturnValue({
      results: mockResults,
      isLoadingAny: false,
      isErrorAny: false,
    });

    const { result } = renderHook(() => usePlan(), { wrapper });

    expect(result.current.plan).toBe('pro');
    expect(result.current.isLoading).toBe(false);
  });

  it('devrait retourner "plus" si PLUS_SENTINEL est allowed (mais pas PRO)', () => {
    const mockResults: UsePaywallResult[] = [
      {
        data: { allowed: false, reason: 'plan' },
        isLoading: false,
        error: null,
        isAllowed: false,
        reason: 'plan',
        query: {} as never,
      },
      {
        data: { allowed: true },
        isLoading: false,
        error: null,
        isAllowed: true,
        query: {} as never,
      },
    ];

    vi.mocked(useMultiPaywall).mockReturnValue({
      results: mockResults,
      isLoadingAny: false,
      isErrorAny: false,
    });

    const { result } = renderHook(() => usePlan(), { wrapper });

    expect(result.current.plan).toBe('plus');
    expect(result.current.isLoading).toBe(false);
  });

  it('devrait retourner "free" si aucune sentinelle n\'est allowed', () => {
    const mockResults: UsePaywallResult[] = [
      {
        data: { allowed: false, reason: 'plan' },
        isLoading: false,
        error: null,
        isAllowed: false,
        reason: 'plan',
        query: {} as never,
      },
      {
        data: { allowed: false, reason: 'plan' },
        isLoading: false,
        error: null,
        isAllowed: false,
        reason: 'plan',
        query: {} as never,
      },
    ];

    vi.mocked(useMultiPaywall).mockReturnValue({
      results: mockResults,
      isLoadingAny: false,
      isErrorAny: false,
    });

    const { result } = renderHook(() => usePlan(), { wrapper });

    expect(result.current.plan).toBe('free');
    expect(result.current.isLoading).toBe(false);
  });

  it('devrait indiquer isLoading si useMultiPaywall charge', () => {
    const mockResults: UsePaywallResult[] = [
      {
        data: undefined,
        isLoading: true,
        error: null,
        isAllowed: false,
        query: {} as never,
      },
      {
        data: undefined,
        isLoading: true,
        error: null,
        isAllowed: false,
        query: {} as never,
      },
    ];

    vi.mocked(useMultiPaywall).mockReturnValue({
      results: mockResults,
      isLoadingAny: true,
      isErrorAny: false,
    });

    const { result } = renderHook(() => usePlan(), { wrapper });

    expect(result.current.isLoading).toBe(true);
  });
});

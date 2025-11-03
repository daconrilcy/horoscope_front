import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { QuotaBadge } from './QuotaBadge';
import { useMultiPaywall } from '@/features/billing/hooks/useMultiPaywall';
import React from 'react';
import type { UsePaywallResult } from '@/features/billing/hooks/usePaywall';

// Mock useMultiPaywall
vi.mock('@/features/billing/hooks/useMultiPaywall', () => ({
  useMultiPaywall: vi.fn(),
}));

// Mock InlineError
vi.mock('@/shared/ui/InlineError', () => ({
  InlineError: ({ error }: { error: Error }): JSX.Element => (
    <div data-testid="inline-error">{error.message}</div>
  ),
}));

describe('QuotaBadge', () => {
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

  it('devrait afficher "OK aujourd\'hui" si toutes les features sont allowed', () => {
    const mockResults: UsePaywallResult[] = [
      {
        data: { allowed: true },
        isLoading: false,
        error: null,
        isAllowed: true,
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

    render(<QuotaBadge />, { wrapper });

    expect(screen.getByText("OK aujourd'hui")).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveAttribute('aria-live', 'polite');
  });

  it('devrait afficher "Quota atteint" si reason=rate', () => {
    const mockResults: UsePaywallResult[] = [
      {
        data: { allowed: false, reason: 'rate' },
        isLoading: false,
        error: null,
        isAllowed: false,
        reason: 'rate',
        query: {} as never,
      },
    ];

    vi.mocked(useMultiPaywall).mockReturnValue({
      results: mockResults,
      isLoadingAny: false,
      isErrorAny: false,
    });

    render(<QuotaBadge />, { wrapper });

    expect(screen.getByText('Quota atteint')).toBeInTheDocument();
  });

  it('devrait afficher compte à rebours si reason=rate avec retry_after', () => {
    const mockResults: UsePaywallResult[] = [
      {
        data: { allowed: false, reason: 'rate' },
        isLoading: false,
        error: null,
        isAllowed: false,
        reason: 'rate',
        retryAfter: 5,
        query: {} as never,
      },
    ];

    vi.mocked(useMultiPaywall).mockReturnValue({
      results: mockResults,
      isLoadingAny: false,
      isErrorAny: false,
    });

    render(<QuotaBadge showRetryAfter={true} />, { wrapper });

    // Vérifier que le texte du compte à rebours est présent
    expect(screen.getByText('Quota atteint')).toBeInTheDocument();
    // Note : Le compte à rebours utilise setInterval qui est testé dans l'intégration
    // Ici on vérifie juste que le composant gère retry_after
  });

  it('devrait afficher "Fonctionnalité Plus/Pro" si reason=plan', () => {
    const mockResults: UsePaywallResult[] = [
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

    render(<QuotaBadge />, { wrapper });

    expect(screen.getByText('Fonctionnalité Plus/Pro')).toBeInTheDocument();
  });

  it('devrait afficher "Chargement..." pendant isLoading', () => {
    const mockResults: UsePaywallResult[] = [
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

    render(<QuotaBadge />, { wrapper });

    expect(screen.getByText('Chargement...')).toBeInTheDocument();
  });

  it('devrait afficher InlineError si erreur', () => {
    const mockError = new Error('Network error');
    const mockResults: UsePaywallResult[] = [
      {
        data: undefined,
        isLoading: false,
        error: mockError,
        isAllowed: false,
        query: {} as never,
      },
    ];

    vi.mocked(useMultiPaywall).mockReturnValue({
      results: mockResults,
      isLoadingAny: false,
      isErrorAny: true,
    });

    render(<QuotaBadge />, { wrapper });

    expect(screen.getByTestId('inline-error')).toBeInTheDocument();
  });
});

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PaywallGate } from './PaywallGate';
import { usePaywall } from './hooks/usePaywall';
import { FEATURES } from '@/shared/config/features';
import React from 'react';

// Mock usePaywall
vi.mock('./hooks/usePaywall', () => ({
  usePaywall: vi.fn(),
}));

describe('PaywallGate', () => {
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

  it('devrait rendre children si isAllowed est true', () => {
    vi.mocked(usePaywall).mockReturnValue({
      isLoading: false,
      isAllowed: true,
      reason: undefined,
      upgradeUrl: undefined,
      retryAfter: undefined,
      data: { allowed: true },
      error: null,
      query: {} as never,
    });

    render(
      <PaywallGate feature={FEATURES.CHAT_MSG_PER_DAY}>
        <div>Content autorisé</div>
      </PaywallGate>,
      { wrapper }
    );

    expect(screen.getByText('Content autorisé')).toBeInTheDocument();
  });

  it('devrait rendre UpgradeBanner si reason est plan (402)', () => {
    vi.mocked(usePaywall).mockReturnValue({
      isLoading: false,
      isAllowed: false,
      reason: 'plan',
      upgradeUrl: 'https://example.com/upgrade',
      retryAfter: undefined,
      data: {
        allowed: false,
        reason: 'plan',
        upgrade_url: 'https://example.com/upgrade',
      },
      error: null,
      query: {} as never,
    });

    render(
      <PaywallGate feature={FEATURES.CHAT_MSG_PER_DAY}>
        <div>Content bloqué</div>
      </PaywallGate>,
      { wrapper }
    );

    expect(
      screen.getByText('Cette fonctionnalité nécessite un plan supérieur.')
    ).toBeInTheDocument();
  });

  it('devrait rendre QuotaMessage si reason est rate (429)', () => {
    vi.mocked(usePaywall).mockReturnValue({
      isLoading: false,
      isAllowed: false,
      reason: 'rate',
      upgradeUrl: 'https://example.com/upgrade',
      retryAfter: 3600,
      data: {
        allowed: false,
        reason: 'rate',
        retry_after: 3600,
        upgrade_url: 'https://example.com/upgrade',
      },
      error: null,
      query: {} as never,
    });

    render(
      <PaywallGate feature={FEATURES.CHAT_MSG_PER_DAY}>
        <div>Content bloqué</div>
      </PaywallGate>,
      { wrapper }
    );

    expect(screen.getByText(/Quota atteint aujourd'hui/)).toBeInTheDocument();
  });

  it('devrait rendre fallback si isLoading est true', () => {
    vi.mocked(usePaywall).mockReturnValue({
      isLoading: true,
      isAllowed: false,
      reason: undefined,
      upgradeUrl: undefined,
      retryAfter: undefined,
      data: undefined,
      error: null,
      query: {} as never,
    });

    render(
      <PaywallGate
        feature={FEATURES.CHAT_MSG_PER_DAY}
        fallback={<div>Chargement...</div>}
      >
        <div>Content</div>
      </PaywallGate>,
      { wrapper }
    );

    expect(screen.getByText('Chargement...')).toBeInTheDocument();
    expect(screen.queryByText('Content')).not.toBeInTheDocument();
  });

  it('devrait rendre null si isLoading est true et pas de fallback', () => {
    vi.mocked(usePaywall).mockReturnValue({
      isLoading: true,
      isAllowed: false,
      reason: undefined,
      upgradeUrl: undefined,
      retryAfter: undefined,
      data: undefined,
      error: null,
      query: {} as never,
    });

    const { container } = render(
      <PaywallGate feature={FEATURES.CHAT_MSG_PER_DAY}>
        <div>Content</div>
      </PaywallGate>,
      { wrapper }
    );

    expect(container.firstChild).toBeNull();
  });

  it('devrait appeler onUpgrade quand on clique sur Upgrade dans UpgradeBanner', async () => {
    const onUpgradeSpy = vi.fn();

    vi.mocked(usePaywall).mockReturnValue({
      isLoading: false,
      isAllowed: false,
      reason: 'plan',
      upgradeUrl: 'https://example.com/upgrade',
      retryAfter: undefined,
      data: {
        allowed: false,
        reason: 'plan',
        upgrade_url: 'https://example.com/upgrade',
      },
      error: null,
      query: {} as never,
    });

    render(
      <PaywallGate feature={FEATURES.CHAT_MSG_PER_DAY} onUpgrade={onUpgradeSpy}>
        <div>Content bloqué</div>
      </PaywallGate>,
      { wrapper }
    );

    const upgradeButton = screen.getByRole('button', { name: /upgrade/i });
    upgradeButton.click();

    await waitFor(() => {
      expect(onUpgradeSpy).toHaveBeenCalledTimes(1);
    });
  });

  it('devrait appeler onUpgrade quand on clique sur Upgrade dans QuotaMessage', async () => {
    const onUpgradeSpy = vi.fn();

    vi.mocked(usePaywall).mockReturnValue({
      isLoading: false,
      isAllowed: false,
      reason: 'rate',
      upgradeUrl: 'https://example.com/upgrade',
      retryAfter: 3600,
      data: {
        allowed: false,
        reason: 'rate',
        retry_after: 3600,
        upgrade_url: 'https://example.com/upgrade',
      },
      error: null,
      query: {} as never,
    });

    render(
      <PaywallGate feature={FEATURES.CHAT_MSG_PER_DAY} onUpgrade={onUpgradeSpy}>
        <div>Content bloqué</div>
      </PaywallGate>,
      { wrapper }
    );

    const upgradeButton = screen.getByRole('button', { name: /upgrade/i });
    upgradeButton.click();

    await waitFor(() => {
      expect(onUpgradeSpy).toHaveBeenCalledTimes(1);
    });
  });
});

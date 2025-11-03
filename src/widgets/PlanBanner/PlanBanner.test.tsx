import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PlanBanner } from './PlanBanner';
import { usePlan } from '@/features/billing/hooks/usePlan';
import { PortalButton } from '@/widgets/PortalButton/PortalButton';
import { UpgradeButton } from '@/widgets/UpgradeButton/UpgradeButton';
import React from 'react';

// Mock usePlan
vi.mock('@/features/billing/hooks/usePlan', () => ({
  usePlan: vi.fn(),
}));

// Mock PortalButton
vi.mock('@/widgets/PortalButton/PortalButton', () => ({
  PortalButton: ({ label }: { label?: string }) => (
    <button data-testid="portal-button">{label}</button>
  ),
}));

// Mock UpgradeButton
vi.mock('@/widgets/UpgradeButton/UpgradeButton', () => ({
  UpgradeButton: ({ plan }: { plan: string }) => (
    <button data-testid={`upgrade-button-${plan}`}>Upgrade {plan}</button>
  ),
}));

describe('PlanBanner', () => {
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

  it('devrait afficher "Gratuit" pour plan=free', () => {
    vi.mocked(usePlan).mockReturnValue({
      plan: 'free',
      isLoading: false,
    });

    render(<PlanBanner />, { wrapper });

    expect(screen.getByText('Gratuit')).toBeInTheDocument();
    expect(screen.getByTestId('upgrade-button-plus')).toBeInTheDocument();
    expect(screen.getByTestId('upgrade-button-pro')).toBeInTheDocument();
    expect(screen.queryByTestId('portal-button')).not.toBeInTheDocument();
  });

  it('devrait afficher "Plus" pour plan=plus', () => {
    vi.mocked(usePlan).mockReturnValue({
      plan: 'plus',
      isLoading: false,
    });

    render(<PlanBanner />, { wrapper });

    expect(screen.getByText('Plus')).toBeInTheDocument();
    expect(screen.getByTestId('portal-button')).toBeInTheDocument();
    expect(screen.queryByTestId('upgrade-button-plus')).not.toBeInTheDocument();
    expect(screen.queryByTestId('upgrade-button-pro')).not.toBeInTheDocument();
  });

  it('devrait afficher "Pro" pour plan=pro', () => {
    vi.mocked(usePlan).mockReturnValue({
      plan: 'pro',
      isLoading: false,
    });

    render(<PlanBanner />, { wrapper });

    expect(screen.getByText('Pro')).toBeInTheDocument();
    expect(screen.getByTestId('portal-button')).toBeInTheDocument();
    expect(screen.queryByTestId('upgrade-button-plus')).not.toBeInTheDocument();
    expect(screen.queryByTestId('upgrade-button-pro')).not.toBeInTheDocument();
  });

  it('devrait afficher "Chargement du plan..." pendant isLoading', () => {
    vi.mocked(usePlan).mockReturnValue({
      plan: 'free',
      isLoading: true,
    });

    render(<PlanBanner />, { wrapper });

    expect(screen.getByText('Chargement du plan...')).toBeInTheDocument();
  });
});

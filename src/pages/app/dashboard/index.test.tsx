import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { DashboardPage } from './index';
import { useAuthStore } from '@/stores/authStore';
import { useHoroscopeStore } from '@/stores/horoscopeStore';
import { usePlan } from '@/features/billing/hooks/usePlan';
import { usePaywall } from '@/features/billing/hooks/usePaywall';
import { ROUTES } from '@/shared/config/routes';
import React from 'react';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock stores et hooks
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

vi.mock('@/stores/horoscopeStore', () => ({
  useHoroscopeStore: vi.fn(),
}));

vi.mock('@/features/billing/hooks/usePlan', () => ({
  usePlan: vi.fn(),
}));

vi.mock('@/features/billing/hooks/usePaywall', () => ({
  usePaywall: vi.fn(),
}));

// Mock widgets
vi.mock('@/widgets/PlanBanner/PlanBanner', () => ({
  PlanBanner: () => <div data-testid="plan-banner">Plan Banner</div>,
}));

vi.mock('@/widgets/QuotaBadge/QuotaBadge', () => ({
  QuotaBadge: () => <div data-testid="quota-badge">Quota Badge</div>,
}));

describe('DashboardPage', () => {
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
    mockNavigate.mockClear();

    // Mocks par défaut
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        userRef: { id: 'user-123', email: 'test@example.com' },
        logout: vi.fn(),
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    vi.mocked(useHoroscopeStore).mockImplementation((selector) => {
      const mockState = {
        recentCharts: [],
      };
      return selector(mockState as ReturnType<typeof useHoroscopeStore>);
    });

    vi.mocked(usePlan).mockReturnValue({
      plan: 'free',
      isLoading: false,
    });

    vi.mocked(usePaywall).mockReturnValue({
      data: { allowed: true },
      isLoading: false,
      error: null,
      isAllowed: true,
      reason: undefined,
      upgradeUrl: undefined,
      retryAfter: undefined,
      query: {} as ReturnType<typeof usePaywall>['query'],
    });
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );

  it('devrait afficher le titre du dashboard', () => {
    render(<DashboardPage />, { wrapper });

    expect(screen.getByText('Tableau de bord')).toBeInTheDocument();
  });

  it('devrait afficher userRef.email dans la carte Auth', () => {
    render(<DashboardPage />, { wrapper });

    expect(screen.getByText(/Email :/)).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('devrait afficher PlanBanner et QuotaBadge', () => {
    render(<DashboardPage />, { wrapper });

    expect(screen.getByTestId('plan-banner')).toBeInTheDocument();
    expect(screen.getByTestId('quota-badge')).toBeInTheDocument();
  });

  it('devrait afficher un loader pour PlanBanner si isLoading est true', () => {
    vi.mocked(usePlan).mockReturnValue({
      plan: 'free',
      isLoading: true,
    });

    render(<DashboardPage />, { wrapper });

    expect(screen.getByText(/Chargement du plan/i)).toBeInTheDocument();
    expect(screen.queryByTestId('plan-banner')).not.toBeInTheDocument();
  });

  it('devrait afficher "Créer mon thème natal" si aucun chart récent', () => {
    vi.mocked(useHoroscopeStore).mockImplementation((selector) => {
      const mockState = {
        recentCharts: [],
      };
      return selector(mockState as ReturnType<typeof useHoroscopeStore>);
    });

    render(<DashboardPage />, { wrapper });

    expect(screen.getByText(/Créer mon thème natal/i)).toBeInTheDocument();
    expect(screen.queryByText(/Voir Today/i)).not.toBeInTheDocument();
  });

  it('devrait afficher "Voir Today" avec le dernier chartId si des charts existent', () => {
    vi.mocked(useHoroscopeStore).mockImplementation((selector) => {
      const mockState = {
        recentCharts: [
          {
            chartId: 'chart-123',
            label: 'Mon thème natal',
            createdAt: new Date().toISOString(),
          },
        ],
      };
      return selector(mockState as ReturnType<typeof useHoroscopeStore>);
    });

    render(<DashboardPage />, { wrapper });

    expect(screen.getByText(/Voir Today/i)).toBeInTheDocument();
    expect(screen.getByText(/Mon thème natal/i)).toBeInTheDocument();
    expect(
      screen.queryByText(/Créer mon thème natal/i)
    ).not.toBeInTheDocument();
  });

  it('devrait afficher badge "Plus requis" sur Chat si paywall gated', () => {
    vi.mocked(usePaywall).mockReturnValue({
      data: { allowed: false, reason: 'plan' },
      isLoading: false,
      error: null,
      isAllowed: false,
      reason: 'plan',
      upgradeUrl: undefined,
      retryAfter: undefined,
      query: {} as ReturnType<typeof usePaywall>['query'],
    });

    render(<DashboardPage />, { wrapper });

    expect(screen.getByText(/Plus requis/i)).toBeInTheDocument();
  });

  it('ne devrait pas afficher badge "Plus requis" si paywall allowed', () => {
    vi.mocked(usePaywall).mockReturnValue({
      data: { allowed: true },
      isLoading: false,
      error: null,
      isAllowed: true,
      reason: undefined,
      upgradeUrl: undefined,
      retryAfter: undefined,
      query: {} as ReturnType<typeof usePaywall>['query'],
    });

    render(<DashboardPage />, { wrapper });

    expect(screen.queryByText(/Plus requis/i)).not.toBeInTheDocument();
  });

  it('devrait naviguer vers Horoscope au clic sur la carte Horoscope', async () => {
    const user = userEvent.setup();
    render(<DashboardPage />, { wrapper });

    const horoscopeCard = screen.getByRole('button', {
      name: /Créer mon thème natal/i,
    });

    await user.click(horoscopeCard);

    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.APP.HOROSCOPE);
  });

  it('devrait naviguer vers Chat au clic sur la carte Chat', async () => {
    const user = userEvent.setup();
    render(<DashboardPage />, { wrapper });

    const chatCard = screen.getByRole('button', {
      name: /Accéder au chat/i,
    });

    await user.click(chatCard);

    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.APP.CHAT);
  });

  it('devrait naviguer vers Account au clic sur la carte Account', async () => {
    const user = userEvent.setup();
    render(<DashboardPage />, { wrapper });

    const accountCard = screen.getByRole('button', {
      name: /Gérer mon compte/i,
    });

    await user.click(accountCard);

    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.APP.ACCOUNT);
  });

  it('devrait appeler logout au clic sur "Se déconnecter"', async () => {
    const mockLogout = vi.fn();
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        userRef: { id: 'user-123', email: 'test@example.com' },
        logout: mockLogout,
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    const user = userEvent.setup();
    render(<DashboardPage />, { wrapper });

    const logoutButton = screen.getByRole('button', {
      name: /Se déconnecter/i,
    });

    await user.click(logoutButton);

    expect(mockLogout).toHaveBeenCalledWith(queryClient);
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.LOGIN, { replace: true });
  });

  it('devrait afficher InlineError si paywall error', () => {
    const mockError = new Error('Paywall error');
    vi.mocked(usePaywall).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: mockError,
      isAllowed: false,
      reason: undefined,
      upgradeUrl: undefined,
      retryAfter: undefined,
      query: {} as ReturnType<typeof usePaywall>['query'],
    });

    render(<DashboardPage />, { wrapper });

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/Paywall error/i)).toBeInTheDocument();
  });

  it('devrait utiliser le tag main pour la structure', () => {
    render(<DashboardPage />, { wrapper });

    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
  });

  it('devrait afficher "Non disponible" si userRef.email est absent', () => {
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        userRef: undefined,
        logout: vi.fn(),
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    render(<DashboardPage />, { wrapper });

    expect(screen.getByText(/Non disponible/i)).toBeInTheDocument();
  });
});

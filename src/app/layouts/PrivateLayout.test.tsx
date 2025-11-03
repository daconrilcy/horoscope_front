import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PrivateLayout } from './PrivateLayout';
import { ROUTES } from '@/shared/config/routes';
import { useAuthStore } from '@/stores/authStore';
import React from 'react';

const mockNavigate = vi.fn();
const mockQueryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

// Mock pour Outlet et useNavigate
vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>(
      'react-router-dom'
    );
  return {
    ...actual,
    Outlet: (): JSX.Element => <div data-testid="outlet">Outlet Content</div>,
    useNavigate: (): typeof mockNavigate => mockNavigate,
  };
});

// Mock pour useQueryClient
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual<typeof import('@tanstack/react-query')>(
    '@tanstack/react-query'
  );
  return {
    ...actual,
    useQueryClient: (): QueryClient => mockQueryClient,
  };
});

// Mock pour les hooks billing
vi.mock('@/features/billing/hooks/useCheckout', () => ({
  useCheckout: (): {
    startCheckout: ReturnType<typeof vi.fn>;
    isPending: boolean;
    error: Error | null;
  } => ({
    startCheckout: vi.fn(),
    isPending: false,
    error: null,
  }),
}));

vi.mock('@/features/billing/hooks/usePortal', () => ({
  usePortal: (): {
    openPortal: ReturnType<typeof vi.fn>;
    isPending: boolean;
    error: Error | null;
  } => ({
    openPortal: vi.fn(),
    isPending: false,
    error: null,
  }),
}));

// Mock pour useAuthStore
const mockAuthStoreState: {
  token: string | null;
  hasHydrated: boolean;
  logout: ReturnType<typeof vi.fn>;
  getToken: () => string | null;
} = {
  token: 'test-token',
  hasHydrated: true,
  logout: vi.fn(),
  getToken: () => mockAuthStoreState.token,
};

vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(
    (selector: (state: typeof mockAuthStoreState) => unknown) => {
      if (typeof selector === 'function') {
        return selector(mockAuthStoreState);
      }
      return selector;
    }
  ),
}));

const wrapper = ({ children }: { children: React.ReactNode }): JSX.Element => (
  <QueryClientProvider client={mockQueryClient}>
    <MemoryRouter>{children}</MemoryRouter>
  </QueryClientProvider>
);

describe('PrivateLayout', () => {
  beforeEach(() => {
    // Reset store
    mockAuthStoreState.token = 'test-token';
    mockAuthStoreState.hasHydrated = true;
    mockAuthStoreState.logout = vi.fn();
    vi.clearAllMocks();
    mockNavigate.mockClear();
    (useAuthStore as ReturnType<typeof vi.fn>).mockImplementation(
      (selector: (state: typeof mockAuthStoreState) => unknown) => {
        if (typeof selector === 'function') {
          return selector(mockAuthStoreState);
        }
        return selector;
      }
    );
  });

  it('devrait afficher la navigation avec Dashboard', () => {
    render(<PrivateLayout />, { wrapper });

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Déconnexion')).toBeInTheDocument();
  });

  it('devrait afficher Outlet', () => {
    render(<PrivateLayout />, { wrapper });

    expect(screen.getByTestId('outlet')).toBeInTheDocument();
  });

  it('devrait avoir un lien vers Dashboard', () => {
    render(<PrivateLayout />, { wrapper });

    const dashboardLink = screen.getByText('Dashboard').closest('a');
    expect(dashboardLink).toHaveAttribute('href', ROUTES.APP.DASHBOARD);
  });

  it('devrait appeler logout et navigate au clic sur Déconnexion', () => {
    const logout = vi.fn();
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    mockAuthStoreState.logout = logout;

    render(<PrivateLayout />, { wrapper });

    const logoutButton = screen.getByText('Déconnexion');
    logoutButton.click();

    expect(logout).toHaveBeenCalledWith(mockQueryClient);
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.LOGIN, { replace: true });
  });
});

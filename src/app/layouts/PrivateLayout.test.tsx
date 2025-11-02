import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { PrivateLayout } from './PrivateLayout';
import { ROUTES } from '@/shared/config/routes';
import { useAuthStore } from '@/stores/authStore';
import { QueryClient } from '@tanstack/react-query';

const mockNavigate = vi.fn();
const mockQueryClient = new QueryClient();

// Mock pour Outlet et useNavigate
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    Outlet: (): JSX.Element => <div data-testid="outlet">Outlet Content</div>,
    useNavigate: (): typeof mockNavigate => mockNavigate,
  };
});

// Mock pour useQueryClient
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual<typeof import('@tanstack/react-query')>('@tanstack/react-query');
  return {
    ...actual,
    useQueryClient: () => mockQueryClient,
  };
});

describe('PrivateLayout', () => {
  beforeEach(() => {
    // Reset store
    useAuthStore.setState({ token: 'test-token', hasHydrated: true });
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('devrait afficher la navigation avec Dashboard', () => {
    render(
      <MemoryRouter>
        <PrivateLayout />
      </MemoryRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Déconnexion')).toBeInTheDocument();
  });

  it('devrait afficher Outlet', () => {
    render(
      <MemoryRouter>
        <PrivateLayout />
      </MemoryRouter>
    );

    expect(screen.getByTestId('outlet')).toBeInTheDocument();
  });

  it('devrait avoir un lien vers Dashboard', () => {
    render(
      <MemoryRouter>
        <PrivateLayout />
      </MemoryRouter>
    );

    const dashboardLink = screen.getByText('Dashboard').closest('a');
    expect(dashboardLink).toHaveAttribute('href', ROUTES.APP.DASHBOARD);
  });

  it('devrait appeler logout et navigate au clic sur Déconnexion', () => {
    const logout = vi.fn();
    useAuthStore.setState({ logout });

    render(
      <MemoryRouter>
        <PrivateLayout />
      </MemoryRouter>
    );

    const logoutButton = screen.getByText('Déconnexion');
    logoutButton.click();

    expect(logout).toHaveBeenCalledWith(mockQueryClient);
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.LOGIN, { replace: true });
  });
});


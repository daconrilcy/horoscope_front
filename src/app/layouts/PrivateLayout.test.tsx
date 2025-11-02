import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { PrivateLayout } from './PrivateLayout';
import { ROUTES } from '@/shared/config/routes';
import { useAuthStore } from '@/stores/authStore';

const mockNavigate = vi.fn();

// Mock pour Outlet et useNavigate
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    Outlet: (): JSX.Element => <div data-testid="outlet">Outlet Content</div>,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-return
    useNavigate: () => mockNavigate,
  };
});

describe('PrivateLayout', () => {
  beforeEach(() => {
    // Reset store
    useAuthStore.setState({ token: 'test-token', _hasHydrated: true });
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

  it('devrait appeler clearToken et navigate au clic sur Déconnexion', () => {
    const clearToken = vi.fn();
    useAuthStore.setState({ clearToken });

    render(
      <MemoryRouter>
        <PrivateLayout />
      </MemoryRouter>
    );

    const logoutButton = screen.getByText('Déconnexion');
    logoutButton.click();

    expect(clearToken).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.LOGIN, { replace: true });
  });
});


import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { HomePage } from './index';
import { useAuthStore } from '@/stores/authStore';
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

// Mock useAuthStore
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

describe('HomePage', () => {
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

  it('devrait afficher les CTA signup/login si non authentifié', () => {
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        token: null,
        hasHydrated: true,
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    render(<HomePage />, { wrapper });

    expect(screen.getByText("S'inscrire")).toBeInTheDocument();
    expect(screen.getByText('Se connecter')).toBeInTheDocument();
    expect(
      screen.getByText('Horoscope & Conseils Personnalisés')
    ).toBeInTheDocument();
  });

  it('devrait rediriger vers dashboard si authentifié (après hydratation)', async () => {
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        token: 'test-token',
        hasHydrated: true,
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    render(<HomePage />, { wrapper });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(ROUTES.APP.DASHBOARD, {
        replace: true,
      });
    });
  });

  it('ne devrait pas rediriger si hasHydrated est false', () => {
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        token: 'test-token',
        hasHydrated: false,
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    render(<HomePage />, { wrapper });

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('devrait afficher les liens légaux', () => {
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        token: null,
        hasHydrated: true,
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    render(<HomePage />, { wrapper });

    const tosLink = screen.getByRole('link', {
      name: /conditions d'utilisation/i,
    });
    expect(tosLink).toBeInTheDocument();
    expect(tosLink).toHaveAttribute('href', ROUTES.LEGAL.TOS);

    const privacyLink = screen.getByRole('link', {
      name: /politique de confidentialité/i,
    });
    expect(privacyLink).toBeInTheDocument();
    expect(privacyLink).toHaveAttribute('href', ROUTES.LEGAL.PRIVACY);
  });

  it('devrait avoir les bons aria-labels pour accessibilité', () => {
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        token: null,
        hasHydrated: true,
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    render(<HomePage />, { wrapper });

    const signupLink = screen.getByRole('link', {
      name: /s'inscrire pour créer un compte/i,
    });
    expect(signupLink).toBeInTheDocument();

    const loginLink = screen.getByRole('link', {
      name: /se connecter à votre compte/i,
    });
    expect(loginLink).toBeInTheDocument();
  });

  it('devrait utiliser le tag main pour la structure', () => {
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        token: null,
        hasHydrated: true,
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    render(<HomePage />, { wrapper });

    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
  });

  it('ne devrait pas afficher de contenu si en cours d hydratation et authentifié', () => {
    vi.mocked(useAuthStore).mockImplementation((selector) => {
      const mockState = {
        token: 'test-token',
        hasHydrated: false,
      };
      return selector(mockState as ReturnType<typeof useAuthStore>);
    });

    const { container } = render(<HomePage />, { wrapper });

    expect(screen.queryByText("S'inscrire")).not.toBeInTheDocument();
    expect(container.querySelector('[aria-busy="true"]')).toBeInTheDocument();
  });
});

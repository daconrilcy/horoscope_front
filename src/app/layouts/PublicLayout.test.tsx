import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { PublicLayout } from './PublicLayout';
import { ROUTES } from '@/shared/config/routes';

// Mock pour Outlet
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    Outlet: () => <div data-testid="outlet">Outlet Content</div>,
  };
});

describe('PublicLayout', () => {
  it('devrait afficher la navigation', () => {
    render(
      <MemoryRouter>
        <PublicLayout />
      </MemoryRouter>
    );

    expect(screen.getByText('Accueil')).toBeInTheDocument();
    expect(screen.getByText('Connexion')).toBeInTheDocument();
    expect(screen.getByText('Inscription')).toBeInTheDocument();
  });

  it('devrait afficher Outlet', () => {
    render(
      <MemoryRouter>
        <PublicLayout />
      </MemoryRouter>
    );

    expect(screen.getByTestId('outlet')).toBeInTheDocument();
  });

  it('devrait avoir des liens vers les routes publiques', () => {
    render(
      <MemoryRouter>
        <PublicLayout />
      </MemoryRouter>
    );

    const homeLink = screen.getByText('Accueil').closest('a');
    const loginLink = screen.getByText('Connexion').closest('a');
    const signupLink = screen.getByText('Inscription').closest('a');

    expect(homeLink).toHaveAttribute('href', ROUTES.HOME);
    expect(loginLink).toHaveAttribute('href', ROUTES.LOGIN);
    expect(signupLink).toHaveAttribute('href', ROUTES.SIGNUP);
  });
});


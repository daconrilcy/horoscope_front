import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { BillingCancelPage } from './index';
import { ROUTES } from '@/shared/config/routes';
import React from 'react';

describe('BillingCancelPage', () => {
  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => <BrowserRouter>{children}</BrowserRouter>;

  it("devrait afficher le titre et le message d'annulation", () => {
    render(<BillingCancelPage />, { wrapper });

    expect(screen.getByText('Paiement annulé')).toBeInTheDocument();
    expect(
      screen.getByText('Vous avez annulé le processus de paiement.')
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Aucun paiement n'a été effectué. Vous pouvez réessayer à tout moment."
      )
    ).toBeInTheDocument();
  });

  it('devrait afficher le lien vers le tableau de bord', () => {
    render(<BillingCancelPage />, { wrapper });

    const dashboardLink = screen.getByRole('link', {
      name: /retour au tableau de bord/i,
    });
    expect(dashboardLink).toBeInTheDocument();
    expect(dashboardLink).toHaveAttribute('href', ROUTES.APP.DASHBOARD);
  });

  it('devrait afficher le lien vers la gestion de compte', () => {
    render(<BillingCancelPage />, { wrapper });

    const accountLink = screen.getByRole('link', {
      name: /gérer mon abonnement/i,
    });
    expect(accountLink).toBeInTheDocument();
    expect(accountLink).toHaveAttribute('href', ROUTES.APP.ACCOUNT);
  });

  it('devrait utiliser le tag main pour la structure', () => {
    render(<BillingCancelPage />, { wrapper });

    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
  });
});

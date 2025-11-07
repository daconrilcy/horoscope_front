import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { BillingSuccessPage } from './index';
import { billingService } from '@/shared/api/billing.service';
import { ApiError } from '@/shared/api/errors';
import React from 'react';

// Mock billingService
vi.mock('@/shared/api/billing.service', () => ({
  billingService: {
    verifyCheckoutSession: vi.fn(),
  },
}));

// Mock useSearchParams
let mockSearchParams: URLSearchParams;
let mockSetSearchParams: ReturnType<typeof vi.fn>;
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useSearchParams: (): [URLSearchParams, ReturnType<typeof vi.fn>] => [
      mockSearchParams,
      mockSetSearchParams,
    ],
  };
});

describe('BillingSuccessPage', () => {
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
    mockSearchParams = new URLSearchParams();
    mockSetSearchParams = vi.fn();
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

  it('devrait afficher une erreur si session_id est manquant', () => {
    render(<BillingSuccessPage />, { wrapper });

    expect(screen.getByText('Erreur')).toBeInTheDocument();
    expect(
      screen.getByText("Aucun identifiant de session trouvé dans l'URL.")
    ).toBeInTheDocument();
  });

  it('devrait afficher "Validation en cours..." pendant le chargement', () => {
    mockSearchParams.set('session_id', 'test-session-id');
    (
      billingService.verifyCheckoutSession as ReturnType<typeof vi.fn>
    ).mockImplementation(
      () => new Promise(() => {}) // Promise qui ne se résout jamais
    );

    render(<BillingSuccessPage />, { wrapper });

    expect(screen.getByText('Validation en cours...')).toBeInTheDocument();
    expect(
      screen.getByText('Vérification de votre paiement...')
    ).toBeInTheDocument();
  });

  it('devrait afficher un message de succès si le paiement est réussi', async () => {
    mockSearchParams.set('session_id', 'test-session-id');
    (
      billingService.verifyCheckoutSession as ReturnType<typeof vi.fn>
    ).mockResolvedValue({
      status: 'paid',
      session_id: 'test-session-id',
      plan: 'plus',
    });

    render(<BillingSuccessPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Paiement réussi !')).toBeInTheDocument();
    });

    expect(
      screen.getByText('Votre abonnement a été activé avec succès.')
    ).toBeInTheDocument();
    expect(screen.getByText('Plan :')).toBeInTheDocument();
    expect(screen.getByText('plus')).toBeInTheDocument();
  });

  it("devrait afficher un message d'erreur si la session est introuvable (404)", async () => {
    mockSearchParams.set('session_id', 'test-session-id');
    (
      billingService.verifyCheckoutSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(new ApiError('Session introuvable', 404));

    render(<BillingSuccessPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Erreur de validation')).toBeInTheDocument();
    });

    expect(
      screen.getByText('Session introuvable ou expirée.')
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /réessayer/i })
    ).toBeInTheDocument();
  });

  it("devrait afficher un message d'erreur si la session a expiré (401)", async () => {
    mockSearchParams.set('session_id', 'test-session-id');
    (
      billingService.verifyCheckoutSession as ReturnType<typeof vi.fn>
    ).mockRejectedValue(new ApiError('Session expirée', 401));

    render(<BillingSuccessPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Erreur de validation')).toBeInTheDocument();
    });

    expect(
      screen.getByText('Session expirée. Veuillez vous reconnecter.')
    ).toBeInTheDocument();
  });

  it("devrait permettre de réessayer la validation en cas d'erreur", async () => {
    mockSearchParams.set('session_id', 'test-session-id');
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockVerify = billingService.verifyCheckoutSession as ReturnType<
      typeof vi.fn
    >;
    // Premier appel échoue avec erreur générique (pas 401/404)
    mockVerify.mockRejectedValueOnce(new ApiError('Erreur réseau', 500));

    render(<BillingSuccessPage />, { wrapper });

    // Attendre l'erreur initiale
    await waitFor(() => {
      expect(screen.getByText('Erreur de validation')).toBeInTheDocument();
    });

    // Vérifier que le premier appel a été fait
    expect(mockVerify).toHaveBeenCalledTimes(1);

    // Vérifier que le bouton de retry existe et est cliquable
    const retryButton = screen.getByRole('button', { name: /réessayer/i });
    expect(retryButton).toBeInTheDocument();
    expect(retryButton).not.toBeDisabled();
  });

  it('devrait afficher un message si le statut est unpaid', async () => {
    mockSearchParams.set('session_id', 'test-session-id');
    (
      billingService.verifyCheckoutSession as ReturnType<typeof vi.fn>
    ).mockResolvedValue({
      status: 'unpaid',
      session_id: 'test-session-id',
    });

    render(<BillingSuccessPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Paiement non finalisé')).toBeInTheDocument();
    });

    expect(
      screen.getByText("Le paiement n'a pas été finalisé.")
    ).toBeInTheDocument();
  });

  it('devrait afficher un message si le statut est expired', async () => {
    mockSearchParams.set('session_id', 'test-session-id');
    (
      billingService.verifyCheckoutSession as ReturnType<typeof vi.fn>
    ).mockResolvedValue({
      status: 'expired',
      session_id: 'test-session-id',
    });

    render(<BillingSuccessPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Paiement non finalisé')).toBeInTheDocument();
    });

    expect(
      screen.getByText('La session de paiement a expiré.')
    ).toBeInTheDocument();
  });

  it('devrait invalider les queries plan/billing après succès', async () => {
    mockSearchParams.set('session_id', 'test-session-id');
    (
      billingService.verifyCheckoutSession as ReturnType<typeof vi.fn>
    ).mockResolvedValue({
      status: 'paid',
      session_id: 'test-session-id',
    });

    const invalidateQueriesSpy = vi.spyOn(queryClient, 'invalidateQueries');

    render(<BillingSuccessPage />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Paiement réussi !')).toBeInTheDocument();
    });

    // Vérifier que les queries sont invalidées
    expect(invalidateQueriesSpy).toHaveBeenCalledWith({
      queryKey: ['plan'],
    });
    expect(invalidateQueriesSpy).toHaveBeenCalledWith({
      queryKey: ['billing'],
    });
    expect(invalidateQueriesSpy).toHaveBeenCalledWith({
      queryKey: ['paywall'],
    });
  });
});

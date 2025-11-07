/* eslint-disable @typescript-eslint/unbound-method */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { DevTerminalConsole } from './DevTerminalConsole';
import {
  terminalService,
  TERMINAL_TEST_AMOUNTS,
  TERMINAL_TEST_CARDS,
} from '@/shared/api/terminal.service';
import React from 'react';

// Mock terminalService
vi.mock('@/shared/api/terminal.service', () => ({
  terminalService: {
    connect: vi.fn<() => Promise<{ connection_token: string }>>(),
    createPaymentIntent:
      vi.fn<
        () => Promise<{ client_secret: string; payment_intent_id: string }>
      >(),
    process:
      vi.fn<
        () => Promise<{
          status: string;
          payment_intent_id: string;
          error_code?: string;
          error_message?: string;
        }>
      >(),
    capture:
      vi.fn<() => Promise<{ status: string; payment_intent_id: string }>>(),
    cancel:
      vi.fn<() => Promise<{ status: string; payment_intent_id: string }>>(),
    refund:
      vi.fn<
        () => Promise<{ refund_id: string; amount: number; status: string }>
      >(),
  },
  TERMINAL_TEST_AMOUNTS: {
    SUCCESS: 100,
    SUCCESS_01: 101,
    SUCCESS_02: 102,
    DECLINED: 200,
  },
  TERMINAL_TEST_CARDS: {
    SUCCESS: '4242424242424242',
    DECLINED: '4000000000000002',
  },
}));

// Mock toast
vi.mock('@/app/AppProviders', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

// Mock import.meta.env.DEV
vi.mock('import.meta', () => ({
  env: {
    DEV: true,
  },
}));

describe('DevTerminalConsole', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
        mutations: {
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
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );

  it('devrait afficher l\'état initial "disconnected"', () => {
    render(<DevTerminalConsole />, { wrapper });

    expect(screen.getByText(/État: disconnected/i)).toBeInTheDocument();
  });

  it('devrait connecter le terminal au clic sur "Connecter Terminal"', async () => {
    const user = userEvent.setup();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockConnect = vi.mocked(terminalService.connect);
    (mockConnect as ReturnType<typeof vi.fn>).mockResolvedValue({
      connection_token: 'tok_test_123',
    });

    render(<DevTerminalConsole />, { wrapper });

    const connectButton = screen.getByRole('button', {
      name: /connecter terminal/i,
    });
    await user.click(connectButton);

    await waitFor(() => {
      expect(mockConnect).toHaveBeenCalledTimes(1);
    });
    expect(screen.getByText(/État: connected/i)).toBeInTheDocument();
  });

  it('devrait créer un PaymentIntent après connexion', async () => {
    const user = userEvent.setup();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockConnect = vi.mocked(terminalService.connect);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockCreateIntent = vi.mocked(terminalService.createPaymentIntent);
    mockConnect.mockResolvedValue({
      connection_token: 'tok_test_123',
    });
    mockCreateIntent.mockResolvedValue({
      client_secret: 'pi_secret_123',
      payment_intent_id: 'pi_test_123',
    });

    render(<DevTerminalConsole />, { wrapper });

    // Connecter
    const connectButton = screen.getByRole('button', {
      name: /connecter terminal/i,
    });
    await user.click(connectButton);

    await waitFor(() => {
      expect(screen.getByText(/État: connected/i)).toBeInTheDocument();
    });

    // Créer PaymentIntent
    const createIntentButton = screen.getByRole('button', {
      name: /créer paymentintent/i,
    });
    await user.click(createIntentButton);

    await waitFor(() => {
      expect(mockCreateIntent).toHaveBeenCalledWith({
        amount: TERMINAL_TEST_AMOUNTS.SUCCESS,
        currency: 'eur',
        payment_method_types: ['card_present'],
      });
    });
    expect(screen.getByText(/État: intent_created/i)).toBeInTheDocument();
  });

  it('devrait traiter un paiement après création de PaymentIntent', async () => {
    const user = userEvent.setup();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockConnect = vi.mocked(terminalService.connect);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockCreateIntent = vi.mocked(terminalService.createPaymentIntent);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockProcess = vi.mocked(terminalService.process);
    mockConnect.mockResolvedValue({
      connection_token: 'tok_test_123',
    });
    mockCreateIntent.mockResolvedValue({
      client_secret: 'pi_secret_123',
      payment_intent_id: 'pi_test_123',
    });
    mockProcess.mockResolvedValue({
      status: 'succeeded',
      payment_intent_id: 'pi_test_123',
    });

    render(<DevTerminalConsole />, { wrapper });

    // Connecter
    await user.click(
      screen.getByRole('button', { name: /connecter terminal/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: connected/i)).toBeInTheDocument();
    });

    // Créer PaymentIntent
    await user.click(
      screen.getByRole('button', { name: /créer paymentintent/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: intent_created/i)).toBeInTheDocument();
    });

    // Traiter
    const processButton = screen.getByRole('button', {
      name: /traiter paiement/i,
    });
    await user.click(processButton);

    await waitFor(() => {
      expect(mockProcess).toHaveBeenCalledWith({
        payment_intent_id: 'pi_test_123',
        payment_method: TERMINAL_TEST_CARDS.SUCCESS,
      });
    });
    expect(screen.getByText(/État: captured/i)).toBeInTheDocument();
  });

  it('devrait capturer un paiement en état "processing"', async () => {
    const user = userEvent.setup();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockConnect = vi.mocked(terminalService.connect);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockCreateIntent = vi.mocked(terminalService.createPaymentIntent);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockProcess = vi.mocked(terminalService.process);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockCapture = vi.mocked(terminalService.capture);
    mockConnect.mockResolvedValue({
      connection_token: 'tok_test_123',
    });
    mockCreateIntent.mockResolvedValue({
      client_secret: 'pi_secret_123',
      payment_intent_id: 'pi_test_123',
    });
    mockProcess.mockResolvedValue({
      status: 'requires_action',
      payment_intent_id: 'pi_test_123',
    });
    mockCapture.mockResolvedValue({
      status: 'succeeded',
      payment_intent_id: 'pi_test_123',
    });

    render(<DevTerminalConsole />, { wrapper });

    // Connecter → Créer → Traiter (état processing)
    await user.click(
      screen.getByRole('button', { name: /connecter terminal/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: connected/i)).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole('button', { name: /créer paymentintent/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: intent_created/i)).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /traiter paiement/i }));
    await waitFor(() => {
      expect(screen.getByText(/État: processing/i)).toBeInTheDocument();
    });

    // Capturer
    const captureButton = screen.getByRole('button', { name: /capturer/i });
    await user.click(captureButton);

    await waitFor(() => {
      expect(mockCapture).toHaveBeenCalledWith({
        payment_intent_id: 'pi_test_123',
      });
    });
    expect(screen.getByText(/État: captured/i)).toBeInTheDocument();
  });

  it('devrait annuler un PaymentIntent', async () => {
    const user = userEvent.setup();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockConnect = vi.mocked(terminalService.connect);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockCreateIntent = vi.mocked(terminalService.createPaymentIntent);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockCancel = vi.mocked(terminalService.cancel);
    mockConnect.mockResolvedValue({
      connection_token: 'tok_test_123',
    });
    mockCreateIntent.mockResolvedValue({
      client_secret: 'pi_secret_123',
      payment_intent_id: 'pi_test_123',
    });
    mockCancel.mockResolvedValue({
      status: 'canceled',
      payment_intent_id: 'pi_test_123',
    });

    render(<DevTerminalConsole />, { wrapper });

    // Connecter → Créer
    await user.click(
      screen.getByRole('button', { name: /connecter terminal/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: connected/i)).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole('button', { name: /créer paymentintent/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: intent_created/i)).toBeInTheDocument();
    });

    // Annuler
    const cancelButton = screen.getByRole('button', { name: /annuler/i });
    await user.click(cancelButton);

    await waitFor(() => {
      expect(mockCancel).toHaveBeenCalledWith({
        payment_intent_id: 'pi_test_123',
      });
    });
    expect(screen.getByText(/État: canceled/i)).toBeInTheDocument();
  });

  it('devrait rembourser un paiement capturé', async () => {
    const user = userEvent.setup();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockConnect = vi.mocked(terminalService.connect);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockCreateIntent = vi.mocked(terminalService.createPaymentIntent);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockProcess = vi.mocked(terminalService.process);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockRefund = vi.mocked(terminalService.refund);
    mockConnect.mockResolvedValue({
      connection_token: 'tok_test_123',
    });
    mockCreateIntent.mockResolvedValue({
      client_secret: 'pi_secret_123',
      payment_intent_id: 'pi_test_123',
    });
    mockProcess.mockResolvedValue({
      status: 'succeeded',
      payment_intent_id: 'pi_test_123',
    });
    mockRefund.mockResolvedValue({
      refund_id: 're_test_123',
      amount: 100,
      status: 'succeeded',
    });

    render(<DevTerminalConsole />, { wrapper });

    // Connecter → Créer → Traiter (captured)
    await user.click(
      screen.getByRole('button', { name: /connecter terminal/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: connected/i)).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole('button', { name: /créer paymentintent/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: intent_created/i)).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /traiter paiement/i }));
    await waitFor(() => {
      expect(screen.getByText(/État: captured/i)).toBeInTheDocument();
    });

    // Rembourser
    const refundButton = screen.getByRole('button', { name: /rembourser/i });
    await user.click(refundButton);

    await waitFor(() => {
      expect(mockRefund).toHaveBeenCalledWith({
        payment_intent_id: 'pi_test_123',
      });
    });
    expect(screen.getByText(/État: refunded/i)).toBeInTheDocument();
  });

  it('devrait gérer les erreurs de paiement (carte refusée)', async () => {
    const user = userEvent.setup();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockConnect = vi.mocked(terminalService.connect);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockCreateIntent = vi.mocked(terminalService.createPaymentIntent);
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockProcess = vi.mocked(terminalService.process);
    mockConnect.mockResolvedValue({
      connection_token: 'tok_test_123',
    });
    mockCreateIntent.mockResolvedValue({
      client_secret: 'pi_secret_123',
      payment_intent_id: 'pi_test_123',
    });
    mockProcess.mockResolvedValue({
      status: 'requires_payment_method',
      payment_intent_id: 'pi_test_123',
      error_code: 'card_declined',
      error_message: 'Your card was declined.',
    });

    render(<DevTerminalConsole />, { wrapper });

    // Connecter → Créer → Traiter (échec)
    await user.click(
      screen.getByRole('button', { name: /connecter terminal/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: connected/i)).toBeInTheDocument();
    });

    await user.click(
      screen.getByRole('button', { name: /créer paymentintent/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: intent_created/i)).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /traiter paiement/i }));

    await waitFor(() => {
      expect(screen.getByText(/État: failed/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/Your card was declined/i)).toBeInTheDocument();
  });

  it("devrait permettre de réinitialiser l'état", async () => {
    const user = userEvent.setup();
    const mockConnect = vi.mocked(terminalService.connect);
    mockConnect.mockResolvedValue({
      connection_token: 'tok_test_123',
    });

    render(<DevTerminalConsole />, { wrapper });

    // Connecter
    await user.click(
      screen.getByRole('button', { name: /connecter terminal/i })
    );
    await waitFor(() => {
      expect(screen.getByText(/État: connected/i)).toBeInTheDocument();
    });

    // Reset
    const resetButton = screen.getByRole('button', { name: /reset/i });
    await user.click(resetButton);

    expect(screen.getByText(/État: disconnected/i)).toBeInTheDocument();
  });

  it('devrait permettre de sélectionner différents montants de test', async () => {
    const user = userEvent.setup();
    render(<DevTerminalConsole />, { wrapper });

    const amountSelect = screen.getByLabelText(/montant/i);
    expect(amountSelect).toBeInTheDocument();

    // Changer le montant
    await user.selectOptions(
      amountSelect,
      String(TERMINAL_TEST_AMOUNTS.DECLINED)
    );

    expect((amountSelect as HTMLSelectElement).value).toBe(
      String(TERMINAL_TEST_AMOUNTS.DECLINED)
    );
  });

  it('devrait permettre de sélectionner différentes cartes de test', async () => {
    const user = userEvent.setup();
    render(<DevTerminalConsole />, { wrapper });

    const cardSelect = screen.getByLabelText(/carte de test/i);
    expect(cardSelect).toBeInTheDocument();

    // Changer la carte
    await user.selectOptions(cardSelect, TERMINAL_TEST_CARDS.DECLINED);

    expect((cardSelect as HTMLSelectElement).value).toBe(
      TERMINAL_TEST_CARDS.DECLINED
    );
  });
});

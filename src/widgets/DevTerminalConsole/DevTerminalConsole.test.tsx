/* eslint-disable @typescript-eslint/unbound-method */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DevTerminalConsole } from './DevTerminalConsole';
import { terminalService } from '@/shared/api/terminal.service';
import { eventBus } from '@/shared/api/eventBus';
import { actUser } from '@/test/utils/actUser';

// Mock terminalService
vi.mock('@/shared/api/terminal.service', () => ({
  terminalService: {
    connect: vi.fn(),
    createPaymentIntent: vi.fn(),
    process: vi.fn(),
    capture: vi.fn(),
    cancel: vi.fn(),
    refund: vi.fn(),
  },
}));

// Mock eventBus
vi.mock('@/shared/api/eventBus', () => ({
  eventBus: {
    emit: vi.fn(),
  },
}));

const mockedTerminalService = vi.mocked(terminalService);
const mockedEventBus = vi.mocked(eventBus);

describe('DevTerminalConsole', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('devrait afficher le titre en mode dev', () => {
    render(<DevTerminalConsole />);
    expect(
      screen.getByText('🔧 Stripe Terminal Simulator (DEV)')
    ).toBeInTheDocument();
  });

  it("devrait afficher l'état idle initial", () => {
    render(<DevTerminalConsole />);
    expect(screen.getByText(/État:/)).toBeInTheDocument();
    expect(screen.getByText(/🟢 Idle/)).toBeInTheDocument();
  });

  it('devrait afficher le bouton Connect initialement', () => {
    render(<DevTerminalConsole />);
    expect(screen.getByText('Connect to Terminal')).toBeInTheDocument();
  });

  it("devrait appeler connect et mettre à jour l'état", async () => {
    const mockConnection = {
      connection_token: 'pst_test_1234567890',
      terminal_id: 'tmr_test_123',
    };

    mockedTerminalService.connect.mockResolvedValue(mockConnection);

    render(<DevTerminalConsole />);

    const connectButton = screen.getByText('Connect to Terminal');
    await actUser(() => userEvent.click(connectButton));

    await waitFor(() => {
      expect(mockedTerminalService.connect).toHaveBeenCalled();
      expect(mockedEventBus.emit).toHaveBeenCalledWith('terminal:connect', {});
    });

    await waitFor(() => {
      expect(screen.getByText(/Terminal ID:/)).toBeInTheDocument();
      expect(screen.getByText(/tmr_test_123/)).toBeInTheDocument();
    });
  });

  it('devrait créer un payment intent après connexion', async () => {
    const mockConnection = {
      connection_token: 'pst_test_123',
      terminal_id: 'tmr_test_123',
    };

    const mockPaymentIntent = {
      payment_intent_id: 'pi_test_123',
      amount: 1000,
      currency: 'eur',
      status: 'requires_payment_method',
    };

    mockedTerminalService.connect.mockResolvedValue(mockConnection);
    mockedTerminalService.createPaymentIntent.mockResolvedValue(
      mockPaymentIntent
    );

    render(<DevTerminalConsole />);

    // Connecter
    const connectButton = screen.getByText('Connect to Terminal');
    await actUser(() => userEvent.click(connectButton));

    await waitFor(() => {
      expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
    });

    // Créer Payment Intent
    const createButton = screen.getByText('Create Payment Intent');
    await actUser(() => userEvent.click(createButton));

    await waitFor(() => {
      expect(mockedTerminalService.createPaymentIntent).toHaveBeenCalledWith(
        1000,
        'eur'
      );
      expect(mockedEventBus.emit).toHaveBeenCalledWith(
        'terminal:payment_intent',
        {
          amount: 1000,
          currency: 'eur',
        }
      );
    });
  });

  it('devrait afficher une erreur si la connexion échoue', async () => {
    mockedTerminalService.connect.mockRejectedValue(
      new Error('Connection failed')
    );

    render(<DevTerminalConsole />);

    const connectButton = screen.getByText('Connect to Terminal');
    await actUser(() => userEvent.click(connectButton));

    await waitFor(() => {
      expect(screen.getByText(/🔴 Error/)).toBeInTheDocument();
      expect(screen.getByText(/Connection failed/)).toBeInTheDocument();
    });
  });

  it('devrait désactiver les boutons pendant le traitement', async () => {
    let resolveConnect: (value: unknown) => void;
    const connectPromise = new Promise<unknown>((resolve) => {
      resolveConnect = resolve;
    });

    mockedTerminalService.connect.mockImplementation(() => connectPromise);

    render(<DevTerminalConsole />);

    const connectButton = screen.getByText('Connect to Terminal');
    expect(connectButton).not.toBeDisabled();

    await actUser(() => userEvent.click(connectButton));

    // Attendre que le bouton soit désactivé (état connecting)
    await waitFor(() => {
      expect(connectButton).toBeDisabled();
    });

    // Résoudre la promesse
    resolveConnect!({
      connection_token: 'pst_test_123',
      terminal_id: 'tmr_test_123',
    });

    // Attendre que l'état change vers 'connected' (le bouton reste désactivé car state.type !== 'idle')
    await waitFor(
      () => {
        expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
      },
      { timeout: 2000 }
    );

    // Le bouton Connect reste désactivé car on est dans l'état 'connected', pas 'idle'
    // C'est le comportement attendu selon la logique du composant
    expect(connectButton).toBeDisabled();
  });

  describe('Stripe Terminal Test Scenarios', () => {
    /**
     * Tests conformes à la documentation Stripe Terminal
     * https://docs.stripe.com/terminal/references/testing
     */

    it('devrait gérer un paiement avec montant approuvé (25.00 EUR)', async () => {
      const mockConnection = {
        connection_token: 'pst_test_123',
        terminal_id: 'tmr_test_123',
      };

      const mockPaymentIntent = {
        payment_intent_id: 'pi_test_approved',
        amount: 2500, // 25.00 EUR - montant approuvé selon Stripe docs
        currency: 'eur',
        status: 'requires_payment_method',
      };

      const mockProcessResponse = {
        payment_intent_id: 'pi_test_approved',
        status: 'succeeded',
      };

      mockedTerminalService.connect.mockResolvedValue(mockConnection);
      mockedTerminalService.createPaymentIntent.mockResolvedValue(
        mockPaymentIntent
      );
      mockedTerminalService.process.mockResolvedValue(mockProcessResponse);

      render(<DevTerminalConsole />);

      // Connecter
      const connectButton = screen.getByText('Connect to Terminal');
      await actUser(() => userEvent.click(connectButton));

      await waitFor(() => {
        expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
      });

      // Créer Payment Intent avec montant approuvé
      const amountInput = screen.getByDisplayValue('1000');
      await actUser(() => userEvent.clear(amountInput));
      await actUser(() => userEvent.type(amountInput, '2500'));
      const createButton = screen.getByText('Create Payment Intent');
      await actUser(() => userEvent.click(createButton));

      await waitFor(() => {
        expect(mockedTerminalService.createPaymentIntent).toHaveBeenCalledWith(
          2500,
          'eur'
        );
      });

      // Traiter le paiement
      const processButton = screen.getByText('Process Payment');
      await actUser(() => userEvent.click(processButton));

      await waitFor(() => {
        expect(mockedTerminalService.process).toHaveBeenCalledWith(
          'pi_test_approved'
        );
      });

      await waitFor(() => {
        expect(screen.getByText(/Processed|succeeded/i)).toBeInTheDocument();
      });
    });

    it('devrait gérer un paiement refusé (10.01 EUR - call_issuer)', async () => {
      const mockConnection = {
        connection_token: 'pst_test_123',
        terminal_id: 'tmr_test_123',
      };

      const mockPaymentIntent = {
        payment_intent_id: 'pi_test_declined',
        amount: 1001, // 10.01 EUR - montant refusé selon Stripe docs
        currency: 'eur',
        status: 'requires_payment_method',
      };

      mockedTerminalService.connect.mockResolvedValue(mockConnection);
      mockedTerminalService.createPaymentIntent.mockResolvedValue(
        mockPaymentIntent
      );
      mockedTerminalService.process.mockRejectedValue(
        new Error('Your card was declined.')
      );

      render(<DevTerminalConsole />);

      // Connecter
      const connectButton = screen.getByText('Connect to Terminal');
      await actUser(() => userEvent.click(connectButton));

      await waitFor(() => {
        expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
      });

      // Créer Payment Intent avec montant refusé
      const amountInput = screen.getByDisplayValue('1000');
      await actUser(() => userEvent.clear(amountInput));
      await actUser(() => userEvent.type(amountInput, '1001'));
      const createButton = screen.getByText('Create Payment Intent');
      await actUser(() => userEvent.click(createButton));

      await waitFor(() => {
        expect(mockedTerminalService.createPaymentIntent).toHaveBeenCalledWith(
          1001,
          'eur'
        );
      });

      // Traiter le paiement (devrait échouer)
      const processButton = screen.getByText('Process Payment');
      await actUser(() => userEvent.click(processButton));

      await waitFor(() => {
        expect(mockedTerminalService.process).toHaveBeenCalledWith(
          'pi_test_declined'
        );
      });

      await waitFor(() => {
        expect(screen.getByText(/🔴 Error/)).toBeInTheDocument();
        expect(screen.getByText(/declined/i)).toBeInTheDocument();
      });
    });

    it('devrait gérer un remboursement avec succès', async () => {
      const mockConnection = {
        connection_token: 'pst_test_123',
        terminal_id: 'tmr_test_123',
      };

      const mockPaymentIntent = {
        payment_intent_id: 'pi_test_refund',
        amount: 2500,
        currency: 'eur',
        status: 'requires_payment_method',
      };

      const mockProcessResponse = {
        payment_intent_id: 'pi_test_refund',
        status: 'succeeded',
      };

      const mockCaptureResponse = {
        payment_intent_id: 'pi_test_refund',
        status: 'succeeded',
        amount_captured: 2500,
      };

      const mockRefundResponse = {
        refund_id: 're_test_123',
        payment_intent_id: 'pi_test_refund',
        amount: 2500,
        status: 'succeeded',
      };

      mockedTerminalService.connect.mockResolvedValue(mockConnection);
      mockedTerminalService.createPaymentIntent.mockResolvedValue(
        mockPaymentIntent
      );
      mockedTerminalService.process.mockResolvedValue(mockProcessResponse);
      mockedTerminalService.capture.mockResolvedValue(mockCaptureResponse);
      mockedTerminalService.refund.mockResolvedValue(mockRefundResponse);

      render(<DevTerminalConsole />);

      // Connecter
      const connectButton = screen.getByText('Connect to Terminal');
      await actUser(() => userEvent.click(connectButton));

      await waitFor(() => {
        expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
      });

      // Créer Payment Intent
      const createButton = screen.getByText('Create Payment Intent');
      await actUser(() => userEvent.click(createButton));

      await waitFor(() => {
        expect(mockedTerminalService.createPaymentIntent).toHaveBeenCalled();
      });

      // Traiter
      const processButton = screen.getByText('Process Payment');
      await actUser(() => userEvent.click(processButton));

      await waitFor(() => {
        expect(mockedTerminalService.process).toHaveBeenCalled();
      });

      // Capturer
      const captureButton = screen.getByText('Capture');
      await actUser(() => userEvent.click(captureButton));

      await waitFor(() => {
        expect(mockedTerminalService.capture).toHaveBeenCalled();
      });

      // Rembourser
      const refundButton = screen.getByText('Refund');
      await actUser(() => userEvent.click(refundButton));

      await waitFor(() => {
        expect(mockedTerminalService.refund).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText(/Refunded|succeeded/i)).toBeInTheDocument();
      });
    });
  });
});

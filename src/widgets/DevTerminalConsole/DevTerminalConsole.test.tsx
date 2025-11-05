import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { DevTerminalConsole } from './DevTerminalConsole';
import { terminalService } from '@/shared/api/terminal.service';
import { eventBus } from '@/shared/api/eventBus';

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

describe('DevTerminalConsole', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('devrait afficher le titre en mode dev', () => {
    render(<DevTerminalConsole />);
    expect(screen.getByText('🔧 Stripe Terminal Simulator (DEV)')).toBeInTheDocument();
  });

  it('devrait afficher l\'état idle initial', () => {
    render(<DevTerminalConsole />);
    expect(screen.getByText(/État:/)).toBeInTheDocument();
    expect(screen.getByText(/🟢 Idle/)).toBeInTheDocument();
  });

  it('devrait afficher le bouton Connect initialement', () => {
    render(<DevTerminalConsole />);
    expect(screen.getByText('Connect to Terminal')).toBeInTheDocument();
  });

  it('devrait appeler connect et mettre à jour l\'état', async () => {
    const mockConnection = {
      connection_token: 'pst_test_1234567890',
      terminal_id: 'tmr_test_123',
    };

    const mockConnect = vi.mocked(terminalService.connect);
    mockConnect.mockResolvedValue(mockConnection);

    render(<DevTerminalConsole />);

    const connectButton = screen.getByText('Connect to Terminal');
    connectButton.click();

    await waitFor(() => {
      expect(mockConnect).toHaveBeenCalled();
      expect(eventBus.emit).toHaveBeenCalledWith('terminal:connect', {});
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

    const mockConnect = vi.mocked(terminalService.connect);
    const mockCreatePaymentIntent = vi.mocked(terminalService.createPaymentIntent);

    mockConnect.mockResolvedValue(mockConnection);
    mockCreatePaymentIntent.mockResolvedValue(mockPaymentIntent);

    render(<DevTerminalConsole />);

    // Connecter
    const connectButton = screen.getByText('Connect to Terminal');
    connectButton.click();

    await waitFor(() => {
      expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
    });

    // Créer Payment Intent
    const createButton = screen.getByText('Create Payment Intent');
    createButton.click();

    await waitFor(() => {
      expect(mockCreatePaymentIntent).toHaveBeenCalledWith(1000, 'eur');
      expect(eventBus.emit).toHaveBeenCalledWith('terminal:payment_intent', {
        amount: 1000,
        currency: 'eur',
      });
    });
  });

  it('devrait afficher une erreur si la connexion échoue', async () => {
    const mockConnect = vi.mocked(terminalService.connect);
    mockConnect.mockRejectedValue(new Error('Connection failed'));

    render(<DevTerminalConsole />);

    const connectButton = screen.getByText('Connect to Terminal');
    connectButton.click();

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

    const mockConnect = vi.mocked(terminalService.connect);
    mockConnect.mockImplementation(() => connectPromise);

    render(<DevTerminalConsole />);

    const connectButton = screen.getByText('Connect to Terminal') as HTMLButtonElement;
    expect(connectButton).not.toBeDisabled();

    connectButton.click();

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
    await waitFor(() => {
      expect(screen.getByText(/🟢 Connected/)).toBeInTheDocument();
    }, { timeout: 2000 });

    // Le bouton Connect reste désactivé car on est dans l'état 'connected', pas 'idle'
    // C'est le comportement attendu selon la logique du composant
    expect(connectButton).toBeDisabled();
  });
});


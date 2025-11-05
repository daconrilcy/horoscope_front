import { describe, it, expect, beforeEach, vi } from 'vitest';
import { terminalService } from './terminal.service';
import { http } from './client';

// Mock http
vi.mock('./client', () => ({
  http: {
    post: vi.fn(),
  },
}));

describe('terminalService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('connect', () => {
    it('devrait retourner une connexion terminal valide', async () => {
      const mockResponse = {
        connection_token: 'pst_test_1234567890',
        terminal_id: 'tmr_test_123',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.connect();

      expect(result).toEqual(mockResponse);
      expect(result.connection_token).toBe('pst_test_1234567890');
      expect(result.terminal_id).toBe('tmr_test_123');
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/connect', {});
    });

    it('devrait échouer si réponse invalide', async () => {
      const mockResponse = {
        // connection_token manquant
        terminal_id: 'tmr_test_123',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      await expect(terminalService.connect()).rejects.toThrow();
    });
  });

  describe('createPaymentIntent', () => {
    it('devrait créer un payment intent avec montant et devise', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_123',
        amount: 1000,
        currency: 'eur',
        status: 'requires_payment_method',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.createPaymentIntent(1000, 'eur');

      expect(result).toEqual(mockResponse);
      expect(result.payment_intent_id).toBe('pi_test_123');
      expect(result.amount).toBe(1000);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/payment_intent', {
        amount: 1000,
        currency: 'eur',
      });
    });

    it('devrait utiliser EUR par défaut si devise non fournie', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_123',
        amount: 2000,
        currency: 'eur',
        status: 'requires_payment_method',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.createPaymentIntent(2000);

      expect(result.currency).toBe('eur');
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/payment_intent', {
        amount: 2000,
        currency: 'eur',
      });
    });
  });

  describe('process', () => {
    it('devrait traiter un paiement', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_123',
        status: 'succeeded',
        client_secret: 'pi_test_123_secret',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.process('pi_test_123');

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/process', {
        payment_intent_id: 'pi_test_123',
      });
    });
  });

  describe('capture', () => {
    it('devrait capturer un paiement', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_123',
        status: 'succeeded',
        amount_captured: 1000,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.capture('pi_test_123');

      expect(result).toEqual(mockResponse);
      expect(result.amount_captured).toBe(1000);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/capture', {
        payment_intent_id: 'pi_test_123',
      });
    });
  });

  describe('cancel', () => {
    it('devrait annuler un paiement', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_123',
        status: 'canceled',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.cancel('pi_test_123');

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/cancel', {
        payment_intent_id: 'pi_test_123',
      });
    });
  });

  describe('refund', () => {
    it('devrait rembourser un paiement sans montant (remboursement total)', async () => {
      const mockResponse = {
        refund_id: 're_test_123',
        payment_intent_id: 'pi_test_123',
        amount: 1000,
        status: 'succeeded',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.refund('pi_test_123');

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/refund', {
        payment_intent_id: 'pi_test_123',
      });
    });

    it('devrait rembourser un paiement avec montant partiel', async () => {
      const mockResponse = {
        refund_id: 're_test_123',
        payment_intent_id: 'pi_test_123',
        amount: 500,
        status: 'succeeded',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.refund('pi_test_123', 500);

      expect(result).toEqual(mockResponse);
      expect(result.amount).toBe(500);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/refund', {
        payment_intent_id: 'pi_test_123',
        amount: 500,
      });
    });
  });
});

/**
 * Note : Pour des tests plus complets conformes à la documentation Stripe Terminal,
 * voir terminal.service.stripe-tests.test.ts qui inclut les scénarios de test
 * pour les montants avec décimales spécifiques et les cartes de test Stripe.
 */


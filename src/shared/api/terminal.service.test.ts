import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  terminalService,
  TERMINAL_TEST_AMOUNTS,
  TERMINAL_TEST_CARDS,
} from './terminal.service';
import { http } from './client';
import { ApiError } from './errors';

// Mock le client HTTP
vi.mock('./client', () => ({
  http: {
    post: vi.fn(),
  },
}));

// Mock import.meta.env.DEV
vi.mock('import.meta', () => ({
  env: {
    DEV: true,
  },
}));

describe('terminalService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('connect', () => {
    it('devrait appeler POST /v1/terminal/connect et retourner connection_token', async () => {
      const mockResponse = {
        connection_token: 'tok_test_1234567890',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.connect();

      expect(result).toEqual(mockResponse);
      expect(result.connection_token).toBe('tok_test_1234567890');
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/connect', {});
    });

    it("devrait propager ApiError en cas d'erreur API", async () => {
      const apiError = new ApiError('Forbidden', 403);
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(apiError);

      await expect(terminalService.connect()).rejects.toThrow(ApiError);
    });
  });

  describe('createPaymentIntent', () => {
    it('devrait créer un PaymentIntent avec montant exact (100 centimes)', async () => {
      const mockResponse = {
        client_secret: 'pi_test_secret_123',
        payment_intent_id: 'pi_test_123',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.createPaymentIntent({
        amount: TERMINAL_TEST_AMOUNTS.SUCCESS,
      });

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/payment-intent', {
        amount: 100,
        currency: 'eur',
        payment_method_types: ['card_present'],
      });
    });

    it('devrait créer un PaymentIntent avec montant 101 (PIN offline)', async () => {
      const mockResponse = {
        client_secret: 'pi_test_secret_101',
        payment_intent_id: 'pi_test_101',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await terminalService.createPaymentIntent({
        amount: TERMINAL_TEST_AMOUNTS.SUCCESS_01,
      });

      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/payment-intent', {
        amount: 101,
        currency: 'eur',
        payment_method_types: ['card_present'],
      });
    });

    it('devrait créer un PaymentIntent avec montant 102 (PIN online)', async () => {
      const mockResponse = {
        client_secret: 'pi_test_secret_102',
        payment_intent_id: 'pi_test_102',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await terminalService.createPaymentIntent({
        amount: TERMINAL_TEST_AMOUNTS.SUCCESS_02,
      });

      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/payment-intent', {
        amount: 102,
        currency: 'eur',
        payment_method_types: ['card_present'],
      });
    });

    it('devrait créer un PaymentIntent avec montant 200 (carte refusée)', async () => {
      const mockResponse = {
        client_secret: 'pi_test_secret_200',
        payment_intent_id: 'pi_test_200',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await terminalService.createPaymentIntent({
        amount: TERMINAL_TEST_AMOUNTS.DECLINED,
      });

      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/payment-intent', {
        amount: 200,
        currency: 'eur',
        payment_method_types: ['card_present'],
      });
    });
  });

  describe('process', () => {
    it('devrait traiter un paiement avec carte de test SUCCESS', async () => {
      const mockResponse = {
        status: 'succeeded',
        payment_intent_id: 'pi_test_123',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.process({
        payment_intent_id: 'pi_test_123',
        payment_method: TERMINAL_TEST_CARDS.SUCCESS,
      });

      expect(result.status).toBe('succeeded');
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/process', {
        payment_intent_id: 'pi_test_123',
        payment_method: TERMINAL_TEST_CARDS.SUCCESS,
      });
    });

    it('devrait échouer avec carte DECLINED', async () => {
      const mockResponse = {
        status: 'requires_payment_method',
        payment_intent_id: 'pi_test_123',
        error_code: 'card_declined',
        error_message: 'Your card was declined.',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.process({
        payment_intent_id: 'pi_test_123',
        payment_method: TERMINAL_TEST_CARDS.DECLINED,
      });

      expect(result.status).toBe('requires_payment_method');
      expect(result.error_code).toBe('card_declined');
    });

    it('devrait échouer avec carte INSUFFICIENT_FUNDS', async () => {
      const mockResponse = {
        status: 'requires_payment_method',
        payment_intent_id: 'pi_test_123',
        error_code: 'insufficient_funds',
        error_message: 'Your card has insufficient funds.',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.process({
        payment_intent_id: 'pi_test_123',
        payment_method: TERMINAL_TEST_CARDS.INSUFFICIENT_FUNDS,
      });

      expect(result.status).toBe('requires_payment_method');
      expect(result.error_code).toBe('insufficient_funds');
    });

    it('devrait échouer avec carte EXPIRED_CARD', async () => {
      const mockResponse = {
        status: 'requires_payment_method',
        payment_intent_id: 'pi_test_123',
        error_code: 'expired_card',
        error_message: 'Your card has expired.',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.process({
        payment_intent_id: 'pi_test_123',
        payment_method: TERMINAL_TEST_CARDS.EXPIRED_CARD,
      });

      expect(result.status).toBe('requires_payment_method');
      expect(result.error_code).toBe('expired_card');
    });
  });

  describe('capture', () => {
    it('devrait capturer un paiement avec succès', async () => {
      const mockResponse = {
        status: 'succeeded',
        payment_intent_id: 'pi_test_123',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.capture({
        payment_intent_id: 'pi_test_123',
      });

      expect(result.status).toBe('succeeded');
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/capture', {
        payment_intent_id: 'pi_test_123',
      });
    });
  });

  describe('cancel', () => {
    it('devrait annuler un paiement', async () => {
      const mockResponse = {
        status: 'canceled',
        payment_intent_id: 'pi_test_123',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.cancel({
        payment_intent_id: 'pi_test_123',
      });

      expect(result.status).toBe('canceled');
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/cancel', {
        payment_intent_id: 'pi_test_123',
      });
    });
  });

  describe('refund', () => {
    it('devrait rembourser un paiement total (sans amount)', async () => {
      const mockResponse = {
        refund_id: 're_test_123',
        amount: 100,
        status: 'succeeded',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.refund({
        payment_intent_id: 'pi_test_123',
      });

      expect(result.status).toBe('succeeded');
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/refund', {
        payment_intent_id: 'pi_test_123',
        amount: undefined,
      });
    });

    it('devrait rembourser un paiement partiel (avec amount)', async () => {
      const mockResponse = {
        refund_id: 're_test_123',
        amount: 50,
        status: 'succeeded',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await terminalService.refund({
        payment_intent_id: 'pi_test_123',
        amount: 50,
      });

      expect(result.status).toBe('succeeded');
      expect(result.amount).toBe(50);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/terminal/refund', {
        payment_intent_id: 'pi_test_123',
        amount: 50,
      });
    });
  });
});

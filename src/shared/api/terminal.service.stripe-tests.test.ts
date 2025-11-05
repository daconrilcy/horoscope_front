/**
 * Tests conformes à la documentation Stripe Terminal
 * https://docs.stripe.com/terminal/references/testing
 *
 * Ces tests vérifient que le service terminal peut gérer les différents
 * scénarios de réponse du backend selon les cartes de test Stripe.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { terminalService } from './terminal.service';
import { http } from './client';
import { ApiError } from './errors';

// Mock http
vi.mock('./client', () => ({
  http: {
    post: vi.fn(),
  },
}));

/**
 * Montants de test selon la documentation Stripe Terminal
 * Les montants finissant par des décimales spécifiques produisent différents résultats
 */
const TEST_AMOUNTS = {
  /** 00 : Paiement approuvé */
  APPROVED: 2500, // 25.00 EUR
  /** 01 : Paiement refusé avec call_issuer */
  DECLINED_CALL_ISSUER: 1001, // 10.01 EUR
  /** 02 : Demande PIN offline */
  OFFLINE_PIN_REQUIRED: 2002, // 20.02 EUR
  /** 03 : Demande PIN online */
  ONLINE_PIN_REQUIRED: 3003, // 30.03 EUR
  /** 05 : Refusé avec generic_decline */
  GENERIC_DECLINE: 5005, // 50.05 EUR
  /** 55 : Refusé avec incorrect_pin */
  INCORRECT_PIN: 5555, // 55.55 EUR
  /** 65 : Refusé avec withdrawal_count_limit_exceeded */
  WITHDRAWAL_LIMIT_EXCEEDED: 6565, // 65.65 EUR
  /** 75 : Refusé avec pin_try_exceeded */
  PIN_TRY_EXCEEDED: 7575, // 75.75 EUR
} as const;

describe('terminalService - Stripe Terminal Test Scenarios', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createPaymentIntent - Test amounts according to Stripe docs', () => {
    it('devrait créer un PI avec montant approuvé (decimal 00)', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_approved',
        amount: TEST_AMOUNTS.APPROVED,
        currency: 'eur',
        status: 'requires_payment_method',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.createPaymentIntent(
        TEST_AMOUNTS.APPROVED,
        'eur'
      );

      expect(result.status).toBe('requires_payment_method');
      expect(result.amount).toBe(TEST_AMOUNTS.APPROVED);
    });

    it('devrait gérer un paiement refusé avec call_issuer (decimal 01)', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_declined',
        amount: TEST_AMOUNTS.DECLINED_CALL_ISSUER,
        currency: 'eur',
        status: 'requires_payment_method',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.createPaymentIntent(
        TEST_AMOUNTS.DECLINED_CALL_ISSUER,
        'eur'
      );

      expect(result.status).toBe('requires_payment_method');
      expect(result.amount).toBe(TEST_AMOUNTS.DECLINED_CALL_ISSUER);
    });

    it('devrait gérer un paiement avec PIN offline requis (decimal 02)', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_offline_pin',
        amount: TEST_AMOUNTS.OFFLINE_PIN_REQUIRED,
        currency: 'eur',
        status: 'requires_payment_method',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.createPaymentIntent(
        TEST_AMOUNTS.OFFLINE_PIN_REQUIRED,
        'eur'
      );

      expect(result.status).toBe('requires_payment_method');
    });

    it('devrait gérer un paiement avec PIN online requis (decimal 03)', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_online_pin',
        amount: TEST_AMOUNTS.ONLINE_PIN_REQUIRED,
        currency: 'eur',
        status: 'requires_payment_method',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.createPaymentIntent(
        TEST_AMOUNTS.ONLINE_PIN_REQUIRED,
        'eur'
      );

      expect(result.status).toBe('requires_payment_method');
    });
  });

  describe('process - Error scenarios from Stripe test cards', () => {
    it('devrait gérer un paiement refusé (charge_declined)', async () => {
      const mockError = new ApiError(
        'Your card was declined.',
        402,
        'card_declined',
        undefined,
        {
          code: 'card_declined',
          decline_code: 'generic_decline',
        }
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(terminalService.process('pi_test_declined')).rejects.toThrow(
        ApiError
      );
    });

    it('devrait gérer un paiement refusé avec insufficient_funds', async () => {
      const mockError = new ApiError(
        'Your card has insufficient funds.',
        402,
        'card_declined',
        undefined,
        {
          code: 'card_declined',
          decline_code: 'insufficient_funds',
        }
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(terminalService.process('pi_test_insufficient')).rejects.toThrow(
        ApiError
      );
    });

    it('devrait gérer un paiement refusé avec expired_card', async () => {
      const mockError = new ApiError(
        'Your card has expired.',
        402,
        'expired_card',
        undefined,
        {
          code: 'expired_card',
        }
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(terminalService.process('pi_test_expired')).rejects.toThrow(
        ApiError
      );
    });

    it('devrait gérer un paiement refusé avec processing_error', async () => {
      const mockError = new ApiError(
        'An error occurred while processing your card.',
        402,
        'processing_error',
        undefined,
        {
          code: 'processing_error',
        }
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(terminalService.process('pi_test_processing_error')).rejects.toThrow(
        ApiError
      );
    });
  });

  describe('process - Success scenarios', () => {
    it('devrait traiter un paiement avec succès (montant approuvé)', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_success',
        status: 'succeeded',
        client_secret: 'pi_test_success_secret',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.process('pi_test_success');

      expect(result.status).toBe('succeeded');
      expect(result.payment_intent_id).toBe('pi_test_success');
    });

    it('devrait traiter un paiement avec PIN offline (offline_pin_cvm)', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_offline_pin',
        status: 'succeeded',
        client_secret: 'pi_test_offline_pin_secret',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.process('pi_test_offline_pin');

      expect(result.status).toBe('succeeded');
    });

    it('devrait traiter un paiement avec PIN online (online_pin_cvm)', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_online_pin',
        status: 'succeeded',
        client_secret: 'pi_test_online_pin_secret',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.process('pi_test_online_pin');

      expect(result.status).toBe('succeeded');
    });
  });

  describe('refund - Test scenarios', () => {
    it('devrait rembourser un paiement avec succès', async () => {
      const mockResponse = {
        refund_id: 're_test_success',
        payment_intent_id: 'pi_test_success',
        amount: 2500,
        status: 'succeeded',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.refund('pi_test_success', 2500);

      expect(result.status).toBe('succeeded');
      expect(result.amount).toBe(2500);
    });

    it('devrait gérer un remboursement partiel', async () => {
      const mockResponse = {
        refund_id: 're_test_partial',
        payment_intent_id: 'pi_test_success',
        amount: 1000,
        status: 'succeeded',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.refund('pi_test_success', 1000);

      expect(result.amount).toBe(1000);
    });

    it('devrait gérer un remboursement total (sans montant spécifié)', async () => {
      const mockResponse = {
        refund_id: 're_test_full',
        payment_intent_id: 'pi_test_success',
        amount: 2500,
        status: 'succeeded',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.refund('pi_test_success');

      expect(result.amount).toBe(2500);
    });

    it('devrait gérer un échec de remboursement (refund_fail)', async () => {
      const mockError = new ApiError(
        'Refund failed',
        402,
        'refund_failed',
        undefined,
        {
          failure_reason: 'expired_or_canceled_card',
        }
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(terminalService.refund('pi_test_refund_fail')).rejects.toThrow(
        ApiError
      );
    });
  });

  describe('cancel - Test scenarios', () => {
    it('devrait annuler un paiement avec succès', async () => {
      const mockResponse = {
        payment_intent_id: 'pi_test_cancel',
        status: 'canceled',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await terminalService.cancel('pi_test_cancel');

      expect(result.status).toBe('canceled');
    });
  });
});

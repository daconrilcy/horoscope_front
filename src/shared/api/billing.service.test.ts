import { describe, it, expect, beforeEach, vi } from 'vitest';
import { billingService } from './billing.service';
import { http } from './client';
import { PLANS } from '@/shared/config/plans';
import { ApiError } from './errors';
import { NetworkError } from './errors';

// Mock le client HTTP
vi.mock('./client', () => ({
  http: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

// Mock eventBus
vi.mock('./eventBus', () => ({
  eventBus: {
    emit: vi.fn(),
  },
}));

describe('billingService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createCheckoutSession', () => {
    const idemKey = 'test-idempotency-key-123';

    it('devrait retourner checkout_url valide avec réponse valide', async () => {
      const mockResponse = {
        checkout_url: 'https://checkout.stripe.com/pay/cs_test_123',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await billingService.createCheckoutSession(
        PLANS.PLUS,
        idemKey
      );

      expect(result).toBe('https://checkout.stripe.com/pay/cs_test_123');
      expect(mockHttpPost).toHaveBeenCalledWith(
        '/v1/billing/checkout',
        { plan: 'plus' },
        {
          idempotency: true,
          headers: {
            'Idempotency-Key': idemKey,
          },
        }
      );
    });

    it('devrait appeler avec body exact { plan }', async () => {
      const mockResponse = {
        checkout_url: 'https://checkout.stripe.com/pay/cs_test_123',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await billingService.createCheckoutSession(PLANS.PRO, idemKey);

      expect(mockHttpPost).toHaveBeenCalledWith(
        '/v1/billing/checkout',
        { plan: 'pro' },

        expect.objectContaining({
          idempotency: true,
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          headers: expect.objectContaining({
            'Idempotency-Key': idemKey,
          }),
        })
      );
    });

    it('devrait utiliser la clé Idempotency-Key passée dans les headers', async () => {
      const customIdemKey = 'custom-key-456';
      const mockResponse = {
        checkout_url: 'https://checkout.stripe.com/pay/cs_test_123',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await billingService.createCheckoutSession(PLANS.PLUS, customIdemKey);

      expect(mockHttpPost).toHaveBeenCalledWith(
        '/v1/billing/checkout',
        { plan: 'plus' },

        expect.objectContaining({
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          headers: expect.objectContaining({
            'Idempotency-Key': customIdemKey,
          }),
        })
      );
    });

    it('devrait échouer si checkout_url manquant', async () => {
      const mockResponse = {
        // checkout_url manquant
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        billingService.createCheckoutSession(PLANS.PLUS, idemKey)
      ).rejects.toThrow();
    });

    it('devrait échouer si checkout_url invalide (pas une URL)', async () => {
      const mockResponse = {
        checkout_url: 'not-a-valid-url',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        billingService.createCheckoutSession(PLANS.PLUS, idemKey)
      ).rejects.toThrow();
    });

    it('devrait échouer si JSON invalide → ZodError (fail-fast)', async () => {
      const mockResponse = {
        // Réponse invalide
        wrong_field: 'value',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        billingService.createCheckoutSession(PLANS.PLUS, idemKey)
      ).rejects.toThrow('Invalid checkout payload or response');
    });

    it('devrait propager ApiError 401 et déclencher événement unauthorized', async () => {
      const apiError = new ApiError('Unauthorized', 401);
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(apiError);

      await expect(
        billingService.createCheckoutSession(PLANS.PLUS, idemKey)
      ).rejects.toThrow(ApiError);

      // L'événement unauthorized est émis par le wrapper client.ts
      // On vérifie que l'erreur est propagée correctement
      expect(mockHttpPost).toHaveBeenCalled();
    });

    it('devrait propager NetworkError', async () => {
      const networkError = new NetworkError('timeout', 'Request timeout');
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(
        networkError
      );

      await expect(
        billingService.createCheckoutSession(PLANS.PLUS, idemKey)
      ).rejects.toThrow(NetworkError);
    });
  });

  describe('createPortalSession', () => {
    it('devrait retourner portal_url valide avec réponse valide', async () => {
      const mockResponse = {
        portal_url: 'https://billing.stripe.com/p/session_123',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await billingService.createPortalSession();

      expect(result).toBe('https://billing.stripe.com/p/session_123');
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/billing/portal', {});
    });

    it('devrait appeler POST sans body et sans idempotency', async () => {
      const mockResponse = {
        portal_url: 'https://billing.stripe.com/p/session_123',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await billingService.createPortalSession();

      expect(mockHttpPost).toHaveBeenCalledWith('/v1/billing/portal', {});
      // Vérifier qu'on n'utilise pas idempotency (pas de 3e paramètre avec idempotency: true)
      const calls = mockHttpPost.mock.calls;
      const lastCall = calls[calls.length - 1];
      expect(lastCall).toHaveLength(2); // Seulement endpoint et body
    });

    it('devrait échouer si portal_url manquant', async () => {
      const mockResponse = {
        // portal_url manquant
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(billingService.createPortalSession()).rejects.toThrow();
    });

    it('devrait échouer si portal_url invalide (pas une URL)', async () => {
      const mockResponse = {
        portal_url: 'not-a-valid-url',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(billingService.createPortalSession()).rejects.toThrow();
    });

    it('devrait échouer si JSON invalide → ZodError (fail-fast)', async () => {
      const mockResponse = {
        // Réponse invalide
        wrong_field: 'value',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(billingService.createPortalSession()).rejects.toThrow(
        'Invalid portal payload or response'
      );
    });

    it('devrait propager ApiError', async () => {
      const apiError = new ApiError('Forbidden', 403);
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(apiError);

      await expect(billingService.createPortalSession()).rejects.toThrow(
        ApiError
      );
    });

    it('devrait propager NetworkError', async () => {
      const networkError = new NetworkError('offline', 'Network error');
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(
        networkError
      );

      await expect(billingService.createPortalSession()).rejects.toThrow(
        NetworkError
      );
    });
  });

  describe('verifyCheckoutSession', () => {
    const sessionId = 'cs_test_1234567890';

    it('devrait retourner statut paid avec plan', async () => {
      const mockResponse = {
        status: 'paid',
        session_id: sessionId,
        plan: 'plus',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await billingService.verifyCheckoutSession(sessionId);

      expect(result).toEqual(mockResponse);
      expect(result.status).toBe('paid');
      expect(result.plan).toBe('plus');
      expect(mockHttpGet).toHaveBeenCalledWith(
        `/v1/billing/checkout/session?session_id=${encodeURIComponent(sessionId)}`
      );
    });

    it('devrait retourner statut unpaid sans plan', async () => {
      const mockResponse = {
        status: 'unpaid',
        session_id: sessionId,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await billingService.verifyCheckoutSession(sessionId);

      expect(result.status).toBe('unpaid');
      expect(result.plan).toBeUndefined();
    });

    it('devrait retourner statut expired', async () => {
      const mockResponse = {
        status: 'expired',
        session_id: sessionId,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await billingService.verifyCheckoutSession(sessionId);

      expect(result.status).toBe('expired');
    });

    it("devrait encoder correctement session_id dans l'URL", async () => {
      const specialSessionId = 'cs_test_abc@123+456';
      const mockResponse = {
        status: 'paid',
        session_id: specialSessionId,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      await billingService.verifyCheckoutSession(specialSessionId);

      expect(mockHttpGet).toHaveBeenCalledWith(
        `/v1/billing/checkout/session?session_id=${encodeURIComponent(specialSessionId)}`
      );
    });

    it('devrait échouer si session_id est vide', async () => {
      await expect(billingService.verifyCheckoutSession('')).rejects.toThrow(
        'session_id is required'
      );
    });

    it('devrait échouer si session_id est null', async () => {
      await expect(
        billingService.verifyCheckoutSession(null as unknown as string)
      ).rejects.toThrow('session_id is required');
    });

    it('devrait échouer si réponse invalide (status manquant)', async () => {
      const mockResponse = {
        session_id: sessionId,
        // status manquant
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      await expect(
        billingService.verifyCheckoutSession(sessionId)
      ).rejects.toThrow('Invalid verify checkout session response');
    });

    it('devrait échouer si réponse invalide (status invalide)', async () => {
      const mockResponse = {
        status: 'invalid_status',
        session_id: sessionId,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      await expect(
        billingService.verifyCheckoutSession(sessionId)
      ).rejects.toThrow('Invalid verify checkout session response');
    });

    it('devrait propager ApiError 404', async () => {
      const apiError = new ApiError('Session introuvable', 404);
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(apiError);

      await expect(
        billingService.verifyCheckoutSession(sessionId)
      ).rejects.toThrow(ApiError);
    });

    it('devrait propager ApiError 401', async () => {
      const apiError = new ApiError('Unauthorized', 401);
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(apiError);

      await expect(
        billingService.verifyCheckoutSession(sessionId)
      ).rejects.toThrow(ApiError);
    });

    it('devrait propager NetworkError', async () => {
      const networkError = new NetworkError('offline', 'Network error');
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(networkError);

      await expect(
        billingService.verifyCheckoutSession(sessionId)
      ).rejects.toThrow(NetworkError);
    });
  });
});

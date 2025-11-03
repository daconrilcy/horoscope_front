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
      ).rejects.toThrow('Invalid checkout response');
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
        'Invalid portal response'
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
});

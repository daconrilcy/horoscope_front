import { describe, it, expect, beforeEach, vi } from 'vitest';
import { paywallService } from './paywall.service';
import { http } from './client';
import { FEATURES } from '@/shared/config/features';

// Mock le client HTTP
vi.mock('./client', () => ({
  http: {
    post: vi.fn(),
  },
}));

describe('paywallService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('decision', () => {
    it('devrait retourner allowed: true avec réponse valide', async () => {
      const mockResponse = {
        allowed: true,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await paywallService.decision(FEATURES.CHAT_MSG_PER_DAY);

      expect(result).toEqual(mockResponse);
      expect(result.allowed).toBe(true);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/paywall/decision', {
        feature: FEATURES.CHAT_MSG_PER_DAY,
      });
    });

    it('devrait retourner allowed: false avec reason: plan et upgrade_url', async () => {
      const mockResponse = {
        allowed: false,
        reason: 'plan',
        upgrade_url: 'https://example.com/upgrade',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await paywallService.decision(FEATURES.HORO_TODAY_PREMIUM);

      expect(result).toEqual(mockResponse);
      expect(result.allowed).toBe(false);
      if (result.allowed === false) {
        expect(result.reason).toBe('plan');
        expect(result.upgrade_url).toBe('https://example.com/upgrade');
      }
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/paywall/decision', {
        feature: FEATURES.HORO_TODAY_PREMIUM,
      });
    });

    it('devrait retourner allowed: false avec reason: rate et retry_after', async () => {
      const mockResponse = {
        allowed: false,
        reason: 'rate',
        retry_after: 3600,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await paywallService.decision(FEATURES.CHAT_MSG_PER_DAY);

      expect(result).toEqual(mockResponse);
      expect(result.allowed).toBe(false);
      if (result.allowed === false) {
        expect(result.reason).toBe('rate');
        expect(result.retry_after).toBe(3600);
      }
    });

    it('devrait échouer si réponse invalide (allowed manquant)', async () => {
      const mockResponse = {
        // allowed manquant
        reason: 'plan',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        paywallService.decision(FEATURES.CHAT_MSG_PER_DAY)
      ).rejects.toThrow();
    });

    it('devrait échouer si allowed: false sans reason', async () => {
      const mockResponse = {
        allowed: false,
        // reason manquant
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        paywallService.decision(FEATURES.CHAT_MSG_PER_DAY)
      ).rejects.toThrow();
    });

    it('devrait échouer si reason invalide', async () => {
      const mockResponse = {
        allowed: false,
        reason: 'invalid', // Doit être 'plan' ou 'rate'
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        paywallService.decision(FEATURES.CHAT_MSG_PER_DAY)
      ).rejects.toThrow();
    });
  });
});

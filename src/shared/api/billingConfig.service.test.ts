import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  billingConfigService,
  BillingConfigSchema,
} from './billingConfig.service';
import { http } from './client';

// Mock le client HTTP
vi.mock('./client', () => ({
  http: {
    get: vi.fn(),
  },
}));

// Mock de window.location
Object.defineProperty(window, 'location', {
  value: {
    origin: 'http://localhost:5173',
  },
  writable: true,
});

describe('billingConfigService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    billingConfigService.clearCache();
  });

  describe('getConfig', () => {
    it("devrait retourner la config depuis l'API", async () => {
      const mockConfig = {
        publicBaseUrl: 'http://localhost:5173',
        checkoutSuccessPath: '/billing/success',
        checkoutCancelPath: '/billing/cancel',
        portalReturnUrl: 'http://localhost:5173/app/account',
        checkoutTrialsEnabled: true,
        checkoutCouponsEnabled: false,
        stripeTaxEnabled: false,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockConfig);

      const result = await billingConfigService.getConfig();

      expect(result).toEqual({
        ...mockConfig,
        publicBaseUrl: 'http://localhost:5173', // Normalisé
      });
      expect(mockHttpGet).toHaveBeenCalledWith('/v1/config', {
        noRetry: false,
      });
    });

    it('devrait normaliser les URLs (retirer trailing slash)', async () => {
      const mockConfig = {
        publicBaseUrl: 'http://localhost:5173/',
        checkoutSuccessPath: '/billing/success',
        checkoutCancelPath: '/billing/cancel',
        portalReturnUrl: 'http://localhost:5173/app/account/',
        checkoutTrialsEnabled: false,
        checkoutCouponsEnabled: true,
        stripeTaxEnabled: true,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockConfig);

      const result = await billingConfigService.getConfig();

      expect(result.publicBaseUrl).toBe('http://localhost:5173');
      expect(result.portalReturnUrl).toBe('http://localhost:5173/app/account');
    });

    it('devrait mettre en cache la config (appel API une seule fois)', async () => {
      const mockConfig = {
        publicBaseUrl: 'http://localhost:5173',
        checkoutSuccessPath: '/billing/success',
        checkoutCancelPath: '/billing/cancel',
        checkoutTrialsEnabled: true,
        checkoutCouponsEnabled: false,
        stripeTaxEnabled: false,
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockConfig);

      // Premier appel
      await billingConfigService.getConfig();

      // Second appel (devrait utiliser le cache)
      await billingConfigService.getConfig();

      expect(mockHttpGet).toHaveBeenCalledTimes(1);
    });

    it('devrait fallback sur env si API 404', async () => {
      const mockError = new Error('Not Found');
      (mockError as { status?: number }).status = 404;

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      const result = await billingConfigService.getConfig();

      // Devrait avoir des valeurs par défaut
      expect(result).toBeDefined();
      expect(result.publicBaseUrl).toBeDefined();
      expect(typeof result.checkoutTrialsEnabled).toBe('boolean');
    });
  });

  describe('validateOrigin', () => {
    it("devrait détecter un match d'origin", () => {
      const config = {
        publicBaseUrl: 'http://localhost:5173',
        checkoutSuccessPath: '/billing/success',
        checkoutCancelPath: '/billing/cancel',
        checkoutTrialsEnabled: false,
        checkoutCouponsEnabled: false,
        stripeTaxEnabled: false,
      };

      const result = billingConfigService.validateOrigin(config);

      expect(result.matches).toBe(true);
      expect(result.current).toBe('http://localhost:5173');
      expect(result.expected).toBe('http://localhost:5173');
    });

    it("devrait détecter un mismatch d'origin", () => {
      const config = {
        publicBaseUrl: 'https://horoscope.app',
        checkoutSuccessPath: '/billing/success',
        checkoutCancelPath: '/billing/cancel',
        checkoutTrialsEnabled: false,
        checkoutCouponsEnabled: false,
        stripeTaxEnabled: false,
      };

      const result = billingConfigService.validateOrigin(config);

      expect(result.matches).toBe(false);
      expect(result.current).toBe('http://localhost:5173');
      expect(result.expected).toBe('https://horoscope.app');
    });
  });

  describe('BillingConfigSchema', () => {
    it('devrait valider une config complète', () => {
      const valid = {
        publicBaseUrl: 'https://horoscope.app',
        checkoutSuccessPath: '/billing/success',
        checkoutCancelPath: '/billing/cancel',
        portalReturnUrl: 'https://horoscope.app/app/account',
        checkoutTrialsEnabled: true,
        checkoutCouponsEnabled: true,
        stripeTaxEnabled: true,
        priceLookupHash: 'abc123',
        priceLookupLength: 10,
      };

      const result = BillingConfigSchema.safeParse(valid);
      expect(result.success).toBe(true);
    });

    it('devrait rejeter si publicBaseUrl invalide', () => {
      const invalid = {
        publicBaseUrl: 'not-a-url',
        checkoutSuccessPath: '/billing/success',
        checkoutCancelPath: '/billing/cancel',
        checkoutTrialsEnabled: false,
        checkoutCouponsEnabled: false,
        stripeTaxEnabled: false,
      };

      const result = BillingConfigSchema.safeParse(invalid);
      expect(result.success).toBe(false);
    });
  });
});

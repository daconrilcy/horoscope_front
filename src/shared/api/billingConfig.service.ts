import { z } from 'zod';
import { http } from './client';
import { env } from '@/shared/config/env';

/**
 * Schéma Zod pour la configuration billing exposée par /v1/config
 */
export const BillingConfigSchema = z.object({
  publicBaseUrl: z.string().url(),
  checkoutSuccessPath: z.string(),
  checkoutCancelPath: z.string(),
  portalReturnUrl: z.string().url().optional().or(z.literal('')),
  checkoutTrialsEnabled: z.boolean(),
  checkoutCouponsEnabled: z.boolean(),
  stripeTaxEnabled: z.boolean(),
  priceLookupHash: z.string().optional(),
  priceLookupLength: z.number().int().optional(),
});

/**
 * Type inféré depuis le schéma Zod
 */
export type BillingConfig = z.infer<typeof BillingConfigSchema>;

/**
 * Cache mémoire singleton pour la config billing
 */
let cachedConfig: BillingConfig | null = null;
let cacheTimestamp: number = 0;
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

/**
 * Fallback depuis les variables d'environnement
 */
function getFallbackConfig(): BillingConfig {
  const defaultBaseUrl = import.meta.env.DEV
    ? window.location.origin
    : 'https://horoscope.app';

  const fallback: BillingConfig = {
    publicBaseUrl: env.VITE_PUBLIC_BASE_URL || defaultBaseUrl,
    checkoutSuccessPath: env.VITE_CHECKOUT_SUCCESS_PATH || '/billing/success',
    checkoutCancelPath: env.VITE_CHECKOUT_CANCEL_PATH || '/billing/cancel',
    portalReturnUrl:
      env.VITE_PORTAL_RETURN_URL || `${defaultBaseUrl}/app/account`,
    checkoutTrialsEnabled: env.VITE_CHECKOUT_TRIALS_ENABLED || false,
    checkoutCouponsEnabled: env.VITE_CHECKOUT_COUPONS_ENABLED || false,
    stripeTaxEnabled: env.VITE_STRIPE_TAX_ENABLED || false,
  };

  return fallback;
}

/**
 * Normalise une URL (retire trailing slash)
 */
function normalizeUrl(url: string): string {
  return url.replace(/\/+$/, '');
}

/**
 * Compare uniquement l'origin d'une URL (pas le path)
 */
function compareOrigin(url1: string, url2: string): boolean {
  try {
    return new URL(url1).origin === new URL(url2).origin;
  } catch {
    return false;
  }
}

/**
 * Service pour récupérer la configuration billing depuis l'API
 */
export const billingConfigService = {
  /**
   * Récupère la configuration billing (GET /v1/config avec fallback)
   * @returns Configuration billing validée et normalisée
   * @throws Error si validation Zod échoue
   */
  async getConfig(): Promise<BillingConfig> {
    // Vérifier le cache
    const now = Date.now();
    if (cachedConfig && now - cacheTimestamp < CACHE_TTL_MS) {
      return cachedConfig;
    }

    try {
      // Tenter de récupérer la config depuis l'API
      const response = await http.get<unknown>('/v1/config', {
        noRetry: false, // Autoriser retry pour GET /v1/config
      });

      // Validation Zod stricte
      const validated = BillingConfigSchema.parse(response);

      // Normaliser les URLs
      validated.publicBaseUrl = normalizeUrl(validated.publicBaseUrl);

      if (validated.portalReturnUrl) {
        validated.portalReturnUrl = normalizeUrl(validated.portalReturnUrl);
      }

      // Mettre en cache
      cachedConfig = validated;
      cacheTimestamp = now;

      return validated;
    } catch (error) {
      // Fallback sur env si 404/5xx ou réseau
      if (import.meta.env.DEV) {
        console.warn(
          "[config:fallback] API /v1/config non disponible, utilisation des variables d'environnement",
          error
        );
      }

      const fallback = getFallbackConfig();

      // Normaliser les URLs
      fallback.publicBaseUrl = normalizeUrl(fallback.publicBaseUrl);

      if (fallback.portalReturnUrl) {
        fallback.portalReturnUrl = normalizeUrl(fallback.portalReturnUrl);
      }

      // Mettre en cache aussi le fallback (durée réduite)
      cachedConfig = fallback;
      cacheTimestamp = now;

      return fallback;
    }
  },

  /**
   * Invalide le cache (utile pour les tests ou refresh manuel)
   * @internal
   */
  clearCache(): void {
    cachedConfig = null;
    cacheTimestamp = 0;
  },

  /**
   * Compare l'origin de publicBaseUrl avec l'origin actuel
   * @param config Configuration à comparer
   * @returns true si les origins matchent, false sinon
   */
  validateOrigin(config: BillingConfig): {
    matches: boolean;
    current: string;
    expected: string;
  } {
    const current = window.location.origin;
    const expected = new URL(config.publicBaseUrl).origin;

    return {
      matches: compareOrigin(current, expected),
      current,
      expected,
    };
  },
};

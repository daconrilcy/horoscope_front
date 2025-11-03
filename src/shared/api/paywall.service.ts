import { z } from 'zod';
import { http } from './client';
import { assertValidFeatureKey } from '@/shared/config/features';

/**
 * Schémas Zod discriminés pour la réponse paywall
 */

/**
 * Réponse paywall autorisée
 */
const PaywallAllowedSchema = z.object({
  allowed: z.literal(true),
});

/**
 * Réponse paywall bloquée
 */
const PaywallBlockedSchema = z.object({
  allowed: z.literal(false),
  reason: z.enum(['plan', 'rate']),
  upgrade_url: z.string().url().optional(),
  retry_after: z.number().int().positive().optional(),
});

/**
 * Schéma union pour la décision paywall
 */
export const PaywallDecisionSchema = z.union([
  PaywallAllowedSchema,
  PaywallBlockedSchema,
]);

/**
 * Types inférés depuis les schémas Zod
 */
export type PaywallAllowed = z.infer<typeof PaywallAllowedSchema>;
export type PaywallBlocked = z.infer<typeof PaywallBlockedSchema>;
export type PaywallDecision = z.infer<typeof PaywallDecisionSchema>;

/**
 * Service pour gérer les décisions paywall
 * Endpoint : POST /v1/paywall/decision
 */
export const paywallService = {
  /**
   * Vérifie si une feature est autorisée pour l'utilisateur actuel
   * @param feature Clé de la feature à vérifier
   * @returns Réponse validée avec allowed, reason, upgrade_url, retry_after
   * @throws ApiError si erreur API (402, 429, etc.)
   * @throws NetworkError si erreur réseau
   */
  async decision(feature: string): Promise<PaywallDecision> {
    // Vérifier la clé en dev
    assertValidFeatureKey(feature);

    try {
      const response = await http.post<unknown>('/v1/paywall/decision', {
        feature,
      });

      // Validation Zod stricte (fail-fast)
      const validated = PaywallDecisionSchema.parse(response);
      return validated;
    } catch (error) {
      // Si c'est une ApiError avec details, enrichir avec les details parsés
      if (error instanceof z.ZodError) {
        // Erreur de validation Zod
        throw new Error(`Invalid paywall response: ${error.message}`);
      }
      throw error;
    }
  },
};

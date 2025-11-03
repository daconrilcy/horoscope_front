import { z } from 'zod';
import { http } from './client';
import { assertValidPlan, type BillingPlan } from '@/shared/config/plans';

/**
 * Schémas Zod stricts pour les réponses billing
 */

/**
 * Schéma pour la réponse de création de session checkout
 */
export const CheckoutSessionSchema = z.object({
  checkout_url: z.string().url(),
});

/**
 * Schéma pour la réponse de création de session portal
 */
export const PortalSessionSchema = z.object({
  portal_url: z.string().url(),
});

/**
 * Types inférés depuis les schémas Zod
 */
export type CheckoutSessionResponse = z.infer<typeof CheckoutSessionSchema>;
export type PortalSessionResponse = z.infer<typeof PortalSessionSchema>;

/**
 * Service pour gérer les sessions billing (checkout & portal)
 */
export const billingService = {
  /**
   * Crée une session checkout Stripe pour un plan donné
   * @param plan Plan de facturation (plus | pro)
   * @param idemKey Clé d'idempotence (UUID v4) générée au clic
   * @returns URL de checkout Stripe
   * @throws ApiError si erreur API (401, 409, etc.)
   * @throws NetworkError si erreur réseau
   * @throws Error si réponse invalide (ZodError)
   */
  async createCheckoutSession(
    plan: BillingPlan,
    idemKey: string
  ): Promise<string> {
    // Vérifier le plan en dev
    assertValidPlan(plan);

    try {
      const response = await http.post<unknown>(
        '/v1/billing/checkout',
        { plan },
        {
          idempotency: true,
          headers: {
            'Idempotency-Key': idemKey,
          },
        }
      );

      // Validation Zod stricte (fail-fast)
      const validated = CheckoutSessionSchema.parse(response);
      return validated.checkout_url;
    } catch (error) {
      // Si c'est une ZodError, enrichir le message
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid checkout response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Crée une session portal Stripe pour gérer l'abonnement
   * @returns URL du portal Stripe
   * @throws ApiError si erreur API (401, etc.)
   * @throws NetworkError si erreur réseau
   * @throws Error si réponse invalide (ZodError)
   */
  async createPortalSession(): Promise<string> {
    try {
      const response = await http.post<unknown>('/v1/billing/portal', {});

      // Validation Zod stricte (fail-fast)
      const validated = PortalSessionSchema.parse(response);
      return validated.portal_url;
    } catch (error) {
      // Si c'est une ZodError, enrichir le message
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid portal response: ${error.message}`);
      }
      throw error;
    }
  },
};

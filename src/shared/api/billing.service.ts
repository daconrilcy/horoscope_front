import { z } from 'zod';
import { http } from './client';
import { assertValidPlan, type BillingPlan } from '@/shared/config/plans';

/**
 * Schémas Zod stricts pour les requêtes billing
 */

/**
 * Schéma pour l'adresse de facturation (si STRIPE_TAX_ENABLED)
 */
const BillingAddressSchema = z.object({
  country: z.string().length(2),
  postal_code: z.string(),
});

/**
 * Schéma pour Tax ID (TVA, etc.)
 */
const TaxIdSchema = z.object({
  type: z.string(),
  value: z.string(),
});

/**
 * Schéma pour le payload de création de session checkout enrichi
 */
export const CheckoutSessionPayloadSchema = z.object({
  plan: z.enum(['plus', 'pro']),
  ab_bucket: z.enum(['A', 'B']).nullable().optional(),
  trial_days: z.number().int().min(1).max(365).optional(),
  coupon: z.string().max(50).optional(),
  address: BillingAddressSchema.optional(),
  tax_ids: z.array(TaxIdSchema).optional(),
});

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
 * Schéma pour le payload de création de session portal
 */
export const PortalSessionPayloadSchema = z.object({
  return_url: z.string().url().optional(),
});

/**
 * Schéma pour la réponse de création de session portal
 */
export const PortalSessionSchema = z.object({
  portal_url: z.string().url(),
});

/**
 * Schéma pour la réponse de vérification de session checkout
 */
export const VerifyCheckoutSessionSchema = z.object({
  status: z.enum(['paid', 'unpaid', 'expired']),
  session_id: z.string(),
  plan: z.enum(['plus', 'pro']).optional(),
});

/**
 * Types inférés depuis les schémas Zod
 */
export type CheckoutSessionPayload = z.infer<
  typeof CheckoutSessionPayloadSchema
>;
export type CheckoutSessionResponse = z.infer<typeof CheckoutSessionSchema>;
export type PortalSessionPayload = z.infer<typeof PortalSessionPayloadSchema>;
export type PortalSessionResponse = z.infer<typeof PortalSessionSchema>;
export type VerifyCheckoutSessionResponse = z.infer<
  typeof VerifyCheckoutSessionSchema
>;
export type BillingAddress = z.infer<typeof BillingAddressSchema>;
export type TaxId = z.infer<typeof TaxIdSchema>;

/**
 * Service pour gérer les sessions billing (checkout & portal)
 */
export const billingService = {
  /**
   * Crée une session checkout Stripe pour un plan donné
   * @param plan Plan de facturation (plus | pro)
   * @param idemKey Clé d'idempotence (UUID v4) générée au clic
   * @param options Options optionnelles (ab_bucket, trial_days, coupon, address, tax_ids)
   * @returns URL de checkout Stripe
   * @throws ApiError si erreur API (401, 409, etc.)
   * @throws NetworkError si erreur réseau
   * @throws Error si réponse invalide (ZodError)
   */
  async createCheckoutSession(
    plan: BillingPlan,
    idemKey: string,
    options?: Partial<CheckoutSessionPayload>
  ): Promise<string> {
    // Vérifier le plan en dev
    assertValidPlan(plan);

    try {
      // Construire le payload avec validation Zod
      const rawPayload: Record<string, unknown> = {
        plan,
        ...(options?.ab_bucket !== undefined && {
          ab_bucket: options.ab_bucket,
        }),
        ...(options?.trial_days !== undefined && {
          trial_days: options.trial_days,
        }),
        ...(options?.coupon != null &&
          options.coupon.trim() !== '' && { coupon: options.coupon.trim() }),
        ...(options?.address && { address: options.address }),
        ...(options?.tax_ids &&
          options.tax_ids.length > 0 && { tax_ids: options.tax_ids }),
      };

      // Normaliser le bucket: 'a'|'b' → 'A'|'B', '' → null
      if (rawPayload.ab_bucket === 'a' || rawPayload.ab_bucket === 'b') {
        rawPayload.ab_bucket = String(rawPayload.ab_bucket).toUpperCase() as
          | 'A'
          | 'B';
      } else if (rawPayload.ab_bucket === '') {
        rawPayload.ab_bucket = null;
      }

      // Validation Zod du payload
      const payload = CheckoutSessionPayloadSchema.parse(rawPayload);

      const response = await http.post<unknown>(
        '/v1/billing/checkout',
        payload,
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
        throw new Error(
          `Invalid checkout payload or response: ${error.message}`
        );
      }
      throw error;
    }
  },

  /**
   * Crée une session portal Stripe pour gérer l'abonnement
   * @param return_url URL de retour (optionnel, utilise BILLING_PORTAL_RETURN_URL si non fournie)
   * @returns URL du portal Stripe
   * @throws ApiError si erreur API (401, etc.)
   * @throws NetworkError si erreur réseau
   * @throws Error si réponse invalide (ZodError)
   */
  async createPortalSession(return_url?: string): Promise<string> {
    try {
      // Construire le payload avec validation Zod
      const payload: Record<string, unknown> = {};
      if (return_url != null && return_url.trim() !== '') {
        payload.return_url = return_url;
      }

      // Validation optionnelle du payload
      const validatedPayload = PortalSessionPayloadSchema.safeParse(payload);

      const response = await http.post<unknown>(
        '/v1/billing/portal',
        validatedPayload.success ? validatedPayload.data : payload
      );

      // Validation Zod stricte (fail-fast)
      const validated = PortalSessionSchema.parse(response);
      return validated.portal_url;
    } catch (error) {
      // Si c'est une ZodError, enrichir le message
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid portal payload or response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Vérifie le statut d'une session checkout Stripe
   * @param session_id ID de la session Stripe (depuis query param)
   * @returns Statut de la session (paid, unpaid, expired) et détails
   * @throws ApiError si erreur API (401, 404, etc.)
   * @throws NetworkError si erreur réseau
   * @throws Error si réponse invalide (ZodError)
   */
  async verifyCheckoutSession(
    session_id: string
  ): Promise<VerifyCheckoutSessionResponse> {
    if (session_id == null || session_id.trim() === '') {
      throw new Error('session_id is required');
    }

    try {
      const response = await http.get<unknown>(
        `/v1/billing/checkout/session?session_id=${encodeURIComponent(session_id)}`
      );

      // Validation Zod stricte (fail-fast)
      const validated = VerifyCheckoutSessionSchema.parse(response);
      return validated;
    } catch (error) {
      // Si c'est une ZodError, enrichir le message
      if (error instanceof z.ZodError) {
        throw new Error(
          `Invalid verify checkout session response: ${error.message}`
        );
      }
      throw error;
    }
  },
};

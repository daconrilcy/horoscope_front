import { z } from 'zod';
import { http } from './client';
import { assertValidPlan, type BillingPlan } from '@/shared/config/plans';

const BillingAddressSchema = z.object({
  country: z.string().length(2),
  postal_code: z.string(),
});

const TaxIdSchema = z.object({
  type: z.string(),
  value: z.string(),
});

export const CheckoutSessionPayloadSchema = z.object({
  plan: z.enum(['plus', 'pro']),
  ab_bucket: z.enum(['A', 'B']).nullable().optional(),
  trial_days: z.number().int().min(1).max(365).optional(),
  coupon: z.string().max(50).optional(),
  address: BillingAddressSchema.optional(),
  tax_ids: z.array(TaxIdSchema).optional(),
});

export const CheckoutSessionSchema = z.object({
  checkout_url: z.string().url(),
});

export const PortalSessionPayloadSchema = z.object({
  return_url: z.string().url().optional(),
});

export const PortalSessionSchema = z.object({
  portal_url: z.string().url(),
});

export type BillingAddress = z.infer<typeof BillingAddressSchema>;
export type TaxId = z.infer<typeof TaxIdSchema>;
export type CheckoutSessionPayload = z.infer<typeof CheckoutSessionPayloadSchema>;
export type CheckoutSessionResponse = z.infer<typeof CheckoutSessionSchema>;
export type PortalSessionPayload = z.infer<typeof PortalSessionPayloadSchema>;
export type PortalSessionResponse = z.infer<typeof PortalSessionSchema>;

export const billingService = {
  async createCheckoutSession(
    plan: BillingPlan,
    idemKey: string,
    options?: Partial<CheckoutSessionPayload>
  ): Promise<string> {
    assertValidPlan(plan);

    try {
      const rawPayload: Record<string, unknown> = {
        plan,
        ...(options?.ab_bucket !== undefined && { ab_bucket: options.ab_bucket }),
        ...(options?.trial_days !== undefined && { trial_days: options.trial_days }),
        ...(options?.coupon != null && options.coupon.trim() !== '' && {
          coupon: options.coupon.trim(),
        }),
        ...(options?.address && { address: options.address }),
        ...(options?.tax_ids && options.tax_ids.length > 0 && {
          tax_ids: options.tax_ids,
        }),
      };

      if (rawPayload.ab_bucket === 'a' || rawPayload.ab_bucket === 'b') {
        rawPayload.ab_bucket = String(rawPayload.ab_bucket).toUpperCase() as 'A' | 'B';
      } else if (rawPayload.ab_bucket === '') {
        rawPayload.ab_bucket = null;
      }

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

      const validated = CheckoutSessionSchema.parse(response);
      return validated.checkout_url;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid checkout payload or response: ${error.message}`);
      }
      throw error;
    }
  },

  async createPortalSession(return_url?: string): Promise<string> {
    try {
      const payload: Record<string, unknown> = {};
      if (return_url != null && return_url !== '') {
        payload.return_url = return_url;
      }

      const validatedPayload = PortalSessionPayloadSchema.safeParse(payload);

      const response = await http.post<unknown>(
        '/v1/billing/portal',
        validatedPayload.success ? validatedPayload.data : payload
      );

      const validated = PortalSessionSchema.parse(response);
      return validated.portal_url;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid portal payload or response: ${error.message}`);
      }
      throw error;
    }
  },
};

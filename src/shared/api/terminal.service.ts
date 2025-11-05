import { z } from 'zod';
import { http } from './client';

/**
 * Schémas Zod pour les réponses Terminal
 */

export const TerminalConnectionSchema = z.object({
  connection_token: z.string(),
  terminal_id: z.string().optional(),
});

export const PaymentIntentSchema = z.object({
  payment_intent_id: z.string(),
  amount: z.number().int(),
  currency: z.string(),
  status: z.enum(['requires_payment_method', 'requires_confirmation', 'succeeded', 'canceled']),
});

export const TerminalProcessResponseSchema = z.object({
  payment_intent_id: z.string(),
  status: z.string(),
  client_secret: z.string().optional(),
});

export const TerminalCaptureResponseSchema = z.object({
  payment_intent_id: z.string(),
  status: z.string(),
  amount_captured: z.number().int(),
});

export const TerminalCancelResponseSchema = z.object({
  payment_intent_id: z.string(),
  status: z.string(),
});

export const TerminalRefundResponseSchema = z.object({
  refund_id: z.string(),
  payment_intent_id: z.string(),
  amount: z.number().int(),
  status: z.string(),
});

/**
 * Types inférés depuis les schémas Zod
 */
export type TerminalConnection = z.infer<typeof TerminalConnectionSchema>;
export type PaymentIntent = z.infer<typeof PaymentIntentSchema>;
export type TerminalProcessResponse = z.infer<typeof TerminalProcessResponseSchema>;
export type TerminalCaptureResponse = z.infer<typeof TerminalCaptureResponseSchema>;
export type TerminalCancelResponse = z.infer<typeof TerminalCancelResponseSchema>;
export type TerminalRefundResponse = z.infer<typeof TerminalRefundResponseSchema>;

/**
 * Service pour gérer le simulateur Stripe Terminal (dev-only)
 * Endpoints : /v1/terminal/*
 */
export const terminalService = {
  /**
   * Connecte au terminal Stripe
   * POST /v1/terminal/connect
   * @returns Token de connexion et terminal_id
   */
  async connect(): Promise<TerminalConnection> {
    try {
      const response = await http.post<unknown>('/v1/terminal/connect', {});
      const validated = TerminalConnectionSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid terminal connection response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Crée un payment intent pour le terminal
   * POST /v1/terminal/payment_intent
   * @param amount Montant en centimes
   * @param currency Devise (ex: 'eur')
   * @returns Payment intent créé
   */
  async createPaymentIntent(
    amount: number,
    currency: string = 'eur'
  ): Promise<PaymentIntent> {
    try {
      const response = await http.post<unknown>('/v1/terminal/payment_intent', {
        amount,
        currency,
      });
      const validated = PaymentIntentSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid payment intent response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Traite un paiement sur le terminal
   * POST /v1/terminal/process
   * @param paymentIntentId ID du payment intent
   * @returns Réponse de traitement
   */
  async process(paymentIntentId: string): Promise<TerminalProcessResponse> {
    try {
      const response = await http.post<unknown>('/v1/terminal/process', {
        payment_intent_id: paymentIntentId,
      });
      const validated = TerminalProcessResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid process response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Capture un paiement
   * POST /v1/terminal/capture
   * @param paymentIntentId ID du payment intent
   * @returns Réponse de capture
   */
  async capture(paymentIntentId: string): Promise<TerminalCaptureResponse> {
    try {
      const response = await http.post<unknown>('/v1/terminal/capture', {
        payment_intent_id: paymentIntentId,
      });
      const validated = TerminalCaptureResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid capture response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Annule un paiement
   * POST /v1/terminal/cancel
   * @param paymentIntentId ID du payment intent
   * @returns Réponse d'annulation
   */
  async cancel(paymentIntentId: string): Promise<TerminalCancelResponse> {
    try {
      const response = await http.post<unknown>('/v1/terminal/cancel', {
        payment_intent_id: paymentIntentId,
      });
      const validated = TerminalCancelResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid cancel response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Rembourse un paiement
   * POST /v1/terminal/refund
   * @param paymentIntentId ID du payment intent
   * @param amount Montant à rembourser en centimes (optionnel, par défaut remboursement total)
   * @returns Réponse de remboursement
   */
  async refund(
    paymentIntentId: string,
    amount?: number
  ): Promise<TerminalRefundResponse> {
    try {
      const payload: Record<string, unknown> = {
        payment_intent_id: paymentIntentId,
      };
      if (amount !== undefined) {
        payload.amount = amount;
      }
      const response = await http.post<unknown>('/v1/terminal/refund', payload);
      const validated = TerminalRefundResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid refund response: ${error.message}`);
      }
      throw error;
    }
  },
};

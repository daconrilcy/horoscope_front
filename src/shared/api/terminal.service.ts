import { z } from 'zod';
import { http } from './client';
import { env } from '@/shared/config/env';

/**
 * Schémas Zod pour les payloads et réponses Terminal
 * Basés sur la documentation Stripe Terminal Testing
 */

export const TerminalConnectSchema = z.object({
  connection_token: z.string(),
});

export const CreatePaymentIntentSchema = z.object({
  client_secret: z.string(),
  payment_intent_id: z.string(),
});

export const ProcessPaymentSchema = z.object({
  status: z.enum(['succeeded', 'requires_payment_method', 'requires_action']),
  payment_intent_id: z.string(),
  error_code: z.string().optional(),
  error_message: z.string().optional(),
});

export const CapturePaymentSchema = z.object({
  status: z.enum(['succeeded', 'processing', 'failed']),
  payment_intent_id: z.string(),
});

export const CancelPaymentSchema = z.object({
  status: z.enum(['canceled', 'failed']),
  payment_intent_id: z.string(),
});

export const RefundPaymentSchema = z.object({
  refund_id: z.string(),
  amount: z.number().int(),
  status: z.enum(['succeeded', 'pending', 'failed']),
});

export type TerminalConnectResponse = z.infer<typeof TerminalConnectSchema>;
export type CreatePaymentIntentResponse = z.infer<
  typeof CreatePaymentIntentSchema
>;
export type ProcessPaymentResponse = z.infer<typeof ProcessPaymentSchema>;
export type CapturePaymentResponse = z.infer<typeof CapturePaymentSchema>;
export type CancelPaymentResponse = z.infer<typeof CancelPaymentSchema>;
export type RefundPaymentResponse = z.infer<typeof RefundPaymentSchema>;

/**
 * Montants de test Stripe Terminal (selon documentation)
 * Les montants doivent être en centimes avec des décimales spécifiques pour déclencher différents scénarios
 */
export const TERMINAL_TEST_AMOUNTS = {
  SUCCESS: 100, // 1.00 EUR - Succès
  SUCCESS_01: 101, // 1.01 EUR - Succès avec PIN offline
  SUCCESS_02: 102, // 1.02 EUR - Succès avec PIN online
  SUCCESS_03: 103, // 1.03 EUR - Succès avec signature
  SUCCESS_05: 105, // 1.05 EUR - Succès avec 3D Secure
  DECLINED: 200, // 2.00 EUR - Carte refusée
  INSUFFICIENT_FUNDS: 201, // 2.01 EUR - Fonds insuffisants
  EXPIRED_CARD: 202, // 2.02 EUR - Carte expirée
  PROCESSING_ERROR: 203, // 2.03 EUR - Erreur de traitement
  OFFLINE_PIN: 255, // 2.55 EUR - PIN offline requis
  ONLINE_PIN: 265, // 2.65 EUR - PIN online requis
  REFUND_TEST: 275, // 2.75 EUR - Montant pour test de remboursement
} as const;

/**
 * Cartes de test Stripe Terminal
 */
export const TERMINAL_TEST_CARDS = {
  SUCCESS: '4242424242424242',
  DECLINED: '4000000000000002',
  INSUFFICIENT_FUNDS: '4000000000009995',
  EXPIRED_CARD: '4000000000000069',
  PROCESSING_ERROR: '4000000000000119',
  OFFLINE_PIN: '4000000000000010',
  ONLINE_PIN: '4000000000000028',
} as const;

/**
 * Service pour Stripe Terminal (dev-only)
 * Simulateur conforme à la documentation Stripe Terminal Testing
 */
export const terminalService = {
  /**
   * Connecte le terminal et récupère un connection_token
   * Endpoint : POST /v1/terminal/connect
   */
  async connect(): Promise<TerminalConnectResponse> {
    if (!(import.meta.env.DEV || env.VITE_DEV_TERMINAL === true)) {
      throw new Error('Terminal service is only available in development');
    }

    try {
      const response = await http.post<unknown>('/v1/terminal/connect', {});

      const validated = TerminalConnectSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid terminal connect response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Crée un PaymentIntent pour le terminal
   * Endpoint : POST /v1/terminal/payment-intent
   * @param amount Montant en centimes (utiliser TERMINAL_TEST_AMOUNTS)
   * @param currency Devise (défaut: 'eur')
   * @param payment_method_types Types de méthodes de paiement (défaut: ['card_present'])
   */
  async createPaymentIntent({
    amount,
    currency = 'eur',
    payment_method_types = ['card_present'],
  }: {
    amount: number;
    currency?: string;
    payment_method_types?: string[];
  }): Promise<CreatePaymentIntentResponse> {
    if (!(import.meta.env.DEV || env.VITE_DEV_TERMINAL === true)) {
      throw new Error('Terminal service is only available in development');
    }

    try {
      const response = await http.post<unknown>('/v1/terminal/payment-intent', {
        amount,
        currency,
        payment_method_types,
      });

      const validated = CreatePaymentIntentSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(
          `Invalid create payment intent response: ${error.message}`
        );
      }
      throw error;
    }
  },

  /**
   * Traite un paiement avec une carte de test
   * Endpoint : POST /v1/terminal/process
   * @param payment_intent_id ID du PaymentIntent
   * @param payment_method Carte de test (utiliser TERMINAL_TEST_CARDS)
   */
  async process({
    payment_intent_id,
    payment_method,
  }: {
    payment_intent_id: string;
    payment_method: string;
  }): Promise<ProcessPaymentResponse> {
    if (!(import.meta.env.DEV || env.VITE_DEV_TERMINAL === true)) {
      throw new Error('Terminal service is only available in development');
    }

    try {
      const response = await http.post<unknown>('/v1/terminal/process', {
        payment_intent_id,
        payment_method,
      });

      const validated = ProcessPaymentSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid process payment response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Capture un paiement (finalise)
   * Endpoint : POST /v1/terminal/capture
   * @param payment_intent_id ID du PaymentIntent
   */
  async capture({
    payment_intent_id,
  }: {
    payment_intent_id: string;
  }): Promise<CapturePaymentResponse> {
    if (!(import.meta.env.DEV || env.VITE_DEV_TERMINAL === true)) {
      throw new Error('Terminal service is only available in development');
    }

    try {
      const response = await http.post<unknown>('/v1/terminal/capture', {
        payment_intent_id,
      });

      const validated = CapturePaymentSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid capture payment response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Annule un paiement
   * Endpoint : POST /v1/terminal/cancel
   * @param payment_intent_id ID du PaymentIntent
   */
  async cancel({
    payment_intent_id,
  }: {
    payment_intent_id: string;
  }): Promise<CancelPaymentResponse> {
    if (!(import.meta.env.DEV || env.VITE_DEV_TERMINAL === true)) {
      throw new Error('Terminal service is only available in development');
    }

    try {
      const response = await http.post<unknown>('/v1/terminal/cancel', {
        payment_intent_id,
      });

      const validated = CancelPaymentSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid cancel payment response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Rembourse un paiement (total ou partiel)
   * Endpoint : POST /v1/terminal/refund
   * @param payment_intent_id ID du PaymentIntent
   * @param amount Montant en centimes (optionnel, si absent = remboursement total)
   */
  async refund({
    payment_intent_id,
    amount,
  }: {
    payment_intent_id: string;
    amount?: number;
  }): Promise<RefundPaymentResponse> {
    if (!(import.meta.env.DEV || env.VITE_DEV_TERMINAL === true)) {
      throw new Error('Terminal service is only available in development');
    }

    try {
      const response = await http.post<unknown>('/v1/terminal/refund', {
        payment_intent_id,
        amount,
      });

      const validated = RefundPaymentSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid refund payment response: ${error.message}`);
      }
      throw error;
    }
  },
};

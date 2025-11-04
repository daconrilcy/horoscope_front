import { z } from 'zod';

/**
 * Schéma de validation pour les variables d'environnement obligatoires
 */
const envRequiredSchema = z.object({
  VITE_API_BASE_URL: z.string().url({
    message: 'VITE_API_BASE_URL must be a valid URL',
  }),
});

/**
 * Schéma de validation pour les variables d'environnement billing (optionnelles)
 * Utilisées en fallback si /v1/config n'est pas disponible
 */
const envBillingSchema = z.object({
  VITE_PUBLIC_BASE_URL: z.string().url().optional(),
  VITE_CHECKOUT_SUCCESS_PATH: z.string().optional(),
  VITE_CHECKOUT_CANCEL_PATH: z.string().optional(),
  VITE_PORTAL_RETURN_URL: z.string().url().optional(),
  VITE_CHECKOUT_TRIALS_ENABLED: z
    .string()
    .transform((val) => val === 'true')
    .optional(),
  VITE_CHECKOUT_COUPONS_ENABLED: z
    .string()
    .transform((val) => val === 'true')
    .optional(),
  VITE_STRIPE_TAX_ENABLED: z
    .string()
    .transform((val) => val === 'true')
    .optional(),
});

/**
 * Schéma de validation pour les outils dev (optionnels)
 */
const envDevSchema = z.object({
  VITE_DEV_TERMINAL: z
    .string()
    .transform((val) => val === 'true')
    .optional(),
});

type EnvRequired = z.infer<typeof envRequiredSchema>;
type EnvBilling = z.infer<typeof envBillingSchema>;
type EnvDev = z.infer<typeof envDevSchema>;

/**
 * Type complet des variables d'environnement
 */
export type Env = EnvRequired & EnvBilling & EnvDev;

/**
 * Parse et valide les variables d'environnement
 * Les variables billing et dev sont optionnelles
 */
function getEnv(): Env {
  const viteApiBaseUrl = import.meta.env.VITE_API_BASE_URL;

  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  const raw = {
    VITE_API_BASE_URL: viteApiBaseUrl,
    // Billing config fallback (optionnel)
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    VITE_PUBLIC_BASE_URL: import.meta.env.VITE_PUBLIC_BASE_URL as
      | string
      | undefined,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    VITE_CHECKOUT_SUCCESS_PATH: import.meta.env.VITE_CHECKOUT_SUCCESS_PATH as
      | string
      | undefined,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    VITE_CHECKOUT_CANCEL_PATH: import.meta.env.VITE_CHECKOUT_CANCEL_PATH as
      | string
      | undefined,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    VITE_PORTAL_RETURN_URL: import.meta.env.VITE_PORTAL_RETURN_URL as
      | string
      | undefined,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    VITE_CHECKOUT_TRIALS_ENABLED: import.meta.env
      .VITE_CHECKOUT_TRIALS_ENABLED as string | undefined,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    VITE_CHECKOUT_COUPONS_ENABLED: import.meta.env
      .VITE_CHECKOUT_COUPONS_ENABLED as string | undefined,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    VITE_STRIPE_TAX_ENABLED: import.meta.env.VITE_STRIPE_TAX_ENABLED as
      | string
      | undefined,
    // Dev tools (optionnel)
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    VITE_DEV_TERMINAL: import.meta.env.VITE_DEV_TERMINAL as string | undefined,
  };

  // Validation stricte des champs obligatoires
  const requiredResult = envRequiredSchema.safeParse(raw);

  if (!requiredResult.success) {
    const errors = requiredResult.error.errors.map((err) => {
      return `${err.path.join('.')}: ${err.message}`;
    });

    throw new Error(
      `❌ Configuration d'environnement invalide:\n${errors.join('\n')}\n\n` +
        'Veuillez définir toutes les variables requises dans votre fichier .env'
    );
  }

  // Validation optionnelle des champs billing et dev
  const billingResult = envBillingSchema.safeParse(raw);
  const devResult = envDevSchema.safeParse(raw);

  return {
    ...requiredResult.data,
    ...(billingResult.success ? billingResult.data : {}),
    ...(devResult.success ? devResult.data : {}),
  };
}

export const env = getEnv();

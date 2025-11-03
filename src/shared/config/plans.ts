/**
 * Plans de facturation centralisés
 * Évite les typos et facilite la maintenance
 */

/**
 * Type strict pour les plans de facturation
 */
export type BillingPlan = 'plus' | 'pro';

/**
 * Constantes pour les plans de facturation
 */
export const PLANS = {
  PLUS: 'plus',
  PRO: 'pro',
} as const;

/**
 * Labels UI pour les plans (séparés de la clé API)
 */
export const PLAN_LABELS: Record<BillingPlan, string> = {
  plus: 'Plus',
  pro: 'Pro',
};

/**
 * Vérifie qu'un plan est valide (uniquement en dev)
 * No-op silencieux en production
 * @param p Plan à valider
 * @throws Error en dev si plan inconnu
 */
export function assertValidPlan(p: string): asserts p is BillingPlan {
  if (import.meta.env.DEV && p !== 'plus' && p !== 'pro') {
    throw new Error(`Unknown plan: ${p}`);
  }
}

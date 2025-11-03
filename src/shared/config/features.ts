/**
 * Clés centralisées pour les features paywall
 * Évite les typos et facilite la maintenance
 */

export const FEATURES = {
  CHAT_MSG_PER_DAY: 'chat.messages/day',
  HORO_TODAY_PREMIUM: 'horoscope.today/premium',
  HORO_NATAL: 'horoscope.natal',
  HORO_PDF_NATAL: 'horoscope.pdf.natal',
  ACCOUNT_EXPORT: 'account.export',
  // Sentinelles pour détection de plan
  PRO_SENTINEL: 'chat.plus', // Feature qui nécessite PRO
  PLUS_SENTINEL: 'horoscope.today/premium', // Feature qui nécessite PLUS
} as const;

/**
 * Type pour les clés de features valides
 */
export type FeatureKey = (typeof FEATURES)[keyof typeof FEATURES];

/**
 * Vérifie qu'une clé de feature est valide (uniquement en dev)
 * No-op en production
 */
export function assertValidFeatureKey(feature: string): void {
  if (import.meta.env.DEV) {
    const validKeys = Object.values(FEATURES);
    if (!validKeys.includes(feature as FeatureKey)) {
      console.warn(
        `Unknown feature key: ${feature}. Valid keys: ${validKeys.join(', ')}`
      );
    }
  }
}

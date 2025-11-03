import { FEATURES } from '@/shared/config/features';
import { useMultiPaywall } from './useMultiPaywall';

export type Plan = 'free' | 'plus' | 'pro';

/**
 * Résultat du hook usePlan
 */
export interface UsePlanResult {
  /** Plan actuel dérivé via sentinelles */
  plan: Plan;
  /** Indique si la requête est en cours */
  isLoading: boolean;
}

/**
 * Hook pour dériver le plan actuel en testant des features sentinelles
 * Utilise une logique heuristique :
 * - allowed(PRO_SENTINEL) → plan: 'pro'
 * - allowed(PLUS_SENTINEL) → plan: 'plus'
 * - Sinon → plan: 'free'
 * @returns Plan dérivé + isLoading
 */
export function usePlan(): UsePlanResult {
  const { results, isLoadingAny } = useMultiPaywall([
    FEATURES.PRO_SENTINEL,
    FEATURES.PLUS_SENTINEL,
  ]);

  const proDecision = results[0];
  const plusDecision = results[1];

  // Logique heuristique : pro > plus > free
  const proAllowed = proDecision?.isAllowed === true;
  const plusAllowed = plusDecision?.isAllowed === true;

  let plan: Plan = 'free';
  if (proAllowed) {
    plan = 'pro';
  } else if (plusAllowed) {
    plan = 'plus';
  }

  return {
    plan,
    isLoading: isLoadingAny,
  };
}

import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import {
  paywallService,
  type PaywallDecision,
} from '@/shared/api/paywall.service';

/**
 * Résultat du hook usePaywall avec helpers
 */
export interface UsePaywallResult {
  /** Données brutes de la réponse paywall */
  data?: PaywallDecision;
  /** Indique si la requête est en cours */
  isLoading: boolean;
  /** Erreur de la requête */
  error: Error | null;
  /** Indique si la feature est autorisée */
  isAllowed: boolean;
  /** Raison du blocage (si allowed: false) */
  reason?: 'plan' | 'rate';
  /** URL d'upgrade (si disponible) */
  upgradeUrl?: string;
  /** Nombre de secondes avant retry (si 429) */
  retryAfter?: number;
  /** Objet query React Query complet */
  query: UseQueryResult<PaywallDecision, Error>;
}

/**
 * Hook React Query pour vérifier l'autorisation d'une feature paywall
 * @param feature Clé de la feature à vérifier
 * @returns Résultat avec isAllowed, reason, upgradeUrl, retryAfter
 */
export function usePaywall(feature: string): UsePaywallResult {
  const query = useQuery<PaywallDecision, Error>({
    queryKey: ['paywall', feature],
    queryFn: () => paywallService.decision(feature),
    staleTime: 5_000, // 5 secondes
    gcTime: 60_000, // 60 secondes (ancien cacheTime)
    retry: false, // 402/429 ne doivent pas retenter
    refetchOnWindowFocus: false, // Évite de spammer l'endpoint
  });

  const data = query.data;
  const error = query.error;

  // Extraire retryAfter depuis le body si 429
  // Note: Retry-After depuis headers est déjà extrait dans client.ts et propagé
  // via l'événement paywall:rate, mais React Query ne donne pas accès direct aux headers
  // Donc on utilise retry_after depuis le body (déjà fusionné avec header Retry-After dans client.ts)
  let retryAfter: number | undefined;
  if (data && !data.allowed && 'retry_after' in data) {
    retryAfter = (data as { retry_after?: number }).retry_after;
  }

  return {
    data,
    isLoading: query.isLoading,
    error: error ?? null,
    isAllowed: data?.allowed === true,
    reason: data?.allowed === false ? data.reason : undefined,
    upgradeUrl: data?.allowed === false ? data.upgrade_url : undefined,
    retryAfter,
    query,
  };
}

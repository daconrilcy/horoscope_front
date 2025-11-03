import { useQueries } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';
import { paywallService } from '@/shared/api/paywall.service';
import type { PaywallDecision } from '@/shared/api/paywall.service';

/**
 * Résultat d'une feature pour useMultiPaywall
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
 * Résultat du hook useMultiPaywall avec helpers agrégés
 */
export interface UseMultiPaywallResult {
  /** Tableau des résultats pour chaque feature */
  results: UsePaywallResult[];
  /** Indique si au moins une requête est en cours */
  isLoadingAny: boolean;
  /** Indique si au moins une requête a échoué */
  isErrorAny: boolean;
}

/**
 * Hook React Query pour vérifier l'autorisation de plusieurs features en parallèle
 * Utilise useQueries pour faire des requêtes parallèles (pas séquentielles)
 * @param features Tableau de clés de features à vérifier
 * @returns Résultat avec tableau de résultats + isLoadingAny + isErrorAny
 */
export function useMultiPaywall(features: string[]): UseMultiPaywallResult {
  const queries = useQueries({
    queries: features.map((feature) => ({
      queryKey: ['paywall', feature],
      queryFn: () => paywallService.decision(feature),
      staleTime: 5_000, // 5 secondes
      gcTime: 60_000, // 60 secondes
      retry: false, // 402/429 ne doivent pas retenter
      refetchOnWindowFocus: false, // Évite de spammer l'endpoint
    })),
  });

  // Transformer chaque query en UsePaywallResult
  const results: UsePaywallResult[] = queries.map((query) => {
    const data = query.data;
    const error = query.error;

    // Extraire retryAfter depuis data si disponible
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
  });

  const isLoadingAny = queries.some((q) => q.isLoading);
  const isErrorAny = queries.some((q) => q.isError);

  return {
    results,
    isLoadingAny,
    isErrorAny,
  };
}

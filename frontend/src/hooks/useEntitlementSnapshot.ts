import { useQuery } from "@tanstack/react-query"
import {
  fetchEntitlementsSnapshot,
  type EntitlementsSnapshot,
  type FeatureEntitlementResponse,
  type UpgradeHint,
  BillingApiError,
} from "../api/billing"
import { useAccessTokenSnapshot, getSubjectFromAccessToken } from "../utils/authToken"

const ANONYMOUS_SUBJECT = "anonymous"

/**
 * Hook généraliste exposant le snapshot complet des droits de l'utilisateur.
 * Centralise la consommation de /v1/entitlements/me.
 * La clé inclut le sujet du token pour éviter la réutilisation de cache après changement de compte.
 */
export function useEntitlementsSnapshot() {
  const token = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(token) ?? ANONYMOUS_SUBJECT

  return useQuery<EntitlementsSnapshot, BillingApiError>({
    queryKey: ["entitlements-me", tokenSubject],
    queryFn: fetchEntitlementsSnapshot,
    staleTime: 2 * 60 * 1000, // 2 minutes (AC5)
    enabled: !!token,
    retry: (failureCount, error) => {
      if (error instanceof BillingApiError && error.status === 403) return false
      return failureCount < 1
    },
  })
}

/**
 * Sélecteur pour récupérer un hint d'upgrade spécifique à une feature.
 */
export function useUpgradeHint(featureCode: string): UpgradeHint | undefined {
  const { data } = useEntitlementsSnapshot()
  return data?.upgrade_hints?.find((h) => h.feature_code === featureCode)
}

/**
 * Sélecteur pour récupérer l'accès effectif à une feature.
 */
export function useFeatureAccess(featureCode: string): FeatureEntitlementResponse | undefined {
  const { data } = useEntitlementsSnapshot()
  return data?.features?.find((f) => f.feature_code === featureCode)
}

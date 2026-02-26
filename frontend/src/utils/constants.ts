/**
 * Label affiché à l'utilisateur pour le timeout de génération du thème natal.
 * @note Cette valeur doit rester synchronisée avec le timeout backend configuré dans
 * `backend/app/services/natal_chart_service.py` (GENERATION_TIMEOUT_SECONDS).
 */
export const GENERATION_TIMEOUT_LABEL = "60s"
/** Subject fallback pour les utilisateurs non authentifiés dans les query keys */
export const ANONYMOUS_SUBJECT = "anonymous"

/**
 * Formate un lieu de naissance à partir de la ville et du pays.
 * Utilisé comme fallback quand le géocodage échoue ou ne retourne pas de display_name.
 * @param city - Nom de la ville de naissance
 * @param country - Nom du pays de naissance
 * @returns Chaîne formatée "ville, pays" (ex: "Paris, France")
 */
export function formatBirthPlace(city: string, country: string): string {
  return `${city}, ${country}`
}

/** Interface commune pour les erreurs API avec requestId (ApiError, BirthProfileApiError, etc.) */
export interface ErrorWithRequestId {
  requestId?: string
}

/**
 * Loggue un request ID pour le support technique.
 * Utilisé pour les erreurs API afin de faciliter le debug sans exposer l'ID à l'utilisateur.
 * @param errorOrRequestId - Soit une erreur avec propriété requestId, soit le requestId directement, soit undefined
 * @note Si undefined ou si requestId est absent/vide, la fonction ne loggue rien (silencieux par design)
 */
export function logSupportRequestId(errorOrRequestId: ErrorWithRequestId | string | undefined): void {
  const requestId = typeof errorOrRequestId === "string" ? errorOrRequestId : errorOrRequestId?.requestId
  if (requestId) {
    console.error(`[Support] Request ID: ${requestId}`)
  }
}

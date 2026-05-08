// Regroupe les decisions partagees de journalisation support pour les erreurs API.
import type { ApiError } from "../api/client"

/** Indique si une erreur API merite une trace support cote UI. */
export function shouldLogSupportForApiError(error: Pick<ApiError, "status">): boolean {
  return error.status >= 500
}

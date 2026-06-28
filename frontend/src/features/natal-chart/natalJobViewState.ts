// Résolution pure de l'état d'affichage du job Astral natal.
import type { AstralJobResponse } from "../../api/astral"

const ASTRAL_TERMINAL_ERROR_STATUSES = new Set(["failed", "safety_rejected", "cancelled", "expired"])

export type NatalJobViewState =
  | "transport-error"
  | "working"
  | "completed"
  | "terminal-error"
  | "idle"

type ResolveNatalJobViewStateParams = {
  hasTransportError: boolean
  isWorking: boolean
  currentJob?: AstralJobResponse
}

/** Normalise les statuts Astral techniques en états UI stables. */
export function resolveNatalJobViewState({
  hasTransportError,
  isWorking,
  currentJob,
}: ResolveNatalJobViewStateParams): NatalJobViewState {
  if (hasTransportError) return "transport-error"
  if (isWorking) return "working"
  if (currentJob?.status === "completed") return "completed"
  if (currentJob?.status && ASTRAL_TERMINAL_ERROR_STATUSES.has(currentJob.status)) {
    return "terminal-error"
  }
  return "idle"
}

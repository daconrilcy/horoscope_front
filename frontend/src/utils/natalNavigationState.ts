// État de navigation utilisé pour restaurer automatiquement un thème natal existant.

export const NATAL_AUTO_OPEN_NAVIGATION_STATE = {
  autoOpenExistingNatal: true,
} as const

/** Indique si la navigation courante doit tenter de restaurer le thème natal existant. */
export function shouldAutoOpenExistingNatal(state: unknown): boolean {
  return Boolean(
    state &&
    typeof state === "object" &&
    "autoOpenExistingNatal" in state &&
    state.autoOpenExistingNatal === true,
  )
}

// Centralise le positionnement UX des guides pour garder le matching coherent.
import type { Astrologer } from "@api/astrologers"

export type AstrologerTheme = "etienne" | "luna" | "nox" | "orion" | "atlas" | "selene" | "default"

export type AstrologerIntentKey = "beginner" | "love" | "career" | "decision" | "inner_work" | "full_reading"

export type AstrologerIntentOption = {
  key: AstrologerIntentKey
  labelKey: string
}

const INTENT_MATCHES: Record<AstrologerIntentKey, AstrologerTheme[]> = {
  beginner: ["etienne"],
  love: ["luna", "selene"],
  career: ["orion", "atlas"],
  decision: ["atlas", "orion"],
  inner_work: ["nox", "selene"],
  full_reading: ["etienne", "orion", "nox"],
}

export const ASTROLOGER_INTENT_OPTIONS: AstrologerIntentOption[] = [
  { key: "beginner", labelKey: "intent_beginner" },
  { key: "love", labelKey: "intent_love" },
  { key: "career", labelKey: "intent_career" },
  { key: "decision", labelKey: "intent_decision" },
  { key: "inner_work", labelKey: "intent_inner_work" },
  { key: "full_reading", labelKey: "intent_full_reading" },
]

/** Deduit le theme stable d'un guide a partir de son prenom public. */
export function getAstrologerTheme(expert: Astrologer): AstrologerTheme {
  const firstName = expert.first_name.toLowerCase()
  if (firstName === "étienne" || firstName === "etienne") return "etienne"
  if (firstName === "luna") return "luna"
  if (firstName === "nox") return "nox"
  if (firstName === "orion") return "orion"
  if (firstName === "atlas") return "atlas"
  if (firstName === "sélène" || firstName === "selene") return "selene"
  return "default"
}

/** Associe au theme une icone decorative courte pour la carte catalogue. */
export function getAstrologerIcon(theme: AstrologerTheme): string {
  switch (theme) {
    case "etienne":
      return "✦"
    case "luna":
      return "❤"
    case "nox":
      return "☽"
    case "orion":
      return "✺"
    case "atlas":
      return "⚡"
    case "selene":
      return "☼"
    default:
      return "✦"
  }
}

/** Retourne la cle i18n du badge principal propre a chaque guide. */
export function getAstrologerFeaturedBadgeKey(expert: Astrologer): string {
  return `featured_${getAstrologerTheme(expert)}`
}

/** Retourne la cle i18n de la phrase benefice affichee sur la carte. */
export function getAstrologerBenefitKey(expert: Astrologer): string {
  return `card_benefit_${getAstrologerTheme(expert)}`
}

/** Indique si le guide correspond a l'intention choisie dans le module d'orientation. */
export function isAstrologerMatchingIntent(expert: Astrologer, intentKey: AstrologerIntentKey): boolean {
  return INTENT_MATCHES[intentKey].includes(getAstrologerTheme(expert))
}

/** Identifie le guide pedagogique a mettre en avant pour les nouveaux utilisateurs. */
export function isAstrologerRecommendedStarter(expert: Astrologer): boolean {
  return getAstrologerTheme(expert) === "etienne"
}

import type { AstrologyLang } from './astrology'

export type InsightId = "amour" | "travail" | "energie"

export type InsightTranslation = {
  title: string
  description: string
}

const insightTranslations: Record<AstrologyLang, Record<InsightId, InsightTranslation>> = {
  fr: {
    amour: { title: "Amour", description: "Balance dans ta relation" },
    travail: { title: "Travail", description: "Nouvelle opportunité à saisir" },
    energie: { title: "Énergie", description: "Énergie haute, humeur positive" },
  },
  en: {
    amour: { title: "Love", description: "Balance in your relationship" },
    travail: { title: "Work", description: "New opportunity to seize" },
    energie: { title: "Energy", description: "High energy, positive mood" },
  },
  es: {
    amour: { title: "Amor", description: "Equilibrio en tu relación" },
    travail: { title: "Trabajo", description: "Nueva oportunidad para aprovechar" },
    energie: { title: "Energía", description: "Energía alta, humor positivo" },
  },
}

export const INSIGHT_SECTION_TRANSLATIONS: Record<AstrologyLang, { title: string; ariaLabel: string }> = {
  fr: { title: "Amour", ariaLabel: "Voir tous les insights amour" },
  en: { title: "Love", ariaLabel: "View all love insights" },
  es: { title: "Amor", ariaLabel: "Ver todos los insights de amor" },
}

export function translateInsight(
  insightId: InsightId,
  locale: AstrologyLang = "fr"
): InsightTranslation {
  return insightTranslations[locale]?.[insightId] ?? insightTranslations.fr[insightId]
}

export function translateInsightSection(locale: AstrologyLang = "fr") {
  return INSIGHT_SECTION_TRANSLATIONS[locale] ?? INSIGHT_SECTION_TRANSLATIONS.fr
}

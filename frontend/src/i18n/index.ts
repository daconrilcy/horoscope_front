import { useAstrologyLabels } from "./astrology"
import { authTranslations, type AuthTranslation } from "./auth"
import { commonTranslations, type CommonTranslation } from "./common"
import { navigationTranslations, type NavigationTranslation } from "./navigation"
import { translateDashboardPage, type DashboardPageTranslation } from "./dashboard"
import { settingsTranslations, type SettingsTranslation } from "./settings"
import { translateAdmin, type AdminTranslation } from "./admin"
import { natalChartTranslations, type NatalChartTranslation } from "./natalChart"
import { birthProfileTranslations, type BirthProfileTranslation } from "./birthProfile"
import { billingTranslations, type BillingTranslation } from "./billing"
import { TONE_LABELS, CATEGORY_LABELS, PREDICTION_UI_MESSAGES, type Lang as PredictionsLang } from "./predictions"
import { tConsultations, type ConsultationsTranslation } from "./consultations"
import { tAstrologers, type AstrologersTranslation } from "./astrologers"
import { translateInsight, translateInsightSection, type InsightsTranslation, type InsightId } from "./insights"
import { supportTranslations } from "./support"
import { landingTranslations, type LandingTranslation } from "./landing"
import type { AppLocale } from "./types"

export * from "./types"
export * from "./astrology"
export * from "./auth"
export * from "./common"
export * from "./navigation"
export * from "./dashboard"
export * from "./predictions"
export * from "./natalChart"
export * from "./birthProfile"
export * from "./billing"
export * from "./settings"
export * from "./consultations"
export * from "./astrologers"
export * from "./admin"
export * from "./insights"
export * from "./support"
export * from "./landing"

export type TranslationMap = {
  auth: AuthTranslation
  common: CommonTranslation
  navigation: NavigationTranslation
  dashboard: DashboardPageTranslation
  settings: SettingsTranslation
  admin: AdminTranslation
  natalChart: NatalChartTranslation
  birthProfile: BirthProfileTranslation
  billing: BillingTranslation
  predictions: {
    getToneLabel: (tone: string) => string
    getMessage: (key: string) => string
    getCategoryLabel: (cat: string) => string
  }
  consultations: ConsultationsTranslation
  astrologers: AstrologersTranslation
  insights: InsightsTranslation
  support: any
  landing: LandingTranslation
}

export type TranslationNamespace = keyof TranslationMap

const translationFunctions: {
  [K in TranslationNamespace]: (lang: AppLocale) => TranslationMap[K]
} = {
  auth: authTranslations,
  common: commonTranslations,
  navigation: navigationTranslations,
  dashboard: translateDashboardPage,
  settings: (lang) => settingsTranslations.page[lang],
  admin: translateAdmin,
  natalChart: (lang) => natalChartTranslations[lang],
  birthProfile: (lang) => birthProfileTranslations[lang],
  billing: billingTranslations,
  predictions: (lang) => {
    const l: PredictionsLang = lang === 'es' ? 'fr' : lang
    return {
      getToneLabel: (tone: string) => TONE_LABELS[tone]?.[l] ?? tone,
      getMessage: (key: string) => PREDICTION_UI_MESSAGES[key as keyof typeof PREDICTION_UI_MESSAGES]?.[l] ?? key,
      getCategoryLabel: (cat: string) => CATEGORY_LABELS[cat]?.[l] ?? cat,
    }
  },
  consultations: (lang) => ({ t: (key: string) => tConsultations(key, lang) }),
  astrologers: (lang) => ({ t: (key: string) => tAstrologers(key, lang) }),
  insights: (lang) => ({ 
    translate: (id: InsightId) => translateInsight(id, lang),
    section: () => translateInsightSection(lang)
  }),
  support: (lang) => supportTranslations[lang] as any,
  landing: landingTranslations,
}

/**
 * Hook to access translated strings for a specific namespace.
 * Story 52.4 implementation.
 */
export function useTranslation<N extends TranslationNamespace>(namespace: N): TranslationMap[N] {
  const { lang } = useAstrologyLabels()
  return translationFunctions[namespace](lang) as TranslationMap[N]
}

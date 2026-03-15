import { useAstrologyLabels, detectLang } from "./astrology"
import { authTranslations, type AuthTranslation } from "./auth"
import { commonTranslations, type CommonTranslation } from "./common"
import { navigationTranslations, type NavigationTranslation } from "./navigation"
import { translateDashboardPage, type DashboardPageTranslation } from "./dashboard"
import { settingsTranslations, type SettingsTranslation } from "./settings"
import { adminTranslations, translateAdmin, type AdminTranslation } from "./admin"
import { natalChartTranslations, type NatalChartTranslation } from "./natalChart"
import { birthProfileTranslations, type BirthProfileTranslation } from "./birthProfile"
import { predictionsTranslations, type PredictionsTranslation } from "./predictions"
import { tConsultations, type ConsultationsTranslation } from "./consultations"
import { tAstrologers, type AstrologersTranslation } from "./astrologers"
import { translateInsight, translateInsightSection, type InsightsTranslation } from "./insights"
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
export * from "./settings"
export * from "./consultations"
export * from "./astrologers"
export * from "./admin"
export * from "./insights"

export type TranslationMap = {
  auth: AuthTranslation
  common: CommonTranslation
  navigation: NavigationTranslation
  dashboard: DashboardPageTranslation
  settings: SettingsTranslation
  admin: AdminTranslation
  natalChart: NatalChartTranslation
  birthProfile: BirthProfileTranslation
  predictions: PredictionsTranslation
  consultations: ConsultationsTranslation
  astrologers: AstrologersTranslation
  insights: InsightsTranslation
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
  natalChart: natalChartTranslations,
  birthProfile: birthProfileTranslations,
  predictions: (lang) => ({
    getToneLabel: (tone: any) => predictionsTranslations.tones[tone][lang],
    getToneColor: (tone: any) => predictionsTranslations.toneColors[tone],
    getMessage: (key: any) => predictionsTranslations.messages[key][lang],
    getCategoryLabel: (cat: any) => predictionsTranslations.categories[cat][lang]
  }) as any,
  consultations: (lang) => ({ t: (key: string) => tConsultations(key, lang) }) as any,
  astrologers: (lang) => ({ t: (key: string) => tAstrologers(key, lang) }) as any,
  insights: (lang) => ({ 
    translate: (id: any) => translateInsight(id, lang),
    section: () => translateInsightSection(lang)
  }) as any,
}

/**
 * Hook to access translated strings for a specific namespace.
 * Story 52.4 implementation.
 */
export function useTranslation<N extends TranslationNamespace>(namespace: N): TranslationMap[N] {
  const { lang } = useAstrologyLabels()
  return translationFunctions[namespace](lang) as TranslationMap[N]
}

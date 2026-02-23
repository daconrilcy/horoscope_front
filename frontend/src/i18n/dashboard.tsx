export type SupportedLocale = "fr" | "en" | "es"

export type DashboardCardId = "natal" | "chat" | "consultations" | "astrologers" | "settings"

type DashboardCardTranslation = {
  label: string
  description: string
}

const dashboardCardTranslations: Record<SupportedLocale, Record<DashboardCardId, DashboardCardTranslation>> = {
  fr: {
    natal: { label: "Mon thème astral", description: "Consultez votre thème natal" },
    chat: { label: "Chat astrologue", description: "Discutez avec votre astrologue" },
    consultations: { label: "Consultations", description: "Vos consultations passées" },
    astrologers: { label: "Astrologues", description: "Nos astrologues" },
    settings: { label: "Paramètres", description: "Gérez vos préférences" },
  },
  en: {
    natal: { label: "My birth chart", description: "View your natal chart" },
    chat: { label: "Astrologer chat", description: "Chat with your astrologer" },
    consultations: { label: "Consultations", description: "Your past consultations" },
    astrologers: { label: "Astrologers", description: "Our astrologers" },
    settings: { label: "Settings", description: "Manage your preferences" },
  },
  es: {
    natal: { label: "Mi carta natal", description: "Consulta tu carta natal" },
    chat: { label: "Chat astrólogo", description: "Habla con tu astrólogo" },
    consultations: { label: "Consultas", description: "Tus consultas pasadas" },
    astrologers: { label: "Astrólogos", description: "Nuestros astrólogos" },
    settings: { label: "Ajustes", description: "Gestiona tus preferencias" },
  },
}

const dashboardPageTranslations: Record<SupportedLocale, { title: string; welcome: string }> = {
  fr: { title: "Tableau de bord", welcome: "Bienvenue ! Accédez rapidement à toutes les fonctionnalités." },
  en: { title: "Dashboard", welcome: "Welcome! Quickly access all features." },
  es: { title: "Panel", welcome: "¡Bienvenido! Accede rápidamente a todas las funciones." },
}

export function translateDashboardCard(
  cardId: DashboardCardId,
  locale: SupportedLocale = "fr"
): DashboardCardTranslation {
  return dashboardCardTranslations[locale]?.[cardId] ?? dashboardCardTranslations.fr[cardId]
}

export function translateDashboardPage(locale: SupportedLocale = "fr"): { title: string; welcome: string } {
  return dashboardPageTranslations[locale] ?? dashboardPageTranslations.fr
}

export const DASHBOARD_CARD_IDS: DashboardCardId[] = ["natal", "chat", "consultations", "astrologers", "settings"]

export const DASHBOARD_CARD_PATHS: Record<DashboardCardId, string> = {
  natal: "/natal",
  chat: "/chat",
  consultations: "/consultations",
  astrologers: "/astrologers",
  settings: "/settings",
}

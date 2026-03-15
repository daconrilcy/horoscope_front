import type { AppLocale } from "./types"

export type SupportedLocale = AppLocale

export type DashboardCardId = "natal" | "chat" | "consultations" | "astrologers" | "settings"

type DashboardCardTranslation = {
  label: string
  description: string
}

export type DashboardPageTranslation = {
  title: string
  welcome: string
  viewHoroscope: string
  noPrediction: string
  errorPrediction: string
  retry: string
  summaryLoading: string
  activities: string
  shortcuts: {
    chatTitle: string
    chatSubtitle: string
    consultationTitle: string
    consultationSubtitle: string
    historyTitle: string
    historySubtitle: string
  }
  header: {
    kicker: string
    title: string
    backToDashboard: string
    switchToLight: string
    switchToDark: string
    profileLoading: string
    profileOf: (displayName: string) => string
  }
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

const dashboardPageTranslations: Record<SupportedLocale, DashboardPageTranslation> = {
  fr: { 
    title: "Tableau de bord", 
    welcome: "Bienvenue ! Accédez rapidement à toutes les fonctionnalités.",
    viewHoroscope: "Voir l'horoscope complet",
    noPrediction: "Aucune prédiction disponible.",
    errorPrediction: "Impossible de charger le résumé du jour.",
    retry: "Réessayer",
    summaryLoading: "Chargement du résumé du jour...",
    activities: "Activités",
    shortcuts: {
      chatTitle: "Chat astrologue",
      chatSubtitle: "En ligne",
      consultationTitle: "Consultation",
      consultationSubtitle: "Guidance ciblée",
      historyTitle: "Historique",
      historySubtitle: "Mes prédictions",
    },
    header: {
      kicker: "Aujourd'hui",
      title: "Horoscope",
      backToDashboard: "Retour au tableau de bord",
      switchToLight: "Passer en mode clair",
      switchToDark: "Passer en mode sombre",
      profileLoading: "Chargement du profil",
      profileOf: (displayName: string) => `Profil de ${displayName}`,
    },
  },
  en: { 
    title: "Dashboard", 
    welcome: "Welcome! Quickly access all features.",
    viewHoroscope: "View full horoscope",
    noPrediction: "No prediction available.",
    errorPrediction: "Unable to load today's summary.",
    retry: "Retry",
    summaryLoading: "Loading today's summary...",
    activities: "Activities",
    shortcuts: {
      chatTitle: "Astrologer chat",
      chatSubtitle: "Online",
      consultationTitle: "Consultation",
      consultationSubtitle: "Targeted guidance",
      historyTitle: "History",
      historySubtitle: "My predictions",
    },
    header: {
      kicker: "Today",
      title: "Horoscope",
      backToDashboard: "Back to dashboard",
      switchToLight: "Switch to light mode",
      switchToDark: "Switch to dark mode",
      profileLoading: "Loading profile",
      profileOf: (displayName: string) => `${displayName}'s profile`,
    },
  },
  es: { 
    title: "Panel", 
    welcome: "¡Bienvenido! Accede rápidamente a todas las funciones.",
    viewHoroscope: "Ver horóscopo completo",
    noPrediction: "No hay predicción disponible.",
    errorPrediction: "No se puede cargar el resumen de hoy.",
    retry: "Reintentar",
    summaryLoading: "Cargando el resumen de hoy...",
    activities: "Actividades",
    shortcuts: {
      chatTitle: "Chat astrólogo",
      chatSubtitle: "En línea",
      consultationTitle: "Consulta",
      consultationSubtitle: "Guía enfocada",
      historyTitle: "Historial",
      historySubtitle: "Mis predicciones",
    },
    header: {
      kicker: "Hoy",
      title: "Horóscopo",
      backToDashboard: "Volver al panel",
      switchToLight: "Cambiar a modo claro",
      switchToDark: "Cambiar a modo oscuro",
      profileLoading: "Cargando perfil",
      profileOf: (displayName: string) => `Perfil de ${displayName}`,
    },
  },
}

export function translateDashboardCard(
  cardId: DashboardCardId,
  locale: SupportedLocale = "fr"
): DashboardCardTranslation {
  return dashboardCardTranslations[locale]?.[cardId] ?? dashboardCardTranslations.fr[cardId]
}

export function translateDashboardPage(locale: SupportedLocale = "fr"): DashboardPageTranslation {
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

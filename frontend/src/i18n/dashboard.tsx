import type { AppLocale } from "./types"

export type SupportedLocale = AppLocale

export type DashboardCardId = "natal" | "astrologers" | "settings"

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
    natalTitle: string
    natalSubtitle: string
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
    astrologers: { label: "Astrologues", description: "Nos astrologues" },
    settings: { label: "Paramètres", description: "Gérez vos préférences" },
  },
  en: {
    natal: { label: "My birth chart", description: "View your natal chart" },
    astrologers: { label: "Astrologers", description: "Our astrologers" },
    settings: { label: "Settings", description: "Manage your preferences" },
  },
  es: {
    natal: { label: "Mi carta natal", description: "Consulta tu carta natal" },
    astrologers: { label: "Astrólogos", description: "Nuestros astrólogos" },
    settings: { label: "Ajustes", description: "Gestiona tus preferencias" },
  },
  de: {
    natal: { label: "Mein Geburtshoroskop", description: "Ihr Geburtshoroskop ansehen" },
    astrologers: { label: "Astrologen", description: "Unsere Astrologen" },
    settings: { label: "Einstellungen", description: "Ihre Präferenzen verwalten" },
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
    summaryLoading: "Horoscope du jour en cours de rédaction",
    activities: "Activités",
    shortcuts: {
      natalTitle: "Thème natal",
      natalSubtitle: "Lecture Astral",
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
    summaryLoading: "Today's horoscope is being written",
    activities: "Activities",
    shortcuts: {
      natalTitle: "Natal chart",
      natalSubtitle: "Astral reading",
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
    summaryLoading: "El horóscopo del día se está redactando",
    activities: "Actividades",
    shortcuts: {
      natalTitle: "Carta natal",
      natalSubtitle: "Lectura Astral",
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
  de: {
    title: "Dashboard",
    welcome: "Willkommen! Greifen Sie schnell auf alle Funktionen zu.",
    viewHoroscope: "Vollständiges Horoskop ansehen",
    noPrediction: "Keine Vorhersage verfügbar.",
    errorPrediction: "Die Tageszusammenfassung konnte nicht geladen werden.",
    retry: "Erneut versuchen",
    summaryLoading: "Das Tageshoroskop wird gerade geschrieben",
    activities: "Aktivitäten",
    shortcuts: {
      natalTitle: "Geburtshoroskop",
      natalSubtitle: "Astral-Lesung",
      historyTitle: "Verlauf",
      historySubtitle: "Meine Vorhersagen",
    },
    header: {
      kicker: "Heute",
      title: "Horoskop",
      backToDashboard: "Zurück zum Dashboard",
      switchToLight: "Zum hellen Modus wechseln",
      switchToDark: "Zum dunklen Modus wechseln",
      profileLoading: "Profil wird geladen",
      profileOf: (displayName: string) => `Profil von ${displayName}`,
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

export const DASHBOARD_CARD_IDS: DashboardCardId[] = ["natal", "astrologers", "settings"]

export const DASHBOARD_CARD_PATHS: Record<DashboardCardId, string> = {
  natal: "/natal",
  astrologers: "/astrologers",
  settings: "/settings",
}

import type { AstrologyLang } from "./astrology"

export interface NavigationTranslation {
  nav: {
    today: string
    chat: string
    natal: string
    consultations: string
    astrologers: string
    help: string
    profile: string
    privacy: string
    support: string
    monitoring: string
    reconciliation: string
    ent_api: string
    ent_astro: string
    ent_usage: string
    ent_editorial: string
    ent_billing: string
  }
}

const translations: Record<AstrologyLang, NavigationTranslation> = {
  fr: {
    nav: {
      today: "Aujourd'hui",
      chat: "Chat",
      natal: "Thème",
      consultations: "Consultations",
      astrologers: "Astrologues",
      help: "Support",
      profile: "Profil",
      privacy: "Confidentialité",
      support: "Support",
      monitoring: "Monitoring",
      reconciliation: "Réconciliation",
      ent_api: "API",
      ent_astro: "Astrologie",
      ent_usage: "Usage",
      ent_editorial: "Éditorial",
      ent_billing: "Facturation",
    },
  },
  en: {
    nav: {
      today: "Today",
      chat: "Chat",
      natal: "Chart",
      consultations: "Consultations",
      astrologers: "Astrologers",
      help: "Support",
      profile: "Profile",
      privacy: "Privacy",
      support: "Support",
      monitoring: "Monitoring",
      reconciliation: "Reconciliation",
      ent_api: "API",
      ent_astro: "Astrology",
      ent_usage: "Usage",
      ent_editorial: "Editorial",
      ent_billing: "Billing",
    },
  },
  es: {
    nav: {
      today: "Hoy",
      chat: "Chat",
      natal: "Carta",
      consultations: "Consultaciones",
      astrologers: "Astrólogos",
      help: "Soporte",
      profile: "Perfil",
      privacy: "Privacidad",
      support: "Soporte",
      monitoring: "Monitoreo",
      reconciliation: "Reconciliación",
      ent_api: "API",
      ent_astro: "Astrología",
      ent_usage: "Uso",
      ent_editorial: "Editorial",
      ent_billing: "Facturación",
    },
  },
}

export function navigationTranslations(lang: AstrologyLang = "fr"): NavigationTranslation {
  return translations[lang] ?? translations.fr
}

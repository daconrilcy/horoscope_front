import type { AstrologyLang } from "./astrology"

export interface LandingTranslation {
  hero: {
    title: string
    subtitle: string
    bullet1: string
    bullet2: string
    bullet3: string
    ctaPrimary: string
    ctaSecondary: string
    micro1: string
    micro2: string
    micro3: string
    imageAlt: string
    caption1: string
    caption2: string
  }
  navbar: {
    howItWorks: string
    pricing: string
    login: string
    register: string
    language: string
  }
}

const translations: Record<AstrologyLang, LandingTranslation> = {
  fr: {
    hero: {
      title: "Votre guide astrologique personnel — disponible 24h/24",
      subtitle: "Des prévisions ultra-précises et un chat en direct avec votre astrologue IA pour éclairer votre chemin au quotidien.",
      bullet1: "Thème natal complet offert",
      bullet2: "Réponses instantanées et bienveillantes",
      bullet3: "Horoscope personnalisé chaque matin",
      ctaPrimary: "Démarrer gratuitement",
      ctaSecondary: "Voir un exemple",
      micro1: "Sans carte bancaire",
      micro2: "Annulation en 1 clic",
      micro3: "Données protégées RGPD",
      imageAlt: "Aperçu de l'interface Astrorizon",
      caption1: "Analyse en temps réel",
      caption2: "Conseils bienveillants",
    },
    navbar: {
      howItWorks: "Comment ça marche",
      pricing: "Tarifs",
      login: "Connexion",
      register: "Démarrer",
      language: "Langue",
    },
  },
  en: {
    hero: {
      title: "Your personal astrological guide — available 24/7",
      subtitle: "Ultra-accurate forecasts and live chat with your AI astrologer to light your path every day.",
      bullet1: "Complete birth chart included",
      bullet2: "Instant and caring answers",
      bullet3: "Personalized horoscope every morning",
      ctaPrimary: "Start for free",
      ctaSecondary: "See an example",
      micro1: "No credit card required",
      micro2: "Cancel in 1 click",
      micro3: "GDPR protected data",
      imageAlt: "Astrorizon interface preview",
      caption1: "Real-time analysis",
      caption2: "Empathetic guidance",
    },
    navbar: {
      howItWorks: "How it works",
      pricing: "Pricing",
      login: "Login",
      register: "Start",
      language: "Language",
    },
  },
  es: {
    hero: {
      title: "Tu guía astrológica personal — disponible 24/7",
      subtitle: "Pronósticos ultra precisos y chat en vivo con tu astrólogo IA para iluminar tu camino cada día.",
      bullet1: "Carta natal completa gratuita",
      bullet2: "Respuestas instantáneas y empáticas",
      bullet3: "Horóscopo personalizado cada mañana",
      ctaPrimary: "Empezar gratis",
      ctaSecondary: "Ver un ejemplo",
      micro1: "Sin tarjeta de crédito",
      micro2: "Cancela en 1 clic",
      micro3: "Datos protegidos por RGPD",
      imageAlt: "Vista previa de la interfaz de Astrorizon",
      caption1: "Análisis en tiempo real",
      caption2: "Guía empática",
    },
    navbar: {
      howItWorks: "Cómo funciona",
      pricing: "Precios",
      login: "Conexión",
      register: "Empezar",
      language: "Idioma",
    },
  },
}

export function landingTranslations(lang: AstrologyLang = "fr"): LandingTranslation {
  return translations[lang] ?? translations.fr
}

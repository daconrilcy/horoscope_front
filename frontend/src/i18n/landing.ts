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
  socialProof: {
    badges: {
      swiss: string
      rgpd: string
      available: string
    }
    metrics: {
      users: string
      usersValue: string
      rating: string
      ratingValue: string
      consultations: string
      consultationsValue: string
    }
  }
  problem: {
    title: string
    before: {
      title: string
      item1: string
      item2: string
      item3: string
    }
    after: {
      title: string
      item1: string
      item2: string
      item3: string
    }
  }
  solution: {
    title: string
    step1: {
      title: string
      desc: string
      benefit: string
    }
    step2: {
      title: string
      desc: string
      benefit: string
    }
    step3: {
      title: string
      desc: string
      benefit: string
    }
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
    socialProof: {
      badges: {
        swiss: "Calculs Swiss Ephemeris",
        rgpd: "Données protégées RGPD",
        available: "Disponible 24h/24",
      },
      metrics: {
        users: "Utilisateurs actifs",
        usersValue: "10k+",
        rating: "Note moyenne",
        ratingValue: "4.9/5",
        consultations: "Consultations réalisées",
        consultationsValue: "50k+",
      },
    },
    problem: {
      title: "L'astrologie devrait éclairer votre chemin, pas vous perdre",
      before: {
        title: "Aujourd'hui",
        item1: "Horoscopes génériques qui ne vous parlent jamais vraiment.",
        item2: "Impossible de poser une question précise à un expert sans attendre des jours.",
        item3: "Interpréter son thème natal seul est complexe et intimidant.",
      },
      after: {
        title: "Avec Astrorizon",
        item1: "Des prévisions basées sur votre thème unique, calculées à la minute près.",
        item2: "Un chat en direct disponible 24h/24 pour toutes vos interrogations.",
        item3: "Une pédagogie bienveillante pour comprendre votre mission de vie.",
      },
    },
    solution: {
      title: "En 3 étapes simples",
      step1: {
        title: "Partagez vos données de naissance",
        desc: "Indiquez votre date, heure et lieu de naissance avec précision pour un calcul rigoureux.",
        benefit: "Votre thème natal est calculé",
      },
      step2: {
        title: "Choisissez votre astrologue IA",
        desc: "Entamez une conversation guidée et personnalisée avec l'expert de votre choix.",
        benefit: "Conversation personnalisée",
      },
      step3: {
        title: "Recevez vos insights au quotidien",
        desc: "Bénéficiez d'une guidance actionnable et de prédictions basées sur le ciel du jour.",
        benefit: "Guidance et prédictions",
      },
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
    socialProof: {
      badges: {
        swiss: "Swiss Ephemeris Calculations",
        rgpd: "GDPR Protected Data",
        available: "Available 24/7",
      },
      metrics: {
        users: "Active Users",
        usersValue: "10k+",
        rating: "Average Rating",
        ratingValue: "4.9/5",
        consultations: "Consultations done",
        consultationsValue: "50k+",
      },
    },
    problem: {
      title: "Astrology should light your path, not confuse you",
      before: {
        title: "Today",
        item1: "Generic horoscopes that never really speak to you.",
        item2: "Impossible to ask an expert a specific question without waiting days.",
        item3: "Interpreting your birth chart alone is complex and intimidating.",
      },
      after: {
        title: "With Astrorizon",
        item1: "Forecasts based on your unique chart, calculated to the minute.",
        item2: "Live chat available 24/7 for all your questions.",
        item3: "Empathetic guidance to understand your life's mission.",
      },
    },
    solution: {
      title: "In 3 simple steps",
      step1: {
        title: "Share your birth data",
        desc: "Provide your date, time and place of birth for a precise calculation.",
        benefit: "Your birth chart is calculated",
      },
      step2: {
        title: "Choose your AI astrologer",
        desc: "Start a guided and personalized conversation with the expert of your choice.",
        benefit: "Personalized conversation",
      },
      step3: {
        title: "Receive daily insights",
        desc: "Get actionable guidance and predictions based on today's sky.",
        benefit: "Guidance and predictions",
      },
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
      ctaSecondary: "Ver un exemple",
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
    socialProof: {
      badges: {
        swiss: "Cálculos de Swiss Ephemeris",
        rgpd: "Datos protegidos por RGPD",
        available: "Disponible 24/7",
      },
      metrics: {
        users: "Usuarios activos",
        usersValue: "10k+",
        rating: "Calificación promedio",
        ratingValue: "4.9/5",
        consultations: "Consultas realizadas",
        consultationsValue: "50k+",
      },
    },
    problem: {
      title: "La astrología debería iluminar tu camino, no confundirte",
      before: {
        title: "Hoy",
        item1: "Horóscopos genéricos que nunca te hablan realmente.",
        item2: "Imposible hacer una pregunta específica a un experto sin esperar días.",
        item3: "Interpretar tu carta natal solo es complejo e intimidante.",
      },
      after: {
        title: "Con Astrorizon",
        item1: "Pronósticos basados en tu carta única, calculados al minuto.",
        item2: "Chat en vivo disponible 24/7 para todas tus dudas.",
        item3: "Guía empática para entender tu misión de vida.",
      },
    },
    solution: {
      title: "En 3 pasos sencillos",
      step1: {
        title: "Comparte tus datos de nacimiento",
        desc: "Indica tu fecha, hora y lugar de nacimiento con precisión para un cálculo riguroso.",
        benefit: "Tu carta natal es calculada",
      },
      step2: {
        title: "Elige tu astrólogo IA",
        desc: "Inicia una conversación guiada y personalizada con el experto de tu elección.",
        benefit: "Conversación personalizada",
      },
      step3: {
        title: "Recibe tus insights diarios",
        desc: "Recibe consejos prácticos y predicciones basadas en el cielo de hoy.",
        benefit: "Guía y predicciones",
      },
    },
  },
}

export function landingTranslations(lang: AstrologyLang = "fr"): LandingTranslation {
  return translations[lang] ?? translations.fr
}

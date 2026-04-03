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
  testimonials: {
    title: string
    subtitle: string
    items: Array<{
      quote: string
      author: string
      context: string
      rating?: number
    }>
    caseStudy: {
      title: string
      badge: string
      before: {
        label: string
        text: string
      }
      after: {
        label: string
        text: string
      }
      action: {
        label: string
        text: string
      }
    }
    reassurance: {
      data: string
      swiss: string
      cancel: string
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
      title: "Comment ça marche ?",
      step1: {
        title: "Créez votre profil natal",
        desc: "Partagez votre date, heure et lieu de naissance avec précision.",
        benefit: "Thème natal calculé instantanément",
      },
      step2: {
        title: "Échangez avec votre IA",
        desc: "Posez toutes vos questions à votre astrologue personnel.",
        benefit: "Réponses sur-mesure 24h/24",
      },
      step3: {
        title: "Suivez votre guidance",
        desc: "Recevez chaque matin des conseils actionnables pour votre journée.",
        benefit: "Saisissez les opportunités célestes",
      },
    },
    testimonials: {
      title: "Ils éclairent leur chemin avec Astrorizon",
      subtitle: "Témoignages basés sur nos premiers utilisateurs bêta.",
      items: [
        {
          quote: "Enfin un outil qui prend en compte l'heure exacte de ma naissance. Les conseils quotidiens tombent toujours juste.",
          author: "Sophie L.",
          context: "Utilisatrice, Balance",
          rating: 5,
        },
        {
          quote: "Le chat avec l'IA est impressionnant de bienveillance. C'est comme avoir un astrologue dans sa poche à toute heure.",
          author: "Marc A.",
          context: "Utilisateur, Capricorne",
          rating: 5,
        },
        {
          quote: "L'interprétation de mon thème natal m'a aidé à comprendre des blocages que je traînais depuis des années.",
          author: "Elena R.",
          context: "Utilisatrice, Poissons",
          rating: 5,
        },
      ],
      caseStudy: {
        title: "Cas d'usage : Sophie et son changement de carrière",
        badge: "Cas inspiré d'utilisateurs réels",
        before: {
          label: "Avant",
          text: "Sophie se sentait perdue dans son travail actuel, sans savoir si c'était le bon moment pour lancer son projet.",
        },
        after: {
          label: "Après",
          text: "Grâce à sa guidance personnalisée, elle a identifié une période favorable pour l'action et a lancé son entreprise avec confiance.",
        },
        action: {
          label: "Action",
          text: "Utilisation quotidienne du chat pour valider ses ressentis lors des phases lunaires clés.",
        },
      },
      reassurance: {
        data: "Données chiffrées et protégées",
        swiss: "Calculs basés sur Swiss Ephemeris",
        cancel: "Annulation sans conditions",
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
      title: "How it works?",
      step1: {
        title: "Create your birth profile",
        desc: "Share your date, time and place of birth with precision.",
        benefit: "Birth chart calculated instantly",
      },
      step2: {
        title: "Chat with your AI",
        desc: "Ask all your questions to your personal astrologer.",
        benefit: "Tailor-made answers 24/7",
      },
      step3: {
        title: "Follow your guidance",
        desc: "Receive actionable advice for your day every morning.",
        benefit: "Seize celestial opportunities",
      },
    },
    testimonials: {
      title: "They light their path with Astrorizon",
      subtitle: "Testimonials based on our first beta users.",
      items: [
        {
          quote: "Finally a tool that takes into account the exact time of my birth. Daily advice is always spot on.",
          author: "Sophie L.",
          context: "User, Libra",
          rating: 5,
        },
        {
          quote: "Chatting with the AI is impressively caring. It's like having an astrologer in your pocket at any time.",
          author: "Marc A.",
          context: "User, Capricorn",
          rating: 5,
        },
        {
          quote: "Interpreting my birth chart helped me understand blockages I've been carrying for years.",
          author: "Elena R.",
          context: "User, Pisces",
          rating: 5,
        },
      ],
      caseStudy: {
        title: "Use Case: Sophie and her career change",
        badge: "Inspiration based on real users",
        before: {
          label: "Before",
          text: "Sophie felt lost in her current job, not knowing if it was the right time to launch her project.",
        },
        after: {
          label: "After",
          text: "Thanks to her personalized guidance, she identified a favorable period for action and launched her company with confidence.",
        },
        action: {
          label: "Action",
          text: "Daily use of the chat to validate her feelings during key lunar phases.",
        },
      },
      reassurance: {
        data: "Encrypted and protected data",
        swiss: "Calculations based on Swiss Ephemeris",
        cancel: "Unconditional cancellation",
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
      title: "¿Cómo funciona?",
      step1: {
        title: "Crea tu perfil natal",
        desc: "Comparte tu fecha, hora y lugar de nacimiento con precisión.",
        benefit: "Carta natal calculada al instante",
      },
      step2: {
        title: "Chatea con tu IA",
        desc: "Haz todas tus preguntas a tu astrólogo personal.",
        benefit: "Respuestas a medida 24/7",
      },
      step3: {
        title: "Sigue tu guía",
        desc: "Recibe consejos prácticos para tu día cada mañana.",
        benefit: "Aprovecha las oportunidades celestiales",
      },
    },
    testimonials: {
      title: "Ellos iluminan su camino con Astrorizon",
      subtitle: "Testimonios basados en nuestros primeros usuarios beta.",
      items: [
        {
          quote: "Finalmente una herramienta que tiene en cuenta la hora exacta de mi nacimiento. Los consejos diarios siempre son acertados.",
          author: "Sophie L.",
          context: "Usuaria, Libra",
          rating: 5,
        },
        {
          quote: "Chatear con la IA es impresionantemente empático. Es como tener un astrólogo en el bolsillo en cualquier momento.",
          author: "Marc A.",
          context: "Usuario, Capricornio",
          rating: 5,
        },
        {
          quote: "Interpretar mi carta natal me ayudó a entender bloqueos que llevaba arrastrando años.",
          author: "Elena R.",
          context: "Usuaria, Piscis",
          rating: 5,
        },
      ],
      caseStudy: {
        title: "Caso de uso: Sophie y su cambio de carrera",
        badge: "Inspirado en usuarios reales",
        before: {
          label: "Antes",
          text: "Sophie se sentía perdida en su trabajo actual, sin saber si era el momento adecuado para lanzar su proyecto.",
        },
        after: {
          label: "Después",
          text: "Gracias a su guía personalizada, identificó un período favorable para la acción y lanzó su empresa con confianza.",
        },
        action: {
          label: "Acción",
          text: "Uso diario del chat para validar sus sentimientos durante las fases lunares clave.",
        },
      },
      reassurance: {
        data: "Datos cifrados y protegidos",
        swiss: "Cálculos basados en Swiss Ephemeris",
        cancel: "Cancelación sin condiciones",
      },
    },
  },
}

export function landingTranslations(lang: AstrologyLang = "fr"): LandingTranslation {
  return translations[lang] ?? translations.fr
}

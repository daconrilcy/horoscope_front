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
  navbarA11y: {
    navLabel: string
    logoLabel: string
    openMenu: string
    closeMenu: string
    mobileMenu: string
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
  pricing: {
    title: string
    perMonth: string
    recommended: string
    cta: {
      free: string
      paid: string
    }
    ariaFeatures: string
    features: {
      natal: string
      horoscope: string
      chat: string
      consultation: string
      predictions: string
      support: string
    }
    plans: {
      free: {
        name: string
        desc: string
      }
      basic: {
        name: string
        desc: string
      }
      premium: {
        name: string
        desc: string
      }
      trial: {
        name: string
        desc: string
      }
    }
    reassurance: string
  }
  faq: {
    title: string
    items: Array<{
      q: string
      a: string
    }>
  }
  finalCta: {
    title: string
    subtitle: string
    button: string
    micro1: string
    micro2: string
  }
  footer: {
    desc: string
    product: {
      title: string
      howItWorks: { label: string; enabled: boolean }
      pricing: { label: string; enabled: boolean }
      login: { label: string; enabled: boolean }
    }
    legal: {
      title: string
      privacy: { label: string; path: string; enabled: boolean }
      legal: { label: string; path: string; enabled: boolean }
      terms: { label: string; path: string; enabled: boolean }
      cookies: { label: string; path: string; enabled: boolean }
    }
    social: {
      title: string
      twitter: { url: string; enabled: boolean }
      instagram: { url: string; enabled: boolean }
    }
    contact: {
      title: string
      email: { label: string; value: string; enabled: boolean }
    }
    copyright: string
  }
  seo: {
    title: string
    description: string
    ogTitle: string
    ogDescription: string
  }
  common: {
    skipLink: string
    separatorOr: string
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
    navbarA11y: {
      navLabel: "Navigation principale",
      logoLabel: "Astrorizon - Retour à l'accueil",
      openMenu: "Ouvrir le menu",
      closeMenu: "Fermer le menu",
      mobileMenu: "Menu mobile",
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
    pricing: {
      title: "Choisissez votre chemin",
      perMonth: "/ mois",
      recommended: "Plus populaire",
      cta: {
        free: "Démarrer gratuitement",
        paid: "Choisir ce plan",
      },
      ariaFeatures: "Fonctionnalités du plan",
      features: {
        natal: "Thème natal précis",
        horoscope: "Horoscope quotidien",
        chat: "Chat astrologue IA",
        consultation: "Consultations thématiques",
        predictions: "Prédictions & Moments clés",
        support: "Support prioritaire",
      },
      plans: {
        free: {
          name: "Free",
          desc: "Découvrez l'essentiel de l'astrologie.",
        },
        basic: {
          name: "Basic",
          desc: "Pour un accompagnement régulier.",
        },
        premium: {
          name: "Premium",
          desc: "L'expérience complète et sans limite.",
        },
        trial: {
          name: "Essai",
          desc: "Découvrez Astrorizon gratuitement.",
        },
      },
      reassurance: "Sans engagement. Annulation en un clic.",
    },
    faq: {
      title: "Questions fréquentes",
      items: [
        {
          q: "Est-ce vraiment personnalisé pour moi ?",
          a: "Oui, contrairement aux horoscopes de presse, Astrorizon utilise votre date, heure et lieu de naissance exacts pour calculer les positions planétaires réelles via Swiss Ephemeris.",
        },
        {
          q: "Combien de temps pour voir un premier résultat ?",
          a: "Dès votre inscription, vous accédez à votre thème natal complet. Le chat IA répond instantanément à vos questions dès la première minute.",
        },
        {
          q: "Mes données personnelles sont-elles protégées ?",
          a: "Absolument. Nous respectons strictement le RGPD. Vos données de naissance et vos conversations sont chiffrées et ne sont jamais vendues à des tiers.",
        },
        {
          q: "Puis-je annuler mon abonnement à tout moment ?",
          a: "Oui, la gestion de l'abonnement se fait en un clic depuis vos paramètres. Il n'y a aucun engagement de durée pour nos plans mensuels.",
        },
        {
          q: "L'astrologie est-elle scientifiquement fondée ?",
          a: "L'astrologie est un système symbolique millénaire de compréhension de soi. Nos calculs astronomiques sont d'une précision scientifique, tandis que l'interprétation relève du conseil et de la guidance personnelle.",
        },
        {
          q: "Y a-t-il un support si j'ai besoin d'aide ?",
          a: "Bien sûr. Notre équipe est disponible par email pour toute question technique ou liée à votre compte utilisateur.",
        },
      ],
    },
    finalCta: {
      title: "Prêt à découvrir votre thème natal ?",
      subtitle: "Rejoignez Astrorizon et commencez votre voyage vers une meilleure connaissance de vous-même.",
      button: "Démarrer gratuitement",
      micro1: "Sans carte bancaire",
      micro2: "Annulation en 1 clic",
    },
    footer: {
      desc: "Astrorizon combine la sagesse millénaire de l'astrologie avec la précision de l'IA pour éclairer votre chemin quotidien.",
      product: {
        title: "Produit",
        howItWorks: { label: "Comment ça marche", enabled: true },
        pricing: { label: "Tarifs", enabled: true },
        login: { label: "Se connecter", enabled: true },
      },
      legal: {
        title: "Légal",
        privacy: { label: "Confidentialité", path: "/privacy", enabled: true },
        legal: { label: "Mentions légales", path: "/legal", enabled: false },
        terms: { label: "CGV/CGU", path: "/terms", enabled: false },
        cookies: { label: "Cookies", path: "/cookies", enabled: false },
      },
      social: {
        title: "Suivez-nous",
        twitter: { url: "https://twitter.com/astrorizon", enabled: false },
        instagram: { url: "https://instagram.com/astrorizon", enabled: false },
      },
      contact: {
        title: "Contact",
        email: { label: "Email", value: "hello@astrorizon.ai", enabled: true },
      },
      copyright: "Astrorizon. Tous droits réservés.",
    },
    seo: {
      title: "Votre Astrologue IA Personnel | Astrorizon",
      description: "Découvrez votre thème natal et échangez avec votre astrologue IA disponible 24h/24. Prévisions précises et guidance personnalisée au quotidien.",
      ogTitle: "Astrorizon — L'astrologie augmentée par l'IA",
      ogDescription: "Obtenez des réponses instantanées sur votre avenir et votre personnalité grâce à notre technologie de calcul astrologique de précision.",
    },
    common: {
      skipLink: "Aller au contenu principal",
      separatorOr: "ou",
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
    navbarA11y: {
      navLabel: "Main navigation",
      logoLabel: "Astrorizon - Back to home",
      openMenu: "Open menu",
      closeMenu: "Close menu",
      mobileMenu: "Mobile menu",
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
    pricing: {
      title: "Choose your path",
      perMonth: "/ month",
      recommended: "Most popular",
      cta: {
        free: "Start for free",
        paid: "Choose this plan",
      },
      ariaFeatures: "Plan features",
      features: {
        natal: "Precise birth chart",
        horoscope: "Daily horoscope",
        chat: "AI Astrologer chat",
        consultation: "Thematic consultations",
        predictions: "Predictions & Key moments",
        support: "Priority support",
      },
      plans: {
        free: {
          name: "Free",
          desc: "Discover the essentials of astrology.",
        },
        basic: {
          name: "Basic",
          desc: "For regular guidance.",
        },
        premium: {
          name: "Premium",
          desc: "The complete, unlimited experience.",
        },
        trial: {
          name: "Trial",
          desc: "Discover Astrorizon for free.",
        },
      },
      reassurance: "No strings attached. One-click cancellation.",
    },
    faq: {
      title: "Frequently Asked Questions",
      items: [
        {
          q: "Is it really personalized for me?",
          a: "Yes, unlike general horoscopes, Astrorizon uses your exact date, time, and place of birth to calculate real planetary positions via Swiss Ephemeris.",
        },
        {
          q: "How long until I see results?",
          a: "As soon as you sign up, you access your complete birth chart. The AI chat answers your questions from the very first minute.",
        },
        {
          q: "Is my personal data protected?",
          a: "Absolutely. We strictly comply with GDPR. Your birth data and conversations are encrypted and never sold to third parties.",
        },
        {
          q: "Can I cancel my subscription anytime?",
          a: "Yes, managing your subscription is easy from your settings. There is no long-term commitment for our monthly plans.",
        },
        {
          q: "Is astrology scientifically based?",
          a: "Astrology is a millenary symbolic system for self-understanding. Our astronomical calculations are scientifically precise, while interpretation is a matter of personal guidance.",
        },
        {
          q: "Is there support if I need help?",
          a: "Of course. Our team is available via email for any technical or account-related questions.",
        },
      ],
    },
    finalCta: {
      title: "Ready to discover your birth chart?",
      subtitle: "Join Astrorizon and start your journey towards better self-knowledge.",
      button: "Start for free",
      micro1: "No credit card required",
      micro2: "Cancel in 1 click",
    },
    footer: {
      desc: "Astrorizon combines millenary astrology wisdom with AI precision to light your daily path.",
      product: {
        title: "Product",
        howItWorks: { label: "How it works", enabled: true },
        pricing: { label: "Pricing", enabled: true },
        login: { label: "Login", enabled: true },
      },
      legal: {
        title: "Legal",
        privacy: { label: "Privacy Policy", path: "/privacy", enabled: true },
        legal: { label: "Legal Notice", path: "/legal", enabled: false },
        terms: { label: "Terms of Service", path: "/terms", enabled: false },
        cookies: { label: "Cookie Policy", path: "/cookies", enabled: false },
      },
      social: {
        title: "Follow us",
        twitter: { url: "https://twitter.com/astrorizon", enabled: false },
        instagram: { url: "https://instagram.com/astrorizon", enabled: false },
      },
      contact: {
        title: "Contact",
        email: { label: "Email", value: "hello@astrorizon.ai", enabled: true },
      },
      copyright: "Astrorizon. All rights reserved.",
    },
    seo: {
      title: "Your Personal AI Astrologer | Astrorizon",
      description: "Discover your birth chart and chat with your AI astrologer available 24/7. Precise forecasts and personalized guidance daily.",
      ogTitle: "Astrorizon — Astrology Augmented by AI",
      ogDescription: "Get instant answers about your future and personality with our precision astrology calculation technology.",
    },
    common: {
      skipLink: "Skip to main content",
      separatorOr: "or",
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
    navbarA11y: {
      navLabel: "Navegación principal",
      logoLabel: "Astrorizon - Volver al inicio",
      openMenu: "Abrir menú",
      closeMenu: "Cerrar menú",
      mobileMenu: "Menú móvil",
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
    pricing: {
      title: "Elige tu camino",
      perMonth: "/ mes",
      recommended: "Más popular",
      cta: {
        free: "Empezar gratis",
        paid: "Elegir este plan",
      },
      ariaFeatures: "Características del plan",
      features: {
        natal: "Carta natal precisa",
        horoscope: "Horóscopo diario",
        chat: "Chat astrólogo IA",
        consultation: "Consultas temáticas",
        predictions: "Predicciones y Momentos clave",
        support: "Soporte prioritario",
      },
      plans: {
        free: {
          name: "Free",
          desc: "Descubre lo esencial de la astrología.",
        },
        basic: {
          name: "Basic",
          desc: "Para un acompañamiento regular.",
        },
        premium: {
          name: "Premium",
          desc: "La experiencia completa y sin límites.",
        },
        trial: {
          name: "Prueba",
          desc: "Descubre Astrorizon gratis hoy mismo.",
        },
      },
      reassurance: "Sin compromiso. Cancelación en un clic.",
    },
    faq: {
      title: "Preguntas frecuentes",
      items: [
        {
          q: "¿Es realmente personalizado para mí?",
          a: "Sí, a diferencia de los horóscopos generales, Astrorizon utiliza tu fecha, hora y lugar de nacimiento exactos para calcular posiciones planetarias reales con Swiss Ephemeris.",
        },
        {
          q: "¿Cuánto tiempo para ver un primer resultado?",
          a: "Desde tu registro, accedes a tu carta natal completa. El chat IA responde instantáneamente a tus dudas desde el primer minuto.",
        },
        {
          q: "¿Mis datos personales están protegidos?",
          a: "Absolutamente. Cumplimos estrictamente con el RGPD. Tus datos de nacimiento y conversaciones están cifrados y nunca se venden a terceros.",
        },
        {
          q: "¿Puedo cancelar mi suscripción en cualquier momento?",
          a: "Sí, la gestión de la suscripción se hace en un clic desde tus ajustes. No hay compromiso de permanencia en nuestros planes mensuales.",
        },
        {
          q: "¿La astrología tiene base científica?",
          a: "La astrología es un sistema simbólico milenario de autoconocimiento. Nuestros cálculos astronómicos son de precisión científica, mientras que la interpretación es una guía personal.",
        },
        {
          q: "¿Hay soporte si necesito ayuda?",
          a: "Por supuesto. Nuestro equipo está disponible por email para cualquier duda técnica o relacionada con tu cuenta.",
        },
      ],
    },
    finalCta: {
      title: "¿Listo para descubrir tu carta natal?",
      subtitle: "Únete a Astrorizon y comienza tu viaje hacia un mejor autoconocimiento.",
      button: "Empezar gratis",
      micro1: "Sin tarjeta de crédito",
      micro2: "Cancela en 1 clic",
    },
    footer: {
      desc: "Astrorizon combina la sabiduría milenaria de la astrología con la précision de la IA para iluminar tu camino diario.",
      product: {
        title: "Producto",
        howItWorks: { label: "Cómo funciona", enabled: true },
        pricing: { label: "Precios", enabled: true },
        login: { label: "Conexión", enabled: true },
      },
      legal: {
        title: "Legal",
        privacy: { label: "Privacidad", path: "/privacy", enabled: true },
        legal: { label: "Aviso legal", path: "/legal", enabled: false },
        terms: { label: "Términos", path: "/terms", enabled: false },
        cookies: { label: "Cookies", path: "/cookies", enabled: false },
      },
      social: {
        title: "Síguenos",
        twitter: { url: "https://twitter.com/astrorizon", enabled: false },
        instagram: { url: "https://instagram.com/astrorizon", enabled: false },
      },
      contact: {
        title: "Contacto",
        email: { label: "Email", value: "hello@astrorizon.ai", enabled: true },
      },
      copyright: "Astrorizon. Todos los derechos reservados.",
    },
    seo: {
      title: "Tu Astrólogo IA Personal | Astrorizon",
      description: "Descubre tu carta natal y chatea con tu astrólogo IA disponible 24/7. Pronósticos precisos y guía personalizada diaria.",
      ogTitle: "Astrorizon — Astrología Aumentada por IA",
      ogDescription: "Obtén respuestas instantáneas sobre tu futuro y personalidad con nuestra tecnología de cálculo astrológico de precisión.",
    },
    common: {
      skipLink: "Saltar al contenido principal",
      separatorOr: "o",
    },
  },
}

export function landingTranslations(lang: AstrologyLang = "fr"): LandingTranslation {
  return translations[lang] ?? translations.fr
}

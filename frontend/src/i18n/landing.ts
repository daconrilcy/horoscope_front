import type { AstrologyLang } from "./astrology"

export interface LandingTranslation {
  hero: {
    titleLead: string
    titleAccent: string
    eyebrow: string
    previewLabel: string
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
    dailyLabel: string
    dailyTitle: string
    dailyItems: Array<{ label: string; value: string }>
    chatLabel: string
    chatQuestion: string
    chatAnswer: string
    momentLabel: string
    momentText: string
  }
  navbar: {
    trust: string
    howItWorks: string
    pricing: string
    faq: string
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
    eyebrow: string
    title: string
    badges: {
      swiss: string
      rgpd: string
      available: string
    }
    proofs: {
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
    eyebrow: string
    intro: string
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
    eyebrow: string
    subtitle: string
    title: string
    step1: {
      title: string
      desc: string
      benefit: string
      example: string
    }
    step2: {
      title: string
      desc: string
      benefit: string
      example: string
    }
    step3: {
      title: string
      desc: string
      benefit: string
      example: string
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
    eyebrow: string
    subtitle: string
    title: string
    perMonth: string
    recommended: string
    audience: {
      free: string
      basic: string
      premium: string
    }
    freeLabel: string
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
    eyebrow: string
    subtitle: string
    title: string
    items: Array<{
      q: string
      a: string
    }>
  }
  finalCta: {
    eyebrow: string
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
      titleLead: "Votre guide astrologique personnel",
      titleAccent: "Toujours disponible",
      eyebrow: "Guidance astrologique premium",
      previewLabel: "Aperçu de l'expérience",
      subtitle: "Comprenez votre journée, posez vos questions et obtenez une guidance personnelle immédiatement utile.",
      bullet1: "Thème natal complet offert",
      bullet2: "Réponses instantanées et bienveillantes",
      bullet3: "Horoscope personnalisé chaque matin",
      ctaPrimary: "Démarrer gratuitement",
      ctaSecondary: "Découvrir comment ça marche",
      micro1: "Sans carte bancaire",
      micro2: "Annulation en 1 clic",
      micro3: "Données protégées RGPD",
      imageAlt: "Aperçu de l'interface Astrorizon",
      caption1: "Analyse en temps réel",
      caption2: "Conseils bienveillants",
      dailyLabel: "Horoscope du jour",
      dailyTitle: "Une journée favorable pour clarifier une décision importante.",
      dailyItems: [
        { label: "Amour", value: "Dialogue fluide" },
        { label: "Travail", value: "Moment d'initiative" },
        { label: "Énergie", value: "Ralentir après 18h" },
      ],
      chatLabel: "Question en direct",
      chatQuestion: "Est-ce le bon moment pour relancer ce projet ?",
      chatAnswer:
        "Oui. Les transits du jour favorisent la reprise de contact et une décision posée, sans brusquer les choses.",
      momentLabel: "Moment clé",
      momentText:
        "Entre 14h et 16h, votre communication est plus claire. Profitez-en pour envoyer le message important.",
    },
    navbar: {
      trust: "Confiance",
      howItWorks: "Comment ça marche",
      pricing: "Tarifs",
      faq: "FAQ",
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
      eyebrow: "Confiance",
      title: "Une expérience utile, cadrée et crédible dès la première visite.",
      badges: {
        swiss: "Calculs Swiss Ephemeris",
        rgpd: "Données protégées RGPD",
        available: "Disponible 24h/24",
      },
      proofs: {
        swiss: "Positions planétaires calculées avec un moteur de référence.",
        rgpd: "Naissance, échanges et compte utilisateur traités de façon sécurisée.",
        available: "Réponses immédiates, sans attente ni prise de rendez-vous.",
      },
      metrics: {
        users: "Moteur de calcul",
        usersValue: "Swiss Ephemeris",
        rating: "Confidentialité",
        ratingValue: "RGPD",
        consultations: "Disponibilité",
        consultationsValue: "24/7",
      },
    },
    problem: {
      eyebrow: "Transformation",
      intro: "Vous cherchez une guidance personnelle, pas des généralités.",
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
      eyebrow: "Fonctionnement",
      subtitle: "Trois étapes simples pour passer de l'intuition à une guidance exploitable.",
      title: "Comment ça marche ?",
      step1: {
        title: "Créez votre profil natal",
        desc: "Partagez votre date, heure et lieu de naissance avec précision.",
        benefit: "Thème natal calculé instantanément",
        example: "Date, heure, lieu de naissance",
      },
      step2: {
        title: "Échangez avec votre IA",
        desc: "Posez toutes vos questions à votre astrologue personnel.",
        benefit: "Réponses sur-mesure 24h/24",
        example: "“Est-ce le bon moment pour relancer cette conversation ?”",
      },
      step3: {
        title: "Suivez votre guidance",
        desc: "Recevez chaque matin des conseils actionnables pour votre journée.",
        benefit: "Saisissez les opportunités célestes",
        example: "Fenêtre favorable, ton du jour, conseil concret",
      },
    },
    testimonials: {
      title: "Nos engagements de confiance",
      subtitle: "Nous publierons uniquement des retours clients vérifiés après validation produit.",
      items: [
        {
          quote: "Les calculs astrologiques reposent sur Swiss Ephemeris et prennent en compte vos données de naissance exactes.",
          author: "Méthodologie",
          context: "Engagement produit",
        },
        {
          quote: "Vos données personnelles et vos conversations restent protégées et ne sont jamais revendues.",
          author: "Confidentialité",
          context: "Engagement produit",
        },
        {
          quote: "L'abonnement reste sans engagement avec une gestion et une résiliation en un clic depuis votre compte.",
          author: "Abonnement",
          context: "Engagement produit",
        },
      ],
      caseStudy: {
        title: "Publication des retours clients",
        badge: "Transparence",
        before: {
          label: "Aujourd'hui",
          text: "La landing met en avant uniquement des preuves qualitatives et des engagements vérifiables.",
        },
        after: {
          label: "Prochaine étape",
          text: "Les témoignages et cas d'usage seront publiés lorsque nous disposerons de retours clients vérifiés.",
        },
        action: {
          label: "Principe",
          text: "Aucune citation nominative ni métrique non auditée n'est exposée avant validation.",
        },
      },
      reassurance: {
        data: "Données chiffrées et protégées",
        swiss: "Calculs basés sur Swiss Ephemeris",
        cancel: "Annulation sans conditions",
      },
    },
    pricing: {
      eyebrow: "Choix",
      subtitle:
        "Commencez gratuitement, choisissez Basic si vous voulez une guidance régulière, Premium si vous utilisez Astrorizon au quotidien.",
      title: "Choisissez votre chemin",
      perMonth: "/ mois",
      recommended: "Plus populaire",
      audience: {
        free: "Pour découvrir l'expérience",
        basic: "Pour une guidance régulière",
        premium: "Pour un accompagnement complet",
      },
      freeLabel: "Gratuit",
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
      eyebrow: "Objections",
      subtitle: "Les questions les plus fréquentes avant de commencer.",
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
      eyebrow: "Décision",
      title: "Commencez votre thème natal en quelques minutes",
      subtitle: "Essayez Astrorizon gratuitement dès aujourd'hui et voyez tout de suite comment la guidance s'applique à votre situation.",
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
      titleLead: "Your personal astrological guide",
      titleAccent: "Always available",
      eyebrow: "Premium astrology guidance",
      previewLabel: "Experience preview",
      subtitle: "Understand your day, ask your questions, and get personal guidance that feels immediately useful.",
      bullet1: "Complete birth chart included",
      bullet2: "Instant and caring answers",
      bullet3: "Personalized horoscope every morning",
      ctaPrimary: "Start for free",
      ctaSecondary: "See how it works",
      micro1: "No credit card required",
      micro2: "Cancel in 1 click",
      micro3: "GDPR protected data",
      imageAlt: "Astrorizon interface preview",
      caption1: "Real-time analysis",
      caption2: "Empathetic guidance",
      dailyLabel: "Today’s horoscope",
      dailyTitle: "A favorable day to clarify an important decision.",
      dailyItems: [
        { label: "Love", value: "Smooth dialogue" },
        { label: "Work", value: "Good timing to act" },
        { label: "Energy", value: "Slow down after 6pm" },
      ],
      chatLabel: "Live question",
      chatQuestion: "Is this the right time to relaunch this project?",
      chatAnswer:
        "Yes. Today’s transits support renewed contact and a grounded decision, without forcing the pace.",
      momentLabel: "Key moment",
      momentText:
        "Between 2pm and 4pm, your communication is clearer. Use that window for the message that matters.",
    },
    navbar: {
      trust: "Trust",
      howItWorks: "How it works",
      pricing: "Pricing",
      faq: "FAQ",
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
      eyebrow: "Trust",
      title: "A useful, credible experience from the very first visit.",
      badges: {
        swiss: "Swiss Ephemeris Calculations",
        rgpd: "GDPR Protected Data",
        available: "Available 24/7",
      },
      proofs: {
        swiss: "Planetary positions calculated with a reference-grade engine.",
        rgpd: "Birth data, conversations, and account data are handled securely.",
        available: "Immediate answers, without waiting or booking a consultation.",
      },
      metrics: {
        users: "Calculation engine",
        usersValue: "Swiss Ephemeris",
        rating: "Privacy",
        ratingValue: "GDPR",
        consultations: "Availability",
        consultationsValue: "24/7",
      },
    },
    problem: {
      eyebrow: "Transformation",
      intro: "You are looking for personal guidance, not generic content.",
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
      eyebrow: "How it works",
      subtitle: "Three simple steps to move from intuition to usable guidance.",
      title: "How it works?",
      step1: {
        title: "Create your birth profile",
        desc: "Share your date, time and place of birth with precision.",
        benefit: "Birth chart calculated instantly",
        example: "Date, time, place of birth",
      },
      step2: {
        title: "Chat with your AI",
        desc: "Ask all your questions to your personal astrologer.",
        benefit: "Tailor-made answers 24/7",
        example: "“Is this the right time to restart this conversation?”",
      },
      step3: {
        title: "Follow your guidance",
        desc: "Receive actionable advice for your day every morning.",
        benefit: "Seize celestial opportunities",
        example: "Best window, tone of the day, concrete advice",
      },
    },
    testimonials: {
      title: "Our trust commitments",
      subtitle: "We only publish verified customer feedback after product validation.",
      items: [
        {
          quote: "Astrological calculations rely on Swiss Ephemeris and your exact birth data.",
          author: "Methodology",
          context: "Product commitment",
        },
        {
          quote: "Your personal data and conversations stay protected and are never resold.",
          author: "Privacy",
          context: "Product commitment",
        },
        {
          quote: "Subscriptions stay commitment-free with one-click management from your account.",
          author: "Subscription",
          context: "Product commitment",
        },
      ],
      caseStudy: {
        title: "Publishing customer feedback",
        badge: "Transparency",
        before: {
          label: "Today",
          text: "The landing page only highlights qualitative proof points and verifiable commitments.",
        },
        after: {
          label: "Next step",
          text: "Testimonials and case studies will be published once verified customer feedback is available.",
        },
        action: {
          label: "Principle",
          text: "No named quote or unaudited metric is exposed before validation.",
        },
      },
      reassurance: {
        data: "Encrypted and protected data",
        swiss: "Calculations based on Swiss Ephemeris",
        cancel: "Unconditional cancellation",
      },
    },
    pricing: {
      eyebrow: "Choice",
      subtitle:
        "Start for free, choose Basic for regular guidance, Premium for a complete day-to-day companion.",
      title: "Choose your path",
      perMonth: "/ month",
      recommended: "Most popular",
      audience: {
        free: "To discover the experience",
        basic: "For regular guidance",
        premium: "For complete support",
      },
      freeLabel: "Free",
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
      eyebrow: "Objections",
      subtitle: "The most common questions before getting started.",
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
      eyebrow: "Decision",
      title: "Start your birth chart in just a few minutes",
      subtitle: "Try Astrorizon for free today and immediately see how the guidance applies to your situation.",
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
      titleLead: "Tu guía astrológica personal",
      titleAccent: "Siempre disponible",
      eyebrow: "Guía astrológica premium",
      previewLabel: "Vista previa de la experiencia",
      subtitle: "Comprende tu día, haz tus preguntas y recibe una guía personal útil desde el primer minuto.",
      bullet1: "Carta natal completa gratuita",
      bullet2: "Respuestas instantáneas y empáticas",
      bullet3: "Horóscopo personalizado cada mañana",
      ctaPrimary: "Empezar gratis",
      ctaSecondary: "Descubrir cómo funciona",
      micro1: "Sin tarjeta de crédito",
      micro2: "Cancela en 1 clic",
      micro3: "Datos protegidos por RGPD",
      imageAlt: "Vista previa de la interfaz de Astrorizon",
      caption1: "Análisis en tiempo real",
      caption2: "Guía empática",
      dailyLabel: "Horóscopo del día",
      dailyTitle: "Un día favorable para aclarar una decisión importante.",
      dailyItems: [
        { label: "Amor", value: "Diálogo fluido" },
        { label: "Trabajo", value: "Buen momento para actuar" },
        { label: "Energía", value: "Baja el ritmo después de las 18h" },
      ],
      chatLabel: "Pregunta en directo",
      chatQuestion: "¿Es el momento adecuado para reactivar este proyecto?",
      chatAnswer:
        "Sí. Los tránsitos del día favorecen retomar el contacto y decidir con calma, sin forzar nada.",
      momentLabel: "Momento clave",
      momentText:
        "Entre las 14h y las 16h tu comunicación es más clara. Aprovecha esa ventana para enviar el mensaje importante.",
    },
    navbar: {
      trust: "Confianza",
      howItWorks: "Cómo funciona",
      pricing: "Precios",
      faq: "FAQ",
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
      eyebrow: "Confianza",
      title: "Una experiencia útil, clara y creíble desde la primera visita.",
      badges: {
        swiss: "Cálculos de Swiss Ephemeris",
        rgpd: "Datos protegidos por RGPD",
        available: "Disponible 24/7",
      },
      proofs: {
        swiss: "Posiciones planetarias calculadas con un motor de referencia.",
        rgpd: "Nacimiento, conversaciones y cuenta tratados de forma segura.",
        available: "Respuestas inmediatas, sin espera ni cita previa.",
      },
      metrics: {
        users: "Motor de cálculo",
        usersValue: "Swiss Ephemeris",
        rating: "Privacidad",
        ratingValue: "RGPD",
        consultations: "Disponibilidad",
        consultationsValue: "24/7",
      },
    },
    problem: {
      eyebrow: "Transformación",
      intro: "Buscas una guía personal, no generalidades.",
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
      eyebrow: "Funcionamiento",
      subtitle: "Tres pasos simples para pasar de la intuición a una guía accionable.",
      title: "¿Cómo funciona?",
      step1: {
        title: "Crea tu perfil natal",
        desc: "Comparte tu fecha, hora y lugar de nacimiento con precisión.",
        benefit: "Carta natal calculada al instante",
        example: "Fecha, hora y lugar de nacimiento",
      },
      step2: {
        title: "Chatea con tu IA",
        desc: "Haz todas tus preguntas a tu astrólogo personal.",
        benefit: "Respuestas a medida 24/7",
        example: "“¿Es el momento adecuado para retomar esta conversación?”",
      },
      step3: {
        title: "Sigue tu guía",
        desc: "Recibe consejos prácticos para tu día cada mañana.",
        benefit: "Aprovecha las oportunidades celestiales",
        example: "Ventana favorable, tono del día y consejo concreto",
      },
    },
    testimonials: {
      title: "Nuestros compromisos de confianza",
      subtitle: "Solo publicaremos opiniones verificadas de clientes tras la validación del producto.",
      items: [
        {
          quote: "Los cálculos astrológicos se basan en Swiss Ephemeris y en tus datos exactos de nacimiento.",
          author: "Metodología",
          context: "Compromiso de producto",
        },
        {
          quote: "Tus datos personales y tus conversaciones permanecen protegidos y nunca se revenden.",
          author: "Privacidad",
          context: "Compromiso de producto",
        },
        {
          quote: "La suscripción no tiene permanencia y puedes gestionarla o cancelarla en un clic desde tu cuenta.",
          author: "Suscripción",
          context: "Compromiso de producto",
        },
      ],
      caseStudy: {
        title: "Publicación de opiniones de clientes",
        badge: "Transparencia",
        before: {
          label: "Hoy",
          text: "La landing solo muestra pruebas cualitativas y compromisos verificables.",
        },
        after: {
          label: "Próximo paso",
          text: "Los testimonios y casos de uso se publicarán cuando existan opiniones de clientes verificadas.",
        },
        action: {
          label: "Principio",
          text: "No se muestra ninguna cita nominal ni ninguna métrica no auditada antes de su validación.",
        },
      },
      reassurance: {
        data: "Datos cifrados y protegidos",
        swiss: "Cálculos basados en Swiss Ephemeris",
        cancel: "Cancelación sin condiciones",
      },
    },
    pricing: {
      eyebrow: "Elección",
      subtitle:
        "Empieza gratis, elige Basic para una guía regular y Premium para un acompañamiento completo del día a día.",
      title: "Elige tu camino",
      perMonth: "/ mes",
      recommended: "Más popular",
      audience: {
        free: "Para descubrir la experiencia",
        basic: "Para una guía regular",
        premium: "Para un acompañamiento completo",
      },
      freeLabel: "Gratis",
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
      eyebrow: "Objeciones",
      subtitle: "Las preguntas más frecuentes antes de empezar.",
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
      eyebrow: "Decisión",
      title: "Empieza tu carta natal en solo unos minutos",
      subtitle: "Prueba Astrorizon gratis hoy y comprueba de inmediato cómo la guía se aplica a tu situación.",
      button: "Empezar gratis",
      micro1: "Sin tarjeta de crédito",
      micro2: "Cancela en 1 clic",
    },
    footer: {
      desc: "Astrorizon combina la sabiduría milenaria de la astrología con la precisión de la IA para iluminar tu camino diario.",
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

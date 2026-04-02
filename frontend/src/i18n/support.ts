export const supportTranslations = {
  fr: {
    help: {
      pageTitle: "Centre d'aide & Support",
      hero: {
        title: "Comment pouvons-nous vous aider aujourd’hui ?",
        subtitle: "Trouvez des réponses rapides ou contactez notre équipe d’experts.",
        primaryCta: "Ouvrir un ticket support",
        secondaryCta: "Gérer mon abonnement",
        steps: [
          "Choisissez une catégorie",
          "Décrivez votre besoin",
          "Suivez la résolution"
        ]
      },
      shortcuts: {
        dashboard: {
          title: "Horoscope",
          benefit: "Suivez votre météo astrale",
          action: "Y aller",
        },
        chat: {
          title: "Chat",
          benefit: "Parlez à votre astrologue",
          action: "Discuter",
        },
        natal: {
          title: "Thème Natal",
          benefit: "Comprenez votre nature",
          action: "Explorer",
        },
        consultations: {
          title: "Consultations",
          benefit: "Analyses thématiques",
          action: "Découvrir",
        },
      },
      tokens: {
        title: "Comprendre vos crédits",
        intro: "Chaque interaction avec l’IA consomme des tokens. Votre quota se renouvelle selon votre abonnement.",
        plans: {
          free: {
            name: "Free",
            quota: "Limité",
            features: ["Horoscope quotidien", "Lecture thème natal"],
            tagline: "Pour découvrir l’essentiel",
          },
          basic: {
            name: "Basic",
            quota: "10 tokens / jour",
            features: ["Chat prioritaire", "Bonus hebdomadaires", "Historique étendu"],
            tagline: "Idéal pour un suivi régulier",
          },
          premium: {
            name: "Premium",
            quota: "Usage étendu",
            features: ["Accès illimité", "Consultations offertes", "Support VIP"],
            tagline: "L’expérience astrologique ultime",
          },
        },
      },
      billing: {
        title: "Abonnement & Facturation",
        features: [
          "Gérez vos moyens de paiement",
          "Téléchargez vos factures",
          "Changez de plan à tout moment",
          "Consultez vos droits effectifs"
        ],
        cta: "Accéder à mon espace facturation",
      },
      supportEntry: {
        title: "Besoin d'aide personnalisée ?",
        description: "Choisissez une catégorie puis envoyez votre demande à notre équipe support. Vous pourrez ensuite suivre vos demandes directement depuis cette page.",
        cta: "Faire une demande de support",
      },
      categories: {
        title: "Comment pouvons-nous vous aider ?",
        loading: "Chargement des catégories…",
        error: "Erreur lors du chargement des catégories.",
        emptyTitle: "Aucune catégorie disponible",
        emptyDescription: "Le formulaire de support n’est pas disponible pour le moment. Veuillez réessayer plus tard.",
      },
      categoryDescriptions: {
        subscription_problem: "Problèmes liés à votre paiement ou accès premium.",
        billing_issue: "Questions sur vos factures ou prélèvements.",
        bug: "Signalement d’un comportement anormal de l’application.",
        account_access: "Difficultés de connexion ou gestion de profil.",
        feature_question: "Comment utiliser une fonctionnalité spécifique.",
        data_privacy: "Exercer vos droits RGPD ou gérer vos données.",
        other: "Toute autre demande non listée ci-dessus.",
      },
      form: {
        title: "Nouvelle demande de support",
        selectedCategory: "Catégorie : {category}",
        changeCategory: "Modifier",
        subject: {
          label: "Objet de votre demande",
          placeholder: "Ex : Problème de connexion",
          errorRequired: "L’objet est requis",
          errorMaxLen: "L’objet ne doit pas dépasser 160 caractères",
        },
        description: {
          label: "Description détaillée",
          placeholder: "Décrivez votre problème avec le plus de précisions possible…",
          hint: "Plus vous donnez de détails, plus vite nous pourrons vous aider.",
          errorRequired: "La description est requise",
          errorMinLen: "La description doit faire au moins 20 caractères",
        },
        submit: "Envoyer ma demande",
        submitting: "Envoi en cours…",
        successMessage: "Votre demande a été envoyée avec succès. Notre équipe reviendra vers vous prochainement.",
        errorInvalidCategory: "Catégorie invalide.",
        errorGeneric: "Une erreur est survenue lors de l’envoi. Veuillez réessayer.",
      },
      tickets: {
        title: "Mes demandes récentes",
        empty: "Vous n’avez pas encore soumis de demande de support.",
        emptyDescription: "Une question ? Un problème ? Nos experts sont là pour vous aider.",
        supportResponseLabel: "Réponse du support",
        statuses: {
          pending: "En attente",
          solved: "Résolu",
          canceled: "Annulé",
          open: "Ouvert",
          in_progress: "En cours",
          resolved: "Résolu",
          closed: "Fermé",
        },
        resolvedAt: "Résolu le {date}",
        loadMore: "Voir plus",
      },
    },
  },
  en: {
    help: {
      pageTitle: "Help Center & Support",
      hero: {
        title: "How can we help you today?",
        subtitle: "Find quick answers or contact our team of experts.",
        primaryCta: "Open a support ticket",
        secondaryCta: "Manage my subscription",
        steps: [
          "Choose a category",
          "Describe your need",
          "Follow the resolution"
        ]
      },
      shortcuts: {
        dashboard: {
          title: "Horoscope",
          benefit: "Follow your astral weather",
          action: "Go there",
        },
        chat: {
          title: "Chat",
          benefit: "Talk to your astrologer",
          action: "Chat",
        },
        natal: {
          title: "Natal Chart",
          benefit: "Understand your nature",
          action: "Explore",
        },
        consultations: {
          title: "Consultations",
          benefit: "Thematic analyses",
          action: "Discover",
        },
      },
      tokens: {
        title: "Understanding your credits",
        intro: "Each interaction with the AI consumes tokens. Your quota renews according to your subscription.",
        plans: {
          free: {
            name: "Free",
            quota: "Limited",
            features: ["Daily horoscope", "Natal chart reading"],
            tagline: "To discover the essentials",
          },
          basic: {
            name: "Basic",
            quota: "10 tokens / day",
            features: ["Priority chat", "Weekly bonuses", "Extended history"],
            tagline: "Ideal for regular follow-up",
          },
          premium: {
            name: "Premium",
            quota: "Extended usage",
            features: ["Unlimited access", "Free consultations", "VIP support"],
            tagline: "The ultimate astrological experience",
          },
        },
      },
      billing: {
        title: "Subscription & Billing",
        features: [
          "Manage your payment methods",
          "Download your invoices",
          "Change plan at any time",
          "Consult your actual rights"
        ],
        cta: "Access my billing space",
      },
      supportEntry: {
        title: "Need personalized help?",
        description: "Choose a category and send your request to our support team. You will then be able to track your requests directly from this page.",
        cta: "Create a support request",
      },
      categories: {
        title: "How can we help you?",
        loading: "Loading categories…",
        error: "Error loading categories.",
        emptyTitle: "No categories available",
        emptyDescription: "The support form is not available at the moment. Please try again later.",
      },
      categoryDescriptions: {
        subscription_problem: "Issues related to your payment or premium access.",
        billing_issue: "Questions about your invoices or charges.",
        bug: "Reporting abnormal application behavior.",
        account_access: "Login difficulties or profile management.",
        feature_question: "How to use a specific feature.",
        data_privacy: "Exercise your GDPR rights or manage your data.",
        other: "Any other request not listed above.",
      },
      form: {
        title: "New support request",
        selectedCategory: "Category: {category}",
        changeCategory: "Change",
        subject: {
          label: "Subject of your request",
          placeholder: "Ex: Connection issue",
          errorRequired: "Subject is required",
          errorMaxLen: "Subject must not exceed 160 characters",
        },
        description: {
          label: "Detailed description",
          placeholder: "Describe your problem with as much detail as possible…",
          hint: "The more details you provide, the faster we can help you.",
          errorRequired: "Description is required",
          errorMinLen: "Description must be at least 20 characters",
        },
        submit: "Send my request",
        submitting: "Sending…",
        successMessage: "Your request has been successfully sent. Our team will get back to you soon.",
        errorInvalidCategory: "Invalid category.",
        errorGeneric: "An error occurred during sending. Please try again.",
      },
      tickets: {
        title: "My recent requests",
        empty: "You haven't submitted any support requests yet.",
        emptyDescription: "A question? A problem? Our experts are here to help.",
        supportResponseLabel: "Support response",
        statuses: {
          pending: "Pending",
          solved: "Solved",
          canceled: "Canceled",
          open: "Open",
          in_progress: "In progress",
          resolved: "Resolved",
          closed: "Closed",
        },
        resolvedAt: "Resolved on {date}",
        loadMore: "See more",
      },
    },
  },
  es: {
    help: {
      pageTitle: "Centro de Ayuda y Soporte",
      hero: {
        title: "¿Cómo podemos ayudarte hoy?",
        subtitle: "Encuentra respuestas rápidas o contacta a nuestro equipo de expertos.",
        primaryCta: "Abrir un ticket de soporte",
        secondaryCta: "Gestionar mi suscripción",
        steps: [
          "Elija una categoría",
          "Describa su necesidad",
          "Siga la resolución"
        ]
      },
      shortcuts: {
        dashboard: {
          title: "Horóscopo",
          benefit: "Sigue tu clima astral",
          action: "Ir allí",
        },
        chat: {
          title: "Chat",
          benefit: "Habla con tu astrólogo",
          action: "Chatear",
        },
        natal: {
          title: "Carta Natal",
          benefit: "Comprende tu naturaleza",
          action: "Explorar",
        },
        consultations: {
          title: "Consultas",
          benefit: "Análisis temáticos",
          action: "Descubrir",
        },
      },
      tokens: {
        title: "Comprender sus créditos",
        intro: "Cada interacción con la IA consume tokens. Su cupo se renueva según su suscripción.",
        plans: {
          free: {
            name: "Free",
            quota: "Limitado",
            features: ["Horóscopo diario", "Lectura de carta natal"],
            tagline: "Para descubrir lo esencial",
          },
          basic: {
            name: "Basic",
            quota: "10 tokens / día",
            features: ["Chat prioritario", "Bonos semanales", "Historial extendido"],
            tagline: "Ideal para un seguimiento regular",
          },
          premium: {
            name: "Premium",
            quota: "Uso extendido",
            features: ["Acceso ilimitado", "Consultas gratuitas", "Soporte VIP"],
            tagline: "La experiencia astrológica definitiva",
          },
        },
      },
      billing: {
        title: "Suscripción y Facturación",
        features: [
          "Gestione sus métodos de pago",
          "Descargue sus facturas",
          "Cambie de plan en cualquier momento",
          "Consulte sus derechos efectivos"
        ],
        cta: "Acceder a mi espacio de facturación",
      },
      supportEntry: {
        title: "¿Necesita ayuda personalizada?",
        description: "Elija una categoría y envíe su solicitud a nuestro equipo de soporte. Luego podrá seguir sus solicitudes directamente desde esta página.",
        cta: "Crear una solicitud de soporte",
      },
      categories: {
        title: "¿Cómo podemos ayudarte?",
        loading: "Cargando categorías…",
        error: "Error al cargar las categorías.",
        emptyTitle: "No hay categorías disponibles",
        emptyDescription: "El formulario de soporte no está disponible por el momento. Por favor, inténtelo de nuevo más tarde.",
      },
      categoryDescriptions: {
        subscription_problem: "Problemas relacionados con su pago o acceso premium.",
        billing_issue: "Preguntas sobre sus facturas o cargos.",
        bug: "Informar un comportamiento anormal de la aplicación.",
        account_access: "Dificultades de inicio de sesión o gestión de perfil.",
        feature_question: "Cómo usar una función específica.",
        data_privacy: "Ejercer sus derechos RGPD o gestionar sus datos.",
        other: "Cualquier otra solicitud no enumerada anteriormente.",
      },
      form: {
        title: "Nueva solicitud de soporte",
        selectedCategory: "Categoría: {category}",
        changeCategory: "Modificar",
        subject: {
          label: "Asunto de su solicitud",
          placeholder: "Ej: Problema de conexión",
          errorRequired: "El asunto es obligatorio",
          errorMaxLen: "El asunto no debe superar los 160 caracteres",
        },
        description: {
          label: "Descripción detallada",
          placeholder: "Describa su problema con el mayor detalle posible…",
          hint: "Cuantos más detalles proporcione, más rápido podremos ayudarle.",
          errorRequired: "La descripción es obligatoria",
          errorMinLen: "La descripción debe tener al menos 20 caracteres",
        },
        submit: "Enviar mi solicitud",
        submitting: "Enviando…",
        successMessage: "Su solicitud ha sido enviada con éxito. Nuestro equipo se pondrá en contacto con usted pronto.",
        errorInvalidCategory: "Categoría inválida.",
        errorGeneric: "Ocurrió un error al enviar. Por favor, inténtelo de nuevo.",
      },
      tickets: {
        title: "Mis solicitudes recientes",
        empty: "Aún no ha enviado ninguna solicitud de soporte.",
        emptyDescription: "¿Una pregunta? ¿Un problema? Nuestros expertos están aquí para ayudar.",
        supportResponseLabel: "Respuesta del soporte",
        statuses: {
          pending: "Pendiente",
          solved: "Resuelto",
          canceled: "Cancelado",
          open: "Abierto",
          in_progress: "En curso",
          resolved: "Resuelto",
          closed: "Cerrado",
        },
        resolvedAt: "Resuelto el {date}",
        loadMore: "Ver más",
      },
    },
  },
};

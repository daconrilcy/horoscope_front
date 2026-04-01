import type { AstrologyLang } from "./astrology"

export type SettingsTranslation = {
  title: string
}
export const settingsTranslations = {
  page: {
    fr: { title: "Paramètres" },
    en: { title: "Settings" },
    es: { title: "Ajustes" },
  } as Record<AstrologyLang, { title: string }>,

  tabs: {
    fr: {
      navLabel: "Navigation des paramètres",
      account: "Compte",
      subscription: "Abonnement",
      usage: "Usage",
    },
    en: {
      navLabel: "Settings navigation",
      account: "Account",
      subscription: "Subscription",
      usage: "Usage",
    },
    es: {
      navLabel: "Navegación de ajustes",
      account: "Cuenta",
      subscription: "Suscripción",
      usage: "Uso",
    },
  } as Record<AstrologyLang, Record<"navLabel" | "account" | "subscription" | "usage", string>>,

  account: {
    fr: {
      title: "Informations du compte",
      email: "Adresse e-mail",
      memberSince: "Membre depuis",
      role: "Rôle",
      birthData: "Données de naissance",
      editBirthData: "Modifier mes données de naissance",
      deleteAccount: "Supprimer mon compte",
      loading: "Chargement...",
      error: "Impossible de charger vos informations",
      retry: "Réessayer",
      astrologerStyle: "Style d'astrologue",
      astrologerStyleDesc: "Personnalise l'interprétation de votre horoscope quotidien.",
      standard: "Standard",
      standardDesc: "Astrologie occidentale classique, ton accessible",
      vedique: "Védique",
      vediqueDesc: "Tradition védique, nakshatra, karma",
      humaniste: "Humaniste",
      humanisteDesc: "Archétypes jungiens, croissance personnelle",
      karmique: "Karmique",
      karmiqueDesc: "Leçons de vie, nœuds lunaires, cycles",
      psychologique: "Psychologique",
      psychologiqueDesc: "Patterns comportementaux, intégration",
      saving: "Enregistrement...",
      saved: "Préférences enregistrées",
      saveError: "Erreur lors de l'enregistrement",
      defaultAstrologer: "Astrologue par défaut",
      defaultAstrologerDesc: "Sélectionnez l'astrologue qui vous accompagnera par défaut.",
      automatic: "Automatique",
      automaticDesc: "Laisse l'application choisir pour vous",
      selected: "Sélectionné",
    },
    en: {
      title: "Account Information",
      email: "Email address",
      memberSince: "Member since",
      role: "Role",
      birthData: "Birth data",
      editBirthData: "Edit my birth data",
      deleteAccount: "Delete my account",
      loading: "Loading...",
      error: "Unable to load your information",
      retry: "Retry",
      astrologerStyle: "Astrologer Style",
      astrologerStyleDesc: "Personalize your daily horoscope interpretation.",
      standard: "Standard",
      standardDesc: "Classic western astrology, accessible tone",
      vedique: "Vedic",
      vediqueDesc: "Vedic tradition, nakshatra, karma",
      humaniste: "Humanistic",
      humanisteDesc: "Humanistic archetypes, personal growth",
      karmique: "Karmic",
      karmiqueDesc: "Life lessons, lunar nodes, cycles",
      psychologique: "Psychological",
      psychologiqueDesc: "Behavioral patterns, integration",
      saving: "Saving...",
      saved: "Preferences saved",
      saveError: "Error saving preferences",
      defaultAstrologer: "Default Astrologer",
      defaultAstrologerDesc: "Select the astrologer who will accompany you by default.",
      automatic: "Automatic",
      automaticDesc: "Let the application choose for you",
      selected: "Selected",
    },
    es: {
      title: "Información de la cuenta",
      email: "Correo electrónico",
      memberSince: "Miembro desde",
      role: "Rol",
      birthData: "Datos de nacimiento",
      editBirthData: "Editar mis datos de nacimiento",
      deleteAccount: "Eliminar mi cuenta",
      loading: "Cargando...",
      error: "No se pudo cargar su información",
      retry: "Reintentar",
      astrologerStyle: "Estilo de Astrólogo",
      astrologerStyleDesc: "Personaliza la interpretación de tu horóscopo diario.",
      standard: "Estándar",
      standardDesc: "Astrología occidental clásica, tono accesible",
      vedique: "Védico",
      vediqueDesc: "Tradición védica, nakshatra, karma",
      humaniste: "Humanista",
      humanisteDesc: "Arquetipos junguianos, crecimiento personal",
      karmique: "Kármico",
      karmiqueDesc: "Lecciones de vida, nodos lunares, ciclos",
      psychologique: "Psicológico",
      psychologiqueDesc: "Patrones de comportamiento, integración",
      saving: "Guardando...",
      saved: "Preferencias guardadas",
      saveError: "Error al guardar preferencias",
      defaultAstrologer: "Astrólogo por defecto",
      defaultAstrologerDesc: "Selecciona el astrólogo que te acompañará por defecto.",
      automatic: "Automático",
      automaticDesc: "Deja que la aplicación elija por ti",
      selected: "Seleccionado",
    },
  } as Record<
    AstrologyLang,
    {
      title: string
      email: string
      memberSince: string
      role: string
      birthData: string
      editBirthData: string
      deleteAccount: string
      loading: string
      error: string
      retry: string
      astrologerStyle: string
      astrologerStyleDesc: string
      standard: string
      standardDesc: string
      vedique: string
      vediqueDesc: string
      humaniste: string
      humanisteDesc: string
      karmique: string
      karmiqueDesc: string
      psychologique: string
      psychologiqueDesc: string
      saving: string
      saved: string
      saveError: string
      defaultAstrologer: string
      defaultAstrologerDesc: string
      automatic: string
      automaticDesc: string
      selected: string
    }
  >,

  subscription: {
    fr: {
      title: "Mon abonnement",
      availablePlans: "Plans disponibles",
      active: "Actif",
      paused: "En pause",
      currentPlan: "Plan actuel",
      selected: "Sélectionné",
      validatePlan: "Valider ce plan",
      reactivateSubscription: "Réactiver l'abonnement",
      cancelSubscription: "Résilier l'abonnement",
      reactivateWithBasic: "Réactiver en prenant Basic",
      reactivateWithPremium: "Réactiver en prenant Premium",
      validating: "Validation en cours...",
      planFree: "Gratuit",
      noActivePlan: "Aucun abonnement actif pour le moment.",
      freePlanLimitedAccess: "Vous êtes actuellement en mode gratuit avec des fonctionnalités limitées.",
      cancelSoon: "L'annulation vers le plan Gratuit sera bientôt disponible.",
      portalSyncPending: "Synchronisation de l'abonnement en cours...",
      cancelAlreadyScheduled: "La résiliation est déjà programmée pour votre prochaine échéance.",
      cancelScheduled: "Résiliation prévue le {{date}}",
      planChangeScheduled: "Passage à {{plan}} le {{date}}",
      currentPlanEndsOn: "Abonnement actif jusqu'au {{date}}",
      upgradeSyncPending: "Paiement accepté. Activation du plan {{plan}} en cours...",
      upgradeApplied: "Le plan {{plan}} est maintenant actif.",
      upgradeModalTitle: "Confirmer l'upgrade",
      upgradeModalLead:
        "Vous allez passer du plan {{currentPlan}} au plan {{targetPlan}} avec une facturation intermédiaire.",
      upgradeModalProration:
        "Stripe recalculera le prix du plan supérieur au prorata du temps restant sur la période en cours.",
      upgradeModalCredit:
        "Le montant déjà payé sur votre abonnement actuel sera déduit du paiement additionnel demandé.",
      upgradeModalRenewal:
        "Vos prochaines échéances seront ensuite facturées normalement sur le plan {{targetPlan}}.",
      upgradeModalCancel: "Plus tard",
      upgradeModalProceed: "Continuer vers Stripe",
      cancelConfirmTitle: "Résilier l'abonnement",
      cancelConfirmDesc: "Votre accès restera actif jusqu'au {{date}}.",
      trialBasicNotice:
        "Votre essai correspond au plan Basic. Le passage Premium sera disponible à la fin de l'essai.",
      buyCredits: "Acheter des crédits",
      buyCreditsDesc: "Besoin de plus de messages ? Achetez un pack de crédits supplémentaires.",
      soon: "Bientôt disponible",
      quotaUnit: "tokens",
      periodUnit: {
        day: "jour",
        month: "mois",
        week: "semaine",
        year: "an",
        lifetime: "vie",
      },
    },
    en: {
      title: "My subscription",
      availablePlans: "Available plans",
      active: "Active",
      paused: "Paused",
      currentPlan: "Current plan",
      selected: "Selected",
      validatePlan: "Validate this plan",
      reactivateSubscription: "Reactivate subscription",
      cancelSubscription: "Cancel subscription",
      reactivateWithBasic: "Reactivate with Basic",
      reactivateWithPremium: "Reactivate with Premium",
      validating: "Validating...",
      planFree: "Free",
      noActivePlan: "You do not have an active subscription at the moment.",
      freePlanLimitedAccess: "You are currently on the free tier with limited features.",
      cancelSoon: "Cancellation to the Free plan will be available soon.",
      portalSyncPending: "Subscription update in progress...",
      cancelAlreadyScheduled: "Cancellation is already scheduled for your next renewal date.",
      cancelScheduled: "Cancellation scheduled for {{date}}",
      planChangeScheduled: "Change to {{plan}} on {{date}}",
      currentPlanEndsOn: "Current subscription remains active until {{date}}",
      upgradeSyncPending: "Payment accepted. Activating the {{plan}} plan...",
      upgradeApplied: "The {{plan}} plan is now active.",
      upgradeModalTitle: "Confirm upgrade",
      upgradeModalLead:
        "You are about to switch from the {{currentPlan}} plan to the {{targetPlan}} plan with an intermediate charge.",
      upgradeModalProration:
        "Stripe will recalculate the higher plan using the prorated time remaining in your current billing period.",
      upgradeModalCredit:
        "The amount already paid on your current subscription will be deducted from the additional payment requested.",
      upgradeModalRenewal:
        "Your next renewals will then be billed normally on the {{targetPlan}} plan.",
      upgradeModalCancel: "Maybe later",
      upgradeModalProceed: "Continue to Stripe",
      cancelConfirmTitle: "Cancel subscription",
      cancelConfirmDesc: "Your access will remain active until {{date}}.",
      trialBasicNotice:
        "Your trial currently follows the Basic plan. Premium upgrades will be available after the trial ends.",
      buyCredits: "Buy credits",
      buyCreditsDesc: "Need more messages? Buy an additional credit pack.",
      soon: "Soon available",
      quotaUnit: "tokens",
      periodUnit: {
        day: "day",
        month: "month",
        week: "week",
        year: "year",
        lifetime: "lifetime",
      },
    },
    es: {
      title: "Mi suscripción",
      availablePlans: "Planes disponibles",
      active: "Activo",
      paused: "En pausa",
      currentPlan: "Plan actuel",
      selected: "Seleccionado",
      validatePlan: "Validar este plan",
      reactivateSubscription: "Reactivar la suscripción",
      cancelSubscription: "Cancelar la suscripción",
      reactivateWithBasic: "Reactivar con Basic",
      reactivateWithPremium: "Reactivar con Premium",
      validating: "Validando...",
      planFree: "Gratis",
      noActivePlan: "No tienes ninguna suscripción activa por ahora.",
      freePlanLimitedAccess: "Actualmente estás en el modo gratuito con funciones limitadas.",
      cancelSoon: "La cancelación al plan Gratuito estará disponible pronto.",
      portalSyncPending: "Sincronización de la suscripción en curso...",
      cancelAlreadyScheduled: "La cancelación ya está programada para la próxima fecha de renovación.",
      cancelScheduled: "Cancelación programada para el {{date}}",
      planChangeScheduled: "Cambio a {{plan}} el {{date}}",
      currentPlanEndsOn: "Suscripción activa hasta el {{date}}",
      upgradeSyncPending: "Pago aceptado. Activación del plan {{plan}} en curso...",
      upgradeApplied: "El plan {{plan}} ya está activo.",
      upgradeModalTitle: "Confirmar mejora",
      upgradeModalLead:
        "Vas a pasar del plan {{currentPlan}} al plan {{targetPlan}} con una facturación intermedia.",
      upgradeModalProration:
        "Stripe recalculará el plan superior según el prorrateo del tiempo restante en el período actual.",
      upgradeModalCredit:
        "El importe ya pagado en tu suscripción actual se descontará del pago adicional solicitado.",
      upgradeModalRenewal:
        "Tus próximas renovaciones se facturarán normalmente en el plan {{targetPlan}}.",
      upgradeModalCancel: "Más tarde",
      upgradeModalProceed: "Continuar con Stripe",
      cancelConfirmTitle: "Cancelar suscripción",
      cancelConfirmDesc: "Tu acceso permanecerá activo hasta el {{date}}.",
      trialBasicNotice:
        "Tu periodo de prueba sigue el plan Basic. El changement a Premium estará disponible al finalizar la prueba.",
      buyCredits: "Comprar crédits",
      buyCreditsDesc: "¿Necesitas más mensajes? Compra un paquete de créditos adicionales.",
      soon: "Próximamente disponible",
      quotaUnit: "tokens",
      periodUnit: {
        day: "día",
        month: "mes",
        week: "semana",
        year: "año",
        lifetime: "vida",
      },
    },
  } as Record<
    AstrologyLang,
    {
      title: string
      availablePlans: string
      active: string
      paused: string
      currentPlan: string
      selected: string
      validatePlan: string
      reactivateSubscription: string
      cancelSubscription: string
      reactivateWithBasic: string
      reactivateWithPremium: string
      validating: string
      planFree: string
      noActivePlan: string
      freePlanLimitedAccess: string
      cancelSoon: string
      portalSyncPending: string
      cancelAlreadyScheduled: string
      cancelScheduled: string
      planChangeScheduled: string
      currentPlanEndsOn: string
      upgradeSyncPending: string
      upgradeApplied: string
      upgradeModalTitle: string
      upgradeModalLead: string
      upgradeModalProration: string
      upgradeModalCredit: string
      upgradeModalRenewal: string
      upgradeModalCancel: string
      upgradeModalProceed: string
      cancelConfirmTitle: string
      cancelConfirmDesc: string
      trialBasicNotice: string
      buyCredits: string
      buyCreditsDesc: string
      soon: string
      quotaUnit: string
      periodUnit: Record<string, string>
    }
  >,

  usage: {
    fr: {
      title: "Statistiques d'usage",
      dailyUsage: "Usage des tokens",
      messagesUsed: "Messages envoyés",
      limit: "Limite",
      remaining: "Restants",
      resetAt: "Réinitialisation",
      resetHint: "Les tokens globaux sont comptabilisés sur le mois en cours.",
      day: "Usage du jour",
      week: "Usage de la semaine",
      month: "Usage du mois",
      totalLabel: "au total",
      loading: "Chargement des statistiques...",
      error: "Erreur de chargement",
      noData: "Aucune donnée disponible",
      retry: "Réessayer",
    },
    en: {
      title: "Usage Statistics",
      dailyUsage: "Token usage",
      messagesUsed: "Messages sent",
      limit: "Limit",
      remaining: "Remaining",
      resetAt: "Reset",
      resetHint: "Global tokens are measured over the current month.",
      day: "Today",
      week: "This week",
      month: "This month",
      totalLabel: "total",
      loading: "Loading statistics...",
      error: "Loading error",
      noData: "No data available",
      retry: "Retry",
    },
    es: {
      title: "Estadísticas de uso",
      dailyUsage: "Uso de tokens",
      messagesUsed: "Mensajes enviados",
      limit: "Límite",
      remaining: "Restantes",
      resetAt: "Reinicio",
      resetHint: "Los tokens globales se cuentan sobre el mes actual.",
      day: "Uso del día",
      week: "Uso de la semana",
      month: "Uso del mes",
      totalLabel: "en total",
      loading: "Cargando estadísticas...",
      error: "Error de carga",
      noData: "Sin datos disponibles",
      retry: "Reintentar",
    },
  } as Record<
    AstrologyLang,
    {
      title: string
      dailyUsage: string
      messagesUsed: string
      limit: string
      remaining: string
      resetAt: string
      resetHint: string
      day: string
      week: string
      month: string
      totalLabel: string
      loading: string
      error: string
      noData: string
      retry: string
    }
  >,

  usageErrors: {
    network_error: {
      fr: "Problème de connexion réseau. Vérifiez votre connexion.",
      en: "Network connection problem. Please check your connection.",
      es: "Problema de conexión de red. Verifique su conexión.",
    },
    unauthorized: {
      fr: "Session expirée. Veuillez vous reconnecter.",
      en: "Session expired. Please log in again.",
      es: "Sesión expirada. Por favor, inicie sesión de nuevo.",
    },
    server_error: {
      fr: "Erreur serveur. Réessayez dans quelques instants.",
      en: "Server error. Please try again in a moment.",
      es: "Error del servidor. Inténtelo de nuevo en unos momentos.",
    },
    default: {
      fr: "Une erreur inattendue est survenue.",
      en: "An unexpected error occurred.",
      es: "Ocurrió un error inesperado.",
    },
  } as Record<string, Record<AstrologyLang, string>>,

  deleteModal: {
    fr: {
      title: "Supprimer mon compte",
      initialMessage:
        "Êtes-vous sûr de vouloir supprimer votre compte ? Cette action supprimera définitivement toutes vos données.",
      confirmMessage:
        "Cette action est irréversible. Pour confirmer, tapez le mot ci-dessous :",
      confirmPlaceholder: "Tapez ici...",
      confirmWord: "SUPPRIMER",
      confirmHint: 'Tapez "SUPPRIMER" pour confirmer',
      cancel: "Annuler",
      confirm: "Confirmer la suppression",
      processing: "Suppression en cours...",
      error: "Une erreur est survenue. Veuillez réessayer.",
      mismatch: "Le mot ne correspond pas",
    },
    en: {
      title: "Delete my account",
      initialMessage:
        "Are you sure you want to delete your account? This action will permanently delete all your data.",
      confirmMessage:
        "This action is irreversible. To confirm, type the word below:",
      confirmPlaceholder: "Type here...",
      confirmWord: "DELETE",
      confirmHint: 'Type "DELETE" to confirm',
      cancel: "Cancel",
      confirm: "Confirm deletion",
      processing: "Deleting...",
      error: "An error occurred. Please try again.",
      mismatch: "The word does not match",
    },
    es: {
      title: "Eliminar mi cuenta",
      initialMessage:
        "¿Está seguro de que desea eliminar su cuenta? Esta acción eliminará permanentemente todos sus datos.",
      confirmMessage:
        "Esta acción es irreversible. Para confirmar, escriba la palabra a continuación:",
      confirmPlaceholder: "Escriba aquí...",
      confirmWord: "ELIMINAR",
      confirmHint: 'Escriba "ELIMINAR" para confirmar',
      cancel: "Cancelar",
      confirm: "Confirmar eliminación",
      processing: "Eliminando...",
      error: "Ocurrió un error. Por favor, inténtelo de nuevo.",
      mismatch: "La palabra no coincide",
    },
  } as Record<
    AstrologyLang,
    {
      title: string
      initialMessage: string
      confirmMessage: string
      confirmPlaceholder: string
      confirmWord: string
      confirmHint: string
      cancel: string
      confirm: string
      processing: string
      error: string
      mismatch: string
    }
  >,
}

import type { AstrologyLang } from "./astrology"

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
    }
  >,

  subscription: {
    fr: { title: "Mon abonnement" },
    en: { title: "My subscription" },
    es: { title: "Mi suscripción" },
  } as Record<AstrologyLang, { title: string }>,

  usage: {
    fr: {
      title: "Statistiques d'usage",
      dailyUsage: "Usage quotidien",
      messagesUsed: "Messages envoyés",
      limit: "Limite",
      remaining: "Restants",
      resetAt: "Réinitialisation à",
      loading: "Chargement des statistiques...",
      error: "Erreur de chargement",
      noData: "Aucune donnée disponible",
      retry: "Réessayer",
    },
    en: {
      title: "Usage Statistics",
      dailyUsage: "Daily usage",
      messagesUsed: "Messages sent",
      limit: "Limit",
      remaining: "Remaining",
      resetAt: "Resets at",
      loading: "Loading statistics...",
      error: "Loading error",
      noData: "No data available",
      retry: "Retry",
    },
    es: {
      title: "Estadísticas de uso",
      dailyUsage: "Uso diario",
      messagesUsed: "Mensajes enviados",
      limit: "Límite",
      remaining: "Restantes",
      resetAt: "Se reinicia a las",
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

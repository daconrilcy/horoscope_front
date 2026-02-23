import type { AstrologyLang } from "./astrology"

type PricingTranslations = {
  title: string
  description: string
  loading: string
  errorLoading: string
  unknownError: string
  apiNote: string
  emptyState: string
  tableLabel: string
  colCode: string
  colName: string
  colPrice: string
  colLimit: string
  colStatus: string
  statusActive: string
  statusInactive: string
  upcomingTitle: string
  upcomingModify: string
  upcomingCreate: string
  upcomingActivate: string
  upcomingNote: string
}

export const adminTranslations = {
  page: {
    fr: { title: "Administration", backToHub: "← Retour au hub" },
    en: { title: "Administration", backToHub: "← Back to hub" },
    es: { title: "Administración", backToHub: "← Volver al hub" },
  } as Record<AstrologyLang, { title: string; backToHub: string }>,

  sections: {
    fr: {
      pricing: "Gestion des tarifs",
      monitoring: "Monitoring Ops",
      personas: "Personas Astrologues",
      reconciliation: "Réconciliation B2B",
    },
    en: {
      pricing: "Pricing Management",
      monitoring: "Ops Monitoring",
      personas: "Astrologer Personas",
      reconciliation: "B2B Reconciliation",
    },
    es: {
      pricing: "Gestión de tarifas",
      monitoring: "Monitoreo Ops",
      personas: "Personas Astrólogos",
      reconciliation: "Reconciliación B2B",
    },
  } as Record<AstrologyLang, Record<"pricing" | "monitoring" | "personas" | "reconciliation", string>>,

  pricing: {
    fr: {
      title: "Gestion des Tarifs",
      description: "Visualisation des plans tarifaires configurés dans le système.",
      loading: "Chargement des plans...",
      errorLoading: "Erreur lors du chargement des plans.",
      unknownError: "Erreur inconnue",
      apiNote:
        "Note : L'API GET /v1/billing/plans n'est pas encore implémentée côté backend. Cette fonctionnalité nécessite une story dédiée pour l'API admin.",
      emptyState: "Aucun plan tarifaire configuré.",
      tableLabel: "Plans tarifaires",
      colCode: "Code",
      colName: "Nom",
      colPrice: "Prix mensuel",
      colLimit: "Limite messages/jour",
      colStatus: "Statut",
      statusActive: "Actif",
      statusInactive: "Inactif",
      upcomingTitle: "Fonctionnalités à venir",
      upcomingModify: "Modification des tarifs existants",
      upcomingCreate: "Création de nouveaux plans",
      upcomingActivate: "Activation/désactivation des plans",
      upcomingNote:
        "Ces fonctionnalités nécessitent l'implémentation d'une API admin dédiée (hors scope de la story 16.7).",
    },
    en: {
      title: "Pricing Management",
      description: "View pricing plans configured in the system.",
      loading: "Loading plans...",
      errorLoading: "Error loading plans.",
      unknownError: "Unknown error",
      apiNote:
        "Note: The GET /v1/billing/plans API is not yet implemented on the backend. This feature requires a dedicated admin API story.",
      emptyState: "No pricing plans configured.",
      tableLabel: "Pricing plans",
      colCode: "Code",
      colName: "Name",
      colPrice: "Monthly price",
      colLimit: "Daily message limit",
      colStatus: "Status",
      statusActive: "Active",
      statusInactive: "Inactive",
      upcomingTitle: "Upcoming features",
      upcomingModify: "Modify existing plans",
      upcomingCreate: "Create new plans",
      upcomingActivate: "Activate/deactivate plans",
      upcomingNote:
        "These features require the implementation of a dedicated admin API (out of scope for story 16.7).",
    },
    es: {
      title: "Gestión de Tarifas",
      description: "Visualización de los planes tarifarios configurados en el sistema.",
      loading: "Cargando planes...",
      errorLoading: "Error al cargar los planes.",
      unknownError: "Error desconocido",
      apiNote:
        "Nota: La API GET /v1/billing/plans aún no está implementada en el backend. Esta funcionalidad requiere una story dedicada para la API admin.",
      emptyState: "Ningún plan tarifario configurado.",
      tableLabel: "Planes tarifarios",
      colCode: "Código",
      colName: "Nombre",
      colPrice: "Precio mensual",
      colLimit: "Límite mensajes/día",
      colStatus: "Estado",
      statusActive: "Activo",
      statusInactive: "Inactivo",
      upcomingTitle: "Próximas funcionalidades",
      upcomingModify: "Modificación de tarifas existentes",
      upcomingCreate: "Creación de nuevos planes",
      upcomingActivate: "Activación/desactivación de planes",
      upcomingNote:
        "Estas funcionalidades requieren la implementación de una API admin dedicada (fuera del alcance de la story 16.7).",
    },
  } as Record<AstrologyLang, PricingTranslations>,

  monitoring: {
    fr: { title: "Monitoring Opérationnel" },
    en: { title: "Operational Monitoring" },
    es: { title: "Monitoreo Operacional" },
  } as Record<AstrologyLang, { title: string }>,

  personas: {
    fr: { title: "Personas Astrologues" },
    en: { title: "Astrologer Personas" },
    es: { title: "Personas Astrólogos" },
  } as Record<AstrologyLang, { title: string }>,

  reconciliation: {
    fr: { title: "Réconciliation B2B" },
    en: { title: "B2B Reconciliation" },
    es: { title: "Reconciliación B2B" },
  } as Record<AstrologyLang, { title: string }>,
}

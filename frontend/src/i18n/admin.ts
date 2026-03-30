// @ts-nocheck
import type { AstrologyLang } from "./astrology"

export interface AdminTranslation {
  page: { title: string; backToHub: string }
  sections: {
    pricing: string
    monitoring: string
    personas: string
    reconciliation: string
  }
  b2b: {
    astrology: {
      title: string
      description: string
      apiKeyLabel: string
      submit: string
      loading: string
      error: (msg: string, code: string) => string
      empty: string
      apiVersion: (v: string, ref: string) => string
    }
    billing: {
      title: string
      description: string
      apiKeyLabel: string
      submit: string
      loading: string
      error: (msg: string, code: string) => string
      empty: string
      period: (start: string, end: string) => string
      plan: (name: string) => string
      fixed: (val: string) => string
      variable: (val: string) => string
      total: (val: string) => string
      historyTitle: string
    }
    editorial: {
      title: string
      description: string
      apiKeyLabel: string
      submitLoad: string
      submitSave: string
      loading: string
      errorRead: (msg: string, code: string) => string
      errorUpdate: (msg: string, code: string) => string
      empty: string
      activeVersion: (v: string, status: string) => string
      statusActive: string
      statusInactive: string
      toneLabel: string
      tones: { neutral: string; friendly: string; premium: string }
      lengthLabel: string
      lengths: { short: string; medium: string; long: string }
      formatLabel: string
      formats: { paragraph: string; bullet: string }
      preferredLabel: string
      avoidedLabel: string
    }
    usage: {
      title: string
      description: string
      apiKeyLabel: string
      submit: string
      loading: string
      error: (msg: string, code: string) => string
      empty: string
      daily: (consumed: number, limit: number, remaining: number) => string
      monthly: (consumed: number, limit: number, remaining: number) => string
      limitMode: (mode: string) => string
      blocking: (active: boolean) => string
    }
    reconciliation: {
      title: string
      description: string
      accountLabel: string
      severityLabel: string
      severities: { all: string; major: string; minor: string; none: string }
      submit: string
      loading: string
      errorList: (msg: string, code: string) => string
      errorDetail: (msg: string, code: string) => string
      errorAction: (msg: string, code: string) => string
      empty: string
      resultsTitle: (total: number) => string
      detailTitle: string
      noteLabel: string
      actionExecuted: (action: string, state: string) => string
    }
    opsPersona: {
      title: string
      description: string
      loading: string
      errorLoad: string
      toneLabel: string
      prudenceLabel: string
      scopeLabel: string
      styleLabel: string
      successUpdate: string
      successRollback: string
      errorGeneral: (msg: string) => string
    }
    opsMonitoring: {
      title: string
      description: string
      windowLabel: string
      error: (msg: string) => string
      empty: string
      scope: (val: string) => string
      totalMessages: (val: number) => string
      p95Latency: (val: string) => string
      successRollback: string
    }
    credentials: {
      title: string
      description: string
      loading: string
      errorLoad: string
      accountTitle: (name: string) => string
      accountStatus: (status: string) => string
      keyTitle: (prefix: string) => string
      createdDate: (date: string) => string
      errorGenerate: (msg: string) => string
      errorRotate: (msg: string) => string
      generateLabel: string
      rotateLabel: string
    }
    support: {
      title: string
      description: string
      targetUserLabel: string
      privacyRequests: (count: number) => string
      noPrivacyRequests: string
      recentAuditTitle: string
    }
    privacy: {
      title: string
      description: string
      requestExport: string
      requestDelete: string
      statusExport: (status: string) => string
      emptyExport: string
      errorExportStatus: (msg: string) => string
      statusDelete: (status: string) => string
      emptyDelete: string
      errorDeleteStatus: (msg: string) => string
      errorExportRequest: (msg: string) => string
      errorDeleteRequest: (msg: string) => string
    }
  }
}

export interface PricingTranslations {
  title: string
  description: string
  loading: string
  errorLoading: string
  unknownError: string
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

  monitoring: {
    fr: { title: "Monitoring Opérationnel" },
    en: { title: "Operational Monitoring" },
    es: { title: "Monitoreo Operativo" },
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

  b2b: {
    fr: {
      astrology: {
        title: "API B2B Astrologie",
        description: "Testez l'endpoint contractuel hebdomadaire par signe avec une clé API entreprise.",
        apiKeyLabel: "Clé API B2B",
        submit: "Récupérer weekly-by-sign",
        loading: "Chargement weekly-by-sign...",
        error: (msg, code) => `Erreur API B2B: ${msg} (${code})`,
        empty: "Aucun contenu astrologique disponible pour cette période.",
        apiVersion: (v, ref) => `Version API: ${v} · Référence: ${ref}`,
      },
      billing: {
        title: "Facturation B2B",
        description: "Consultez votre relevé facturé (fixe + volume) pour la dernière période clôturée.",
        apiKeyLabel: "Clé API B2B",
        submit: "Récupérer le relevé facturé",
        loading: "Chargement facturation B2B...",
        error: (msg, code) => `Erreur facturation B2B: ${msg} (${code})`,
        empty: "Aucun cycle de facturation clôturé pour ce compte.",
        period: (start, end) => `Période: ${start} -> ${end}`,
        plan: (name) => `Plan: ${name}`,
        fixed: (val) => `Fixe: ${val}`,
        variable: (val) => `Variable: ${val}`,
        total: (val) => `Total: ${val}`,
        historyTitle: "Historique récent",
      },
      editorial: {
        title: "Personnalisation éditoriale B2B",
        description: "Configurez le style des réponses astrologiques selon votre ligne éditoriale.",
        apiKeyLabel: "Clé API B2B",
        submitLoad: "Charger la configuration",
        submitSave: "Enregistrer la configuration",
        loading: "Chargement configuration éditoriale...",
        errorRead: (msg, code) => `Erreur lecture éditoriale: ${msg} (${code})`,
        errorUpdate: (msg, code) => `Erreur mise à jour éditoriale: ${msg} (${code})`,
        empty: "Aucune configuration chargée.",
        activeVersion: (v, status) => `Version active: ${v} (${status})`,
        statusActive: "active",
        statusInactive: "inactive",
        toneLabel: "Ton",
        tones: { neutral: "Neutre", friendly: "Amical", premium: "Premium" },
        lengthLabel: "Longueur",
        lengths: { short: "Court", medium: "Moyen", long: "Long" },
        formatLabel: "Format",
        formats: { paragraph: "Paragraphe", bullet: "Liste à puces" },
        preferredLabel: "Mots à privilégier (séparés par des virgules)",
        avoidedLabel: "Mots à éviter (séparés par des virgules)",
      },
      usage: {
        title: "Consommation B2B",
        description: "Consultez limites contractuelles et volumes utilisés pour votre credential API.",
        apiKeyLabel: "Clé API B2B",
        submit: "Récupérer le résumé de consommation",
        loading: "Chargement consommation B2B...",
        error: (msg, code) => `Erreur consommation B2B: ${msg} (${code})`,
        empty: "Aucune consommation enregistrée pour cette période.",
        daily: (c, l, r) => `Quotidien: ${c}/${l} (${r} restant)`,
        monthly: (c, l, r) => `Mensuel: ${c}/${l} (${r} restant)`,
        limitMode: (mode) => `Mode de limite: ${mode}`,
        blocking: (active) => `Blocage actif: ${active ? "oui" : "non"}`,
      },
      reconciliation: {
        title: "Réconciliation B2B Ops",
        description: "Compare l'usage mesuré et la facturation afin de détecter les écarts avant impact client.",
        accountLabel: "Compte entreprise (optionnel)",
        severityLabel: "Sévérité",
        severities: { all: "Toutes", major: "Majeure", minor: "Mineure", none: "Aucune" },
        submit: "Charger la réconciliation",
        loading: "Chargement réconciliation...",
        errorList: (msg, code) => `Erreur réconciliation liste: ${msg} (${code})`,
        errorDetail: (msg, code) => `Erreur réconciliation détail: ${msg} (${code})`,
        errorAction: (msg, code) => `Erreur action réconciliation: ${msg} (${code})`,
        empty: "Aucun écart de réconciliation pour ces filtres.",
        resultsTitle: (total) => `Écarts identifiés (${total})`,
        detailTitle: "Détail écart",
        noteLabel: "Note action (optionnel)",
        actionExecuted: (action, state) => `Action exécutée: ${action} (${state})`,
      },
      opsPersona: {
        title: "Paramétrage Persona Ops",
        description: "Contrôlez le ton et les bornes de l'astrologue virtuel.",
        loading: "Chargement configuration persona...",
        errorLoad: "Erreur chargement persona.",
        toneLabel: "Tone",
        prudenceLabel: "Prudence",
        scopeLabel: "Scope",
        styleLabel: "Style",
        successUpdate: "Configuration persona mise à jour.",
        successRollback: "Rollback persona effectué.",
        errorGeneral: (msg) => `Erreur persona: ${msg}`,
      },
      opsMonitoring: {
        title: "Monitoring conversationnel Ops",
        description: "Suivi de la qualité conversationnelle et action rapide de rollback.",
        windowLabel: "Fenêtre",
        error: (msg) => `Erreur monitoring: ${msg}`,
        empty: "Aucune donnée conversationnelle sur cette fenêtre.",
        scope: (val) => `Portée agrégation: ${val}`,
        totalMessages: (val) => `Messages total: ${val}`,
        p95Latency: (val) => `Latence p95: ${val}`,
        successRollback: "Rollback persona effectué.",
      },
      credentials: {
        title: "API Entreprise",
        description: "Générez et régénérez vos clés API B2B.",
        loading: "Chargement des credentials...",
        errorLoad: "Impossible de charger les credentials.",
        accountTitle: (name) => `Compte: ${name}`,
        accountStatus: (status) => `Status compte: ${status}`,
        keyTitle: (prefix) => `Clé: ${prefix}***`,
        createdDate: (date) => `Créée le: ${date}`,
        errorGenerate: (msg) => `Erreur génération clé: ${msg}`,
        errorRotate: (msg) => `Erreur régénération clé: ${msg}`,
        generateLabel: "Générer une clé API",
        rotateLabel: "Régénérer la clé active",
      },
      support: {
        title: "Support et opérations",
        description: "Consultez le dossier utilisateur et gérez les incidents.",
        targetUserLabel: "Utilisateur cible",
        privacyRequests: (count) => `Demandes RGPD: ${count}`,
        noPrivacyRequests: "Aucune demande RGPD.",
        recentAuditTitle: "Audit récent",
      },
      privacy: {
        title: "Confidentialité et données",
        description: "Demandez un export de vos données ou la suppression de votre compte.",
        requestExport: "Demander un export",
        requestDelete: "Supprimer mes données",
        statusExport: (status) => `Statut export: ${status}`,
        emptyExport: "Aucune demande d'export pour le moment.",
        errorExportStatus: (msg) => `Erreur statut export: ${msg}`,
        statusDelete: (status) => `Statut suppression: ${status}`,
        emptyDelete: "Aucune demande de suppression pour le moment.",
        errorDeleteStatus: (msg) => `Erreur statut suppression: ${msg}`,
        errorExportRequest: (msg) => `Erreur demande export: ${msg}`,
        errorDeleteRequest: (msg) => `Erreur demande suppression: ${msg}`,
      },
    },
    en: {
      astrology: {
        title: "B2B Astrology API",
        description: "Test the contractual weekly by sign endpoint with a business API key.",
        apiKeyLabel: "B2B API Key",
        submit: "Fetch weekly-by-sign",
        loading: "Loading weekly-by-sign...",
        error: (msg, code) => `B2B API Error: ${msg} (${code})`,
        empty: "No astrology content available for this period.",
        apiVersion: (v, ref) => `API Version: ${v} · Reference: ${ref}`,
      },
      billing: {
        title: "B2B Billing",
        description: "View your billed statement (fixed + volume) for the last closed period.",
        apiKeyLabel: "B2B API Key",
        submit: "Fetch billed statement",
        loading: "Loading B2B billing...",
        error: (msg, code) => `B2B billing error: ${msg} (${code})`,
        empty: "No closed billing cycles for this account.",
        period: (start, end) => `Period: ${start} -> ${end}`,
        plan: (name) => `Plan: ${name}`,
        fixed: (val) => `Fixed: ${val}`,
        variable: (val) => `Variable: ${val}`,
        total: (val) => `Total: ${val}`,
        historyTitle: "Recent history",
      },
      editorial: {
        title: "B2B Editorial Customization",
        description: "Configure the style of astrology responses according to your editorial line.",
        apiKeyLabel: "B2B API Key",
        submitLoad: "Load configuration",
        submitSave: "Save configuration",
        loading: "Loading editorial configuration...",
        errorRead: (msg, code) => `Editorial read error: ${msg} (${code})`,
        errorUpdate: (msg, code) => `Editorial update error: ${msg} (${code})`,
        empty: "No configuration loaded.",
        activeVersion: (v, status) => `Active version: ${v} (${status})`,
        statusActive: "active",
        statusInactive: "inactive",
        toneLabel: "Tone",
        tones: { neutral: "Neutral", friendly: "Friendly", premium: "Premium" },
        lengthLabel: "Length",
        lengths: { short: "Short", medium: "Medium", long: "Long" },
        formatLabel: "Format",
        formats: { paragraph: "Paragraph", bullet: "Bullet points" },
        preferredLabel: "Words to prioritize (comma separated)",
        avoidedLabel: "Words to avoid (comma separated)",
      },
      usage: {
        title: "B2B Usage",
        description: "View contractual limits and volumes used for your API credential.",
        apiKeyLabel: "B2B API Key",
        submit: "Fetch usage summary",
        loading: "Loading B2B usage...",
        error: (msg, code) => `B2B usage error: ${msg} (${code})`,
        empty: "No consumption recorded for this period.",
        daily: (c, l, r) => `Daily: ${c}/${l} (${r} remaining)`,
        monthly: (c, l, r) => `Monthly: ${c}/${l} (${r} remaining)`,
        limitMode: (mode) => `Limit mode: ${mode}`,
        blocking: (active) => `Active blocking: ${active ? "yes" : "no"}`,
      },
      reconciliation: {
        title: "B2B Ops Reconciliation",
        description: "Compare measured usage and billing to detect discrepancies before customer impact.",
        accountLabel: "Business account (optional)",
        severityLabel: "Severity",
        severities: { all: "All", major: "Major", minor: "Minor", none: "None" },
        submit: "Load reconciliation",
        loading: "Loading reconciliation...",
        errorList: (msg, code) => `Reconciliation list error: ${msg} (${code})`,
        errorDetail: (msg, code) => `Reconciliation detail error: ${msg} (${code})`,
        errorAction: (msg, code) => `Reconciliation action error: ${msg} (${code})`,
        empty: "No reconciliation discrepancies for these filters.",
        resultsTitle: (total) => `Identified discrepancies (${total})`,
        detailTitle: "Discrepancy detail",
        noteLabel: "Action note (optional)",
        actionExecuted: (action, state) => `Action executed: ${action} (${state})`,
      },
      opsPersona: {
        title: "Ops Persona Settings",
        description: "Control the tone and boundaries of the virtual astrologer.",
        loading: "Loading persona configuration...",
        errorLoad: "Error loading persona.",
        toneLabel: "Tone",
        prudenceLabel: "Prudence",
        scopeLabel: "Scope",
        styleLabel: "Style",
        successUpdate: "Persona configuration updated.",
        successRollback: "Persona rollback performed.",
        errorGeneral: (msg) => `Persona error: ${msg}`,
      },
      opsMonitoring: {
        title: "Ops Conversational Monitoring",
        description: "Monitor conversational quality and rapid rollback actions.",
        windowLabel: "Window",
        error: (msg) => `Monitoring error: ${msg}`,
        empty: "No conversational data for this window.",
        scope: (val) => `Aggregation scope: ${val}`,
        totalMessages: (val) => `Total messages: ${val}`,
        p95Latency: (val) => `p95 Latency: ${val}`,
        successRollback: "Persona rollback performed.",
      },
      credentials: {
        title: "Business API",
        description: "Generate and regenerate your B2B API keys.",
        loading: "Loading credentials...",
        errorLoad: "Unable to load credentials.",
        accountTitle: (name) => `Account: ${name}`,
        accountStatus: (status) => `Account status: ${status}`,
        keyTitle: (prefix) => `Key: ${prefix}***`,
        createdDate: (date) => `Created on: ${date}`,
        errorGenerate: (msg) => `Key generation error: ${msg}`,
        errorRotate: (msg) => `Key regeneration error: ${msg}`,
        generateLabel: "Generate API Key",
        rotateLabel: "Regenerate Active Key",
      },
      support: {
        title: "Support and Operations",
        description: "View user file and manage incidents.",
        targetUserLabel: "Target user",
        privacyRequests: (count) => `Privacy requests: ${count}`,
        noPrivacyRequests: "No privacy requests.",
        recentAuditTitle: "Recent audit",
      },
      privacy: {
        title: "Privacy and Data",
        description: "Request an export of your data or account deletion.",
        requestExport: "Request Data Export",
        requestDelete: "Delete My Data",
        statusExport: (status) => `Export status: ${status}`,
        emptyExport: "No export requests yet.",
        errorExportStatus: (msg) => `Export status error: ${msg}`,
        statusDelete: (status) => `Deletion status: ${status}`,
        emptyDelete: "No deletion requests yet.",
        errorDeleteStatus: (msg) => `Deletion status error: ${msg}`,
        errorExportRequest: (msg) => `Export request error: ${msg}`,
        errorDeleteRequest: (msg) => `Deletion request error: ${msg}`,
      },
    },
    es: {
      astrology: {
        title: "API B2B Astrología",
        description: "Pruebe el endpoint contractual semanal por signe con une clave API de empresa.",
        apiKeyLabel: "Clave API B2B",
        submit: "Obtener semanal-por-signo",
        loading: "Cargando semanal-por-signo...",
        error: (msg, code) => `Error API B2B: ${msg} (${code})`,
        empty: "No hay contenido astrológico disponible para este período.",
        apiVersion: (v, ref) => `Versión API: ${v} · Referencia: ${ref}`,
      },
      billing: {
        title: "Facturation B2B",
        description: "Consulte su estado de cuenta facturado (fijo + volumen) para el último período cerrado.",
        apiKeyLabel: "Clave API B2B",
        submit: "Obtener estado de cuenta",
        loading: "Cargando facturación B2B...",
        error: (msg, code) => `Error de facturación B2B: ${msg} (${code})`,
        empty: "No hay ciclos de facturación cerrados para esta cuenta.",
        period: (start, end) => `Período: ${start} -> ${end}`,
        plan: (name) => `Plan: ${name}`,
        fixed: (val) => `Fijo: ${val}`,
        variable: (val) => `Variable: ${val}`,
        total: (val) => `Total: ${val}`,
        historyTitle: "Historial reciente",
      },
      editorial: {
        title: "Personalización editorial B2B",
        description: "Configure el estilo de las respuestas astrológicas según su línea editorial.",
        apiKeyLabel: "Clave API B2B",
        submitLoad: "Cargar configuración",
        submitSave: "Guardar configuración",
        loading: "Cargando configuración editorial...",
        errorRead: (msg, code) => `Error de lectura editorial: ${msg} (${code})`,
        errorUpdate: (msg, code) => `Error de actualización editorial: ${msg} (${code})`,
        empty: "No hay configuración cargada.",
        activeVersion: (v, status) => `Versión activa: ${v} (${status})`,
        statusActive: "activa",
        statusInactive: "inactiva",
        toneLabel: "Tono",
        tones: { neutral: "Neutro", friendly: "Amistoso", premium: "Premium" },
        lengthLabel: "Longitud",
        lengths: { short: "Corto", medium: "Medio", long: "Largo" },
        formatLabel: "Formato",
        formats: { paragraph: "Párrafo", bullet: "Lista" },
        preferredLabel: "Palabras a priorizar (separadas por comas)",
        avoidedLabel: "Palabras a evitar (separadas par comas)",
      },
      usage: {
        title: "Consumo B2B",
        description: "Consulte los límites contractuales y los volúmenes utilisés para su credencial API.",
        apiKeyLabel: "Clave API B2B",
        submit: "Obtener resumen de consumo",
        loading: "Cargando consumo B2B...",
        error: (msg, code) => `Error de consumo B2B: ${msg} (${code})`,
        empty: "No hay consumo registrado para este período.",
        daily: (c, l, r) => `Diario: ${c}/${l} (${r} restante)`,
        monthly: (c, l, r) => `Mensuel: ${c}/${l} (${r} restante)`,
        limitMode: (mode) => `Modo de limite: ${mode}`,
        blocking: (active) => `Bloqueo activo: ${active ? "sí" : "no"}`,
      },
      reconciliation: {
        title: "Reconciliación B2B Ops",
        description: "Compare el uso medido y la facturación para detectar discrepancias antes del impacto en el cliente.", 
        accountLabel: "Cuenta de empresa (opcional)",
        severityLabel: "Severidad",
        severities: { all: "Todas", major: "Mayor", minor: "Menor", none: "Ninguna" },
        submit: "Cargar reconciliación",
        loading: "Cargando reconciliación...",
        errorList: (msg, code) => `Error de lista de reconciliación: ${msg} (${code})`,
        errorDetail: (msg, code) => `Error de detalle de reconciliación: ${msg} (${code})`,
        errorAction: (msg, code) => `Error de acción de reconciliación: ${msg} (${code})`,
        empty: "No hay discrepancias de reconciliación para estos filtros.",
        resultsTitle: (total) => `Discrepancias identificadas (${total})`,
        detailTitle: "Detalle de discrepancia",
        noteLabel: "Nota de acción (opcional)",
        actionExecuted: (action, state) => `Action exécutée: ${action} (${state})`,
      },
      opsPersona: {
        title: "Ajustes de Persona Ops",
        description: "Controle el tono y los límites del astrólogo virtual.",
        loading: "Cargando configuración de persona...",
        errorLoad: "Error al cargar persona.",
        toneLabel: "Tono",
        prudenceLabel: "Prudencia",
        scopeLabel: "Alcance",
        styleLabel: "Estilo",
        successUpdate: "Configuración de persona actualizada.",
        successRollback: "Rollback de persona realizado.",
        errorGeneral: (msg) => `Error de persona: ${msg}`,
      },
      opsMonitoring: {
        title: "Monitoreo Conversacional Ops",
        description: "Supervise la qualité conversacional y acciones rápidas de rollback.",
        windowLabel: "Ventana",
        error: (msg) => `Error de monitoreo: ${msg}`,
        empty: "Sin datos conversacionales en esta ventana.",
        scope: (val) => `Alcance de agregación: ${val}`,
        totalMessages: (val) => `Messages totales: ${val}`,
        p95Latency: (val) => `Latencia p95: ${val}`,
        successRollback: "Rollback de persona realizado.",
      },
      credentials: {
        title: "API de Empresa",
        description: "Genere y regenere sus claves API B2B.",
        loading: "Cargando credenciales...",
        errorLoad: "No se pudieron cargar las credenciales.",
        accountTitle: (name) => `Cuenta: ${name}`,
        accountStatus: (status) => `Estado de cuenta: ${status}`,
        keyTitle: (prefix) => `Clave: ${prefix}***`,
        createdDate: (date) => `Creada el: ${date}`,
        errorGenerate: (msg) => `Error de generación de clave: ${msg}`,
        errorRotate: (msg) => `Error de regeneración de clave: ${msg}`,
        generateLabel: "Generar una clave API",
        rotateLabel: "Régénérer la clé active",
      },
      support: {
        title: "Soporte y Operaciones",
        description: "Consulte el expediente del usuario y gestione incidentes.",
        targetUserLabel: "Usuario objetivo",
        privacyRequests: (count) => `Solicitudes RGPD: ${count}`,
        noPrivacyRequests: "Sin solicitudes RGPD.",
        recentAuditTitle: "Auditoría reciente",
      },
      privacy: {
        title: "Privacidad et Datos",
        description: "Solicite una exportación de sus datos o la eliminación de su cuenta.",
        requestExport: "Solicitar exportación",
        requestDelete: "Eliminar mis datos",
        statusExport: (status) => `Estado de exportación: ${status}`,
        emptyExport: "Sin solicitudes de exportación por ahora.",
        errorExportStatus: (msg) => `Error de estado de exportación: ${msg}`,
        statusDelete: (status) => `Estado de eliminación: ${status}`,
        emptyDelete: "Sin solicitudes de eliminación por ahora.",
        errorDeleteStatus: (msg) => `Error de estado de eliminación: ${msg}`,
        errorExportRequest: (msg) => `Error de solicitud de exportación: ${msg}`,
        errorDeleteRequest: (msg) => `Error de solicitud de eliminación: ${msg}`,
      },
    },
  },

  pricing: {
    fr: {
      title: "Gestion des Tarifs",
      description: "Visualisation des plans tarifaires configurés dans le système.",
      loading: "Chargement des plans...",
      errorLoading: "Erreur lors du chargement des plans.",
      unknownError: "Erreur inconnue",
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
      description: "Visualization of pricing plans configured in the system.",
      loading: "Loading plans...",
      errorLoading: "Error loading plans.",
      unknownError: "Unknown error",
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
      description: "Visualización de los planes tarifarios configurados en le sistema.",
      loading: "Cargando planes...",
      errorLoading: "Error al cargar los planes.",
      unknownError: "Error desconocido",
      emptyState: "Ningún plan tarifario configurado.",
      tableLabel: "Planes tarifarios",
      colCode: "Código",
      colName: "Nombre",
      colPrice: "Precio mensual",
      colLimit: "Límite mensajes/día",
      colStatus: "Estado",
      statusActive: "Activo",
      statusInactive: "Inactif",
      upcomingTitle: "Próximas funcionalidades",
      upcomingModify: "Modificación de tarifas existentes",
      upcomingCreate: "Creación de nouveaux planes",
      upcomingActivate: "Activación/desactivación de planes",
      upcomingNote:
        "Estas funcionalidades requieren la implementación de une API admin dedicada (fuera del alcance de la story 16.7).",
    },
  } as Record<AstrologyLang, PricingTranslations>,
}

export function translateAdmin(lang: AstrologyLang = "fr"): AdminTranslation {
  return {
    page: adminTranslations.page[lang],
    sections: adminTranslations.sections[lang],
    monitoring: adminTranslations.monitoring[lang],
    personas: adminTranslations.personas[lang],
    reconciliation: adminTranslations.reconciliation[lang],
    b2b: adminTranslations.b2b[lang],
    pricing: adminTranslations.pricing[lang],
  }
}

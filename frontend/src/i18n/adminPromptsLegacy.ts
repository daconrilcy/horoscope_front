import type { AstrologyLang } from "./astrology"
import type { AppLocale } from "./types"
import type { AdminPromptVersion } from "../api/adminPrompts"

/** Textes de la route /admin/prompts/legacy (alignés FR / EN / ES). */
export type AdminPromptsLegacyStrings = {
  regionAriaLabel: string
  loadingHistory: string
  errorHistory: string
  kicker: string
  surfaceTitle: string
  surfaceIntro: string
  toolbarLabel: string
  useCaseSelectAria: string
  emptyVersions: string
  versionsHeading: string
  versionsHintActiveKnown: string
  versionsHintActiveUnknown: string
  badgeInProduction: string
  authorLine: (author: string, dateFormatted: string) => string
  restoreThisVersion: string
  alreadyActiveHint: string
  diffHeading: string
  diffLeadActiveKnown: string
  diffLeadActiveUnknown: string
  refVersionLabel: string
  refSelectAria: string
  diffGroupAria: string
  refColumnTitle: string
  rightColumnTitleProduction: string
  rightColumnTitlePeer: string
  contentComparedCaption: string
  metaVariantReference: string
  metaVariantProduction: string
  metaVariantPeer: string
  metaStatus: string
  metaModel: string
  metaAuthor: string
  metaCreated: string
  metaId: string
  statusPublished: string
  statusArchived: string
  statusDraft: string
  modalTitle: string
  modalPublishTarget: string
  modalReplaceActive: string
  modalNoActiveResolved: string
  modalEmphasis: string
  modalCancel: string
  modalConfirm: string
  modalConfirming: string
  successRestore: string
}

export const adminPromptsLegacyByLang: Record<AstrologyLang, AdminPromptsLegacyStrings> = {
  fr: {
    regionAriaLabel: "Investigation historique LLM hors catalogue",
    loadingHistory: "Chargement de l'historique legacy…",
    errorHistory: "Impossible de charger l'historique legacy.",
    kicker: "Hors catalogue canonique",
    surfaceTitle: "Investigation des versions historiques",
    surfaceIntro:
      "Ce périmètre est dédié à la lecture et à la comparaison des prompts enregistrés avant le modèle catalogue. Choisissez un cas d'usage, repérez la version active lorsqu'elle est connue de l'API, puis comparez le texte développeur à une autre version. Les restaurations sont regroupées et nécessitent une confirmation explicite.",
    toolbarLabel: "Cas d'usage à consulter",
    useCaseSelectAria: "Cas d'usage historique",
    emptyVersions: "Aucune version enregistrée pour ce cas d'usage.",
    versionsHeading: "Versions enregistrées",
    versionsHintActiveKnown:
      "La version marquée « en production » est celle comparée à droite dans le diff ci-dessous.",
    versionsHintActiveUnknown:
      "Aucune version « active » résolue par l'API pour ce cas d'usage : le diff compare deux versions choisies sans statut de production garanti.",
    badgeInProduction: "En production",
    authorLine: (author, dateFormatted) => `Auteur ${author} · ${dateFormatted}`,
    restoreThisVersion: "Restaurer cette version",
    alreadyActiveHint: "Déjà actif — comparez à gauche",
    diffHeading: "Comparaison du prompt développeur",
    diffLeadActiveKnown:
      "Diff ligne à ligne : à gauche la version de référence choisie, à droite la version actuellement en production pour ce cas d'usage. Les métadonnées restent visibles sans ouvrir le texte intégral.",
    diffLeadActiveUnknown:
      "Diff ligne à ligne entre deux versions de l'historique : l'API n'a pas renvoyé d'identifiant de version active reconnu dans cette liste. La colonne de droite est une autre version de contraste, pas une « production » attestée.",
    refVersionLabel: "Version de référence (colonne gauche)",
    refSelectAria: "Version de référence pour la comparaison legacy",
    diffGroupAria: "Diff prompt développeur legacy",
    refColumnTitle: "Colonne gauche — version de référence",
    rightColumnTitleProduction: "Colonne droite — version en production",
    rightColumnTitlePeer: "Colonne droite — autre version (actif non résolu)",
    contentComparedCaption: "Contenu comparé (ligne à ligne)",
    metaVariantReference: "Référence (gauche)",
    metaVariantProduction: "Version en production (droite)",
    metaVariantPeer: "Autre version (droite)",
    metaStatus: "Statut",
    metaModel: "Modèle",
    metaAuthor: "Auteur",
    metaCreated: "Création",
    metaId: "Identifiant",
    statusPublished: "Publié",
    statusArchived: "Archivé",
    statusDraft: "Brouillon",
    modalTitle: "Confirmer la restauration de version",
    modalPublishTarget:
      "Vous allez publier la version {{code}} ({{status}}) comme prompt actif pour le cas d'usage {{name}} ({{key}}).",
    modalReplaceActive:
      "La version actuellement en production {{code}} ({{status}}) sera remplacée pour les prochains appels qui résolvent ce cas d'usage.",
    modalNoActiveResolved:
      "Aucune version active résolue dans la liste : la cible ci-dessus sera publiée pour ce cas d'usage.",
    modalEmphasis:
      "Cette action est traçable côté serveur et affecte le prompt/persona legacy, pas le catalogue canonique.",
    modalCancel: "Annuler",
    modalConfirm: "Confirmer la restauration",
    modalConfirming: "Restauration en cours…",
    successRestore: "Restauration effectuée vers {{short}}…",
  },
  en: {
    regionAriaLabel: "Off-catalog LLM history investigation",
    loadingHistory: "Loading legacy history…",
    errorHistory: "Could not load legacy history.",
    kicker: "Off canonical catalog",
    surfaceTitle: "Historical versions investigation",
    surfaceIntro:
      "This area is for reading and comparing prompts recorded before the catalog model. Pick a use case, identify the active version when the API provides it, then compare developer prompt text to another version. Restore actions are grouped and require explicit confirmation.",
    toolbarLabel: "Use case to inspect",
    useCaseSelectAria: "Historical use case",
    emptyVersions: "No versions recorded for this use case.",
    versionsHeading: "Recorded versions",
    versionsHintActiveKnown:
      "The row marked “in production” is the one compared on the right in the diff below.",
    versionsHintActiveUnknown:
      "No “active” version resolved by the API for this use case: the diff compares two chosen versions without a guaranteed production state.",
    badgeInProduction: "In production",
    authorLine: (author, dateFormatted) => `Author ${author} · ${dateFormatted}`,
    restoreThisVersion: "Restore this version",
    alreadyActiveHint: "Already active — compare on the left",
    diffHeading: "Developer prompt comparison",
    diffLeadActiveKnown:
      "Line-by-line diff: reference on the left, currently in-production version for this use case on the right. Metadata stays visible without opening the full text.",
    diffLeadActiveUnknown:
      "Line-by-line diff between two history versions: the API did not return an active version id that matches this list. The right column is another contrast version, not an asserted “production” prompt.",
    refVersionLabel: "Reference version (left column)",
    refSelectAria: "Legacy comparison reference version",
    diffGroupAria: "Legacy developer prompt diff",
    refColumnTitle: "Left column — reference version",
    rightColumnTitleProduction: "Right column — in-production version",
    rightColumnTitlePeer: "Right column — other version (active unresolved)",
    contentComparedCaption: "Compared content (line by line)",
    metaVariantReference: "Reference (left)",
    metaVariantProduction: "In production (right)",
    metaVariantPeer: "Other version (right)",
    metaStatus: "Status",
    metaModel: "Model",
    metaAuthor: "Author",
    metaCreated: "Created",
    metaId: "Id",
    statusPublished: "Published",
    statusArchived: "Archived",
    statusDraft: "Draft",
    modalTitle: "Confirm version restore",
    modalPublishTarget:
      "You will publish version {{code}} ({{status}}) as the active prompt for use case {{name}} ({{key}}).",
    modalReplaceActive:
      "The version currently in production {{code}} ({{status}}) will be replaced for subsequent calls that resolve this use case.",
    modalNoActiveResolved:
      "No active version resolved in this list: the target above will be published for this use case.",
    modalEmphasis:
      "This action is traceable server-side and affects the legacy prompt/persona, not the canonical catalog.",
    modalCancel: "Cancel",
    modalConfirm: "Confirm restore",
    modalConfirming: "Restoring…",
    successRestore: "Restore completed toward {{short}}…",
  },
  es: {
    regionAriaLabel: "Investigación de historial LLM fuera del catálogo",
    loadingHistory: "Cargando historial legacy…",
    errorHistory: "No se pudo cargar el historial legacy.",
    kicker: "Fuera del catálogo canónico",
    surfaceTitle: "Investigación de versiones históricas",
    surfaceIntro:
      "Este ámbito sirve para leer y comparar prompts registrados antes del modelo de catálogo. Elija un caso de uso, identifique la versión activa cuando la API la proporcione y compare el texto del desarrollador con otra versión. Las restauraciones están agrupadas y requieren confirmación explícita.",
    toolbarLabel: "Caso de uso a consultar",
    useCaseSelectAria: "Caso de uso histórico",
    emptyVersions: "Ninguna versión registrada para este caso de uso.",
    versionsHeading: "Versiones registradas",
    versionsHintActiveKnown:
      "La versión marcada « en producción » es la que se compara a la derecha en el diff.",
    versionsHintActiveUnknown:
      "Ninguna versión « activa » resuelta por la API para este caso de uso: el diff compara dos versiones elegidas sin estado de producción garantizado.",
    badgeInProduction: "En producción",
    authorLine: (author, dateFormatted) => `Autor ${author} · ${dateFormatted}`,
    restoreThisVersion: "Restaurar esta versión",
    alreadyActiveHint: "Ya activo — compare a la izquierda",
    diffHeading: "Comparación del prompt de desarrollador",
    diffLeadActiveKnown:
      "Diff línea a línea: a la izquierda la versión de referencia elegida, a la derecha la versión actualmente en producción para este caso de uso. Los metadatos permanecen visibles sin abrir el texto completo.",
    diffLeadActiveUnknown:
      "Diff línea a línea entre dos versiones del historial: la API no devolvió un id de versión activa reconocido en esta lista. La columna derecha es otra versión de contraste, no una producción certificada.",
    refVersionLabel: "Versión de referencia (columna izquierda)",
    refSelectAria: "Versión de referencia para la comparación legacy",
    diffGroupAria: "Diff de prompt desarrollador legacy",
    refColumnTitle: "Columna izquierda — versión de referencia",
    rightColumnTitleProduction: "Columna derecha — versión en producción",
    rightColumnTitlePeer: "Columna derecha — otra versión (activo no resuelto)",
    contentComparedCaption: "Contenido comparado (línea a línea)",
    metaVariantReference: "Referencia (izquierda)",
    metaVariantProduction: "Versión en producción (derecha)",
    metaVariantPeer: "Otra versión (derecha)",
    metaStatus: "Estado",
    metaModel: "Modelo",
    metaAuthor: "Autor",
    metaCreated: "Creación",
    metaId: "Identificador",
    statusPublished: "Publicado",
    statusArchived: "Archivado",
    statusDraft: "Borrador",
    modalTitle: "Confirmar restauración de versión",
    modalPublishTarget:
      "Publicará la versión {{code}} ({{status}}) como prompt activo para el caso de uso {{name}} ({{key}}).",
    modalReplaceActive:
      "La versión actualmente en producción {{code}} ({{status}}) será reemplazada para las próximas llamadas que resuelvan este caso de uso.",
    modalNoActiveResolved:
      "Ninguna versión activa resuelta en esta lista: el objetivo anterior se publicará para este caso de uso.",
    modalEmphasis:
      "Esta acción es trazable en el servidor y afecta el prompt/persona legacy, no el catálogo canónico.",
    modalCancel: "Cancelar",
    modalConfirm: "Confirmar restauración",
    modalConfirming: "Restauración en curso…",
    successRestore: "Restauración efectuada hacia {{short}}…",
  },
}

export function interpolateLegacyTemplate(template: string, vars: Record<string, string>): string {
  return template.replace(/\{\{(\w+)\}\}/g, (_, key: string) => vars[key] ?? "")
}

export function formatLegacyPromptTimestamp(iso: string, lang: AppLocale): string {
  try {
    const tag = lang === "fr" ? "fr-FR" : lang === "es" ? "es-ES" : "en-GB"
    return new Date(iso).toLocaleString(tag, { dateStyle: "short", timeStyle: "short" })
  } catch {
    return iso
  }
}

export function legacyPromptStatusLabel(
  status: AdminPromptVersion["status"],
  L: AdminPromptsLegacyStrings,
): string {
  switch (status) {
    case "published":
      return L.statusPublished
    case "archived":
      return L.statusArchived
    case "draft":
      return L.statusDraft
    default:
      return status
  }
}

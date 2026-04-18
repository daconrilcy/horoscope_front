import type { AstrologyLang } from "./astrology"
import type { AdminConsumptionRow, AdminConsumptionView, AdminInspectionMode } from "@api"
import type { AdminResolvedPlaceholder } from "@api"

function mapOrRaw(map: Readonly<Record<string, string>>, raw: string): string {
  return map[raw] ?? raw
}

const SOURCE_OF_TRUTH: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    active_snapshot: "Snapshot actif (catalogue)",
    live_table_fallback: "Repli table live",
    "n/a": "Non renseigné",
  },
  en: {
    active_snapshot: "Active snapshot (catalog)",
    live_table_fallback: "Live table fallback",
    "n/a": "Not available",
  },
  es: {
    active_snapshot: "Snapshot activo (catálogo)",
    live_table_fallback: "Respaldo tabla en vivo",
    "n/a": "No disponible",
  },
}

const RELEASE_HEALTH: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    monitoring: "Surveillance",
    activated: "Activé",
    degraded: "Dégradé",
    rollback_recommended: "Rollback recommandé",
    rolled_back: "Rollback effectué",
    "n/a": "Non renseigné",
  },
  en: {
    monitoring: "Monitoring",
    activated: "Activated",
    degraded: "Degraded",
    rollback_recommended: "Rollback recommended",
    rolled_back: "Rolled back",
    "n/a": "N/A",
  },
  es: {
    monitoring: "Monitorización",
    activated: "Activado",
    degraded: "Degradado",
    rollback_recommended: "Rollback recomendado",
    rolled_back: "Rollback aplicado",
    "n/a": "N/D",
  },
}

const CATALOG_VISIBILITY: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    visible: "Visible",
    orphaned: "Orpheline",
    stale: "Périmée",
    hidden: "Masquée",
  },
  en: {
    visible: "Visible",
    orphaned: "Orphaned",
    stale: "Stale",
    hidden: "Hidden",
  },
  es: {
    visible: "Visible",
    orphaned: "Huérfana",
    stale: "Obsoleta",
    hidden: "Oculta",
  },
}

const RUNTIME_SIGNAL: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    fresh: "À jour",
    stale: "Périmé",
    "n/a": "Non renseigné",
  },
  en: {
    fresh: "Fresh",
    stale: "Stale",
    "n/a": "N/A",
  },
  es: {
    fresh: "Actualizado",
    stale: "Obsoleto",
    "n/a": "N/D",
  },
}

const ASSEMBLY_STATUS: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    published: "Publié",
    draft: "Brouillon",
    archived: "Archivé",
  },
  en: {
    published: "Published",
    draft: "Draft",
    archived: "Archived",
  },
  es: {
    published: "Publicado",
    draft: "Borrador",
    archived: "Archivado",
  },
}

/** Messages d'erreur API résolue (codes métier) — alignés sur AdminPromptsApiError.code */
const RESOLVED_ASSEMBLY_ERRORS: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    sample_payload_inactive:
      "Ce sample payload est inactif. Choisissez un autre payload ou réactivez-le dans le catalogue.",
    sample_payload_not_found: "Sample payload introuvable.",
    sample_payload_target_mismatch:
      "Ce sample payload ne correspond pas à cette entrée (feature ou locale différente).",
    sample_payload_runtime_preview_only:
      "Un sample payload ne peut être utilisé qu'en mode prévisualisation runtime.",
    invalid_sample_payload: "Le sample payload est invalide (JSON attendu : un objet).",
    manifest_entry_not_found: "Entrée de catalogue introuvable.",
    invalid_manifest_entry_id: "Identifiant d'entrée manifeste invalide.",
    runtime_preview_incomplete_for_execution:
      "La prévisualisation runtime est incomplète : corrigez les placeholders bloquants avant d'exécuter le LLM.",
    admin_manual_execution_failed:
      "L'exécution manuelle LLM a échoué. Consultez le message détaillé ou les journaux.",
  },
  en: {
    sample_payload_inactive:
      "This sample payload is inactive. Choose another payload or re-enable it in the catalog.",
    sample_payload_not_found: "Sample payload not found.",
    sample_payload_target_mismatch:
      "This sample payload does not match this entry (different feature or locale).",
    sample_payload_runtime_preview_only: "A sample payload can only be used in runtime preview mode.",
    invalid_sample_payload: "The sample payload is invalid (JSON expected: an object).",
    manifest_entry_not_found: "Catalog entry not found.",
    invalid_manifest_entry_id: "Invalid manifest entry identifier.",
    runtime_preview_incomplete_for_execution:
      "Runtime preview is incomplete: fix blocking placeholders before running the LLM.",
    admin_manual_execution_failed: "Manual LLM execution failed. See the detailed message or logs.",
  },
  es: {
    sample_payload_inactive:
      "Este sample payload está inactivo. Elija otro o reactívelo en el catálogo.",
    sample_payload_not_found: "Sample payload no encontrado.",
    sample_payload_target_mismatch:
      "Este sample payload no coincide con esta entrada (feature o locale distinta).",
    sample_payload_runtime_preview_only: "Un sample payload solo puede usarse en modo previsualización runtime.",
    invalid_sample_payload: "El sample payload no es válido (se esperaba JSON: un objeto).",
    manifest_entry_not_found: "Entrada de catálogo no encontrada.",
    invalid_manifest_entry_id: "Identificador de entrada de manifiesto no válido.",
    runtime_preview_incomplete_for_execution:
      "La previsualización runtime está incompleta: corrija los placeholders bloqueantes antes de ejecutar el LLM.",
    admin_manual_execution_failed:
      "La ejecución manual del LLM falló. Consulte el mensaje detallado o los registros.",
  },
}

const MANUAL_EXEC_FAILURE_LEADS: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    runtime_preview_incomplete: "Prévisualisation runtime incomplète (placeholders bloquants)",
    input_validation: "Validation des entrées (schéma ou contexte)",
    gateway_config: "Configuration gateway ou profil d'exécution",
    output_validation: "Validation de sortie (schéma)",
    prompt_render: "Erreur de rendu du prompt (gateway)",
    provider_error: "Erreur fournisseur LLM",
    unknown_use_case: "Use case ou résolution catalogue inconnue",
    unexpected: "Erreur interne inattendue",
  },
  en: {
    runtime_preview_incomplete: "Incomplete runtime preview (blocking placeholders)",
    input_validation: "Input validation (schema or context)",
    gateway_config: "Gateway or execution profile configuration",
    output_validation: "Output validation (schema)",
    prompt_render: "Prompt render error (gateway)",
    provider_error: "LLM provider error",
    unknown_use_case: "Unknown use case or catalog resolution",
    unexpected: "Unexpected internal error",
  },
  es: {
    runtime_preview_incomplete: "Previsualización runtime incompleta (placeholders bloqueantes)",
    input_validation: "Validación de entradas (esquema o contexto)",
    gateway_config: "Configuración gateway o perfil de ejecución",
    output_validation: "Validación de salida (esquema)",
    prompt_render: "Error de render del prompt (gateway)",
    provider_error: "Error del proveedor LLM",
    unknown_use_case: "Caso de uso o resolución de catálogo desconocida",
    unexpected: "Error interno inesperado",
  },
}

const RENDER_ERROR_LEADS: Record<
  AstrologyLang,
  { staticIncomplete: string; live: string; default: string }
> = {
  fr: {
    staticIncomplete:
      "Prévisualisation partielle : certaines substitutions nécessitent des données runtime. ",
    live: "Erreur détectée pendant l'inspection live. ",
    default: "Erreur de rendu détectée dans la prévisualisation. ",
  },
  en: {
    staticIncomplete: "Partial preview: some substitutions require runtime data. ",
    live: "Error detected during live inspection. ",
    default: "Render error detected in the preview. ",
  },
  es: {
    staticIncomplete: "Vista previa parcial: algunas sustituciones requieren datos runtime. ",
    live: "Error detectado durante la inspección en vivo. ",
    default: "Error de render detectado en la vista previa. ",
  },
}

type ReleaseDiffCategoryLabels = {
  changed: string
  added: string
  removed: string
  stable: string
  empty: string
  apiUnknown: (raw: string) => string
}

const RELEASE_DIFF_CATEGORY: Record<AstrologyLang, ReleaseDiffCategoryLabels> = {
  fr: {
    changed: "Écart sur cette fiche",
    added: "Ajout",
    removed: "Retrait",
    stable: "Sans écart",
    empty: "Catégorie non renseignée",
    apiUnknown: (raw) => `Catégorie (API) : ${raw}`,
  },
  en: {
    changed: "Diff on this entry",
    added: "Added",
    removed: "Removed",
    stable: "No diff",
    empty: "Category not set",
    apiUnknown: (raw) => `API category: ${raw}`,
  },
  es: {
    changed: "Cambio en esta ficha",
    added: "Añadido",
    removed: "Retirado",
    stable: "Sin cambio",
    empty: "Categoría no indicada",
    apiUnknown: (raw) => `Categoría (API): ${raw}`,
  },
}

const RELEASE_EVENT_TYPE: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    created: "Création",
    validated: "Validation",
    activated: "Activation",
    monitoring: "Surveillance",
    degraded: "Dégradation",
    rollback_recommended: "Rollback recommandé",
    rolled_back: "Rollback effectué",
    backend_unmapped: "Événement backend non mappé",
  },
  en: {
    created: "Created",
    validated: "Validated",
    activated: "Activated",
    monitoring: "Monitoring",
    degraded: "Degraded",
    rollback_recommended: "Rollback recommended",
    rolled_back: "Rolled back",
    backend_unmapped: "Backend unmapped event",
  },
  es: {
    created: "Creación",
    validated: "Validación",
    activated: "Activación",
    monitoring: "Monitorización",
    degraded: "Degradación",
    rollback_recommended: "Rollback recomendado",
    rolled_back: "Rollback aplicado",
    backend_unmapped: "Evento backend no mapeado",
  },
}

const RELEASE_CURRENT_STATUS: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    active: "Actif",
    archived: "Archivé",
    validated: "Validé",
    monitoring: "Surveillance",
    degraded: "Dégradé",
    rollback_recommended: "Rollback recommandé",
    rolled_back: "Rollback effectué",
  },
  en: {
    active: "Active",
    archived: "Archived",
    validated: "Validated",
    monitoring: "Monitoring",
    degraded: "Degraded",
    rollback_recommended: "Rollback recommended",
    rolled_back: "Rolled back",
  },
  es: {
    active: "Activo",
    archived: "Archivado",
    validated: "Validado",
    monitoring: "Monitorización",
    degraded: "Degradado",
    rollback_recommended: "Rollback recomendado",
    rolled_back: "Rollback aplicado",
  },
}

const RELEASE_PROOF_TYPE: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    qualification: "Qualification",
    golden: "Jeu golden",
    smoke: "Test smoke",
    readiness: "Validation readiness",
  },
  en: {
    qualification: "Qualification",
    golden: "Golden",
    smoke: "Smoke test",
    readiness: "Readiness",
  },
  es: {
    qualification: "Calificación",
    golden: "Golden",
    smoke: "Prueba smoke",
    readiness: "Readiness",
  },
}

const RELEASE_PROOF_VERDICT: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    go: "Go",
    pass: "Succès",
    valid: "Valide",
    uncorrelated: "Non corrélé",
  },
  en: {
    go: "Go",
    pass: "Pass",
    valid: "Valid",
    uncorrelated: "Uncorrelated",
  },
  es: {
    go: "Go",
    pass: "Correcto",
    valid: "Válido",
    uncorrelated: "No correlacionado",
  },
}

const RELEASE_PROOF_STATUS: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    present: "Présente",
    missing: "Manquante",
  },
  en: {
    present: "Present",
    missing: "Missing",
  },
  es: {
    present: "Presente",
    missing: "Faltante",
  },
}

const MANUAL_LLM_MODAL: Record<
  AstrologyLang,
  {
    title: string
    introBeforeSample: string
    betweenSampleAndManifest: string
    afterManifest: string
    modePrefix: string
    modeTraced: string
    cancel: string
    confirm: string
    executing: string
  }
> = {
  fr: {
    title: "Confirmer l'exécution LLM réelle",
    introBeforeSample:
      "Vous allez lancer un appel fournisseur réel (hors trafic utilisateur nominal), avec le sample ",
    betweenSampleAndManifest: " sur l'entrée ",
    afterManifest: ".",
    modePrefix: "Mode actif : ",
    modeTraced: ". Cette action est tracée côté serveur.",
    cancel: "Annuler",
    confirm: "Confirmer l'exécution",
    executing: "Exécution en cours...",
  },
  en: {
    title: "Confirm real LLM execution",
    introBeforeSample:
      "You are about to trigger a real provider call (off nominal user traffic), using sample ",
    betweenSampleAndManifest: " for manifest entry ",
    afterManifest: ".",
    modePrefix: "Active mode: ",
    modeTraced: ". This action is traced on the server.",
    cancel: "Cancel",
    confirm: "Confirm execution",
    executing: "Executing…",
  },
  es: {
    title: "Confirmar ejecución real del LLM",
    introBeforeSample:
      "Va a lanzar una llamada real al proveedor (fuera del tráfico nominal), con el sample ",
    betweenSampleAndManifest: " en la entrada ",
    afterManifest: ".",
    modePrefix: "Modo activo: ",
    modeTraced: ". Esta acción queda trazada en el servidor.",
    cancel: "Cancelar",
    confirm: "Confirmar ejecución",
    executing: "Ejecutando…",
  },
}

const CONTEXT_COMPENSATION: Record<AstrologyLang, Readonly<Record<string, string>>> = {
  fr: {
    none: "Aucune compensation",
    not_needed: "Non nécessaire",
    applied: "Compensation appliquée",
    pending: "En attente",
  },
  en: {
    none: "None",
    not_needed: "Not needed",
    applied: "Applied",
    pending: "Pending",
  },
  es: {
    none: "Ninguna",
    not_needed: "No necesaria",
    applied: "Aplicada",
    pending: "Pendiente",
  },
}

export interface AdminPromptsCatalogStrings {
  subNavAriaLabel: string
  catalogRegionAria: string
  filterSearchLabel: string
  filterSearchPlaceholder: string
  filterFeatureLabel: string
  filterSubfeatureLabel: string
  filterPlanLabel: string
  filterLocaleLabel: string
  filterProviderLabel: string
  filterSortLabel: string
  filterSortOrderLabel: string
  sortOrderAsc: string
  sortOrderDesc: string
  resetCatalogFilters: string
  sortAriaCatalog: string
  sortOrderAriaCatalog: string
  activeFiltersAria: string
  sortOptionFeature: string
  sortOptionSubfeature: string
  sortOptionPlan: string
  sortOptionLocale: string
  sortOptionManifestEntry: string
  sortOptionProvider: string
  sortOptionSourceOfTruth: string
  sortOptionAssemblyStatus: string
  sortOptionReleaseHealth: string
  sortOptionCatalogVisibility: string
  filterAllFeminine: string
  filterAllMasculine: string
  filterSourceOfTruth: string
  filterAssemblyStatus: string
  filterReleaseHealth: string
  filterCatalogVisibility: string
  activeFilterSearch: (value: string) => string
  activeFilterFeature: (value: string) => string
  activeFilterSubfeature: (value: string) => string
  activeFilterPlan: (value: string) => string
  activeFilterLocale: (value: string) => string
  activeFilterProvider: (value: string) => string
  activeFilterSourceOfTruth: (value: string) => string
  activeFilterAssembly: (value: string) => string
  activeFilterReleaseHealth: (value: string) => string
  activeFilterVisibility: (value: string) => string
  noActiveFilters: string
  advancedFiltersToggle: string
  catalogLoading: string
  catalogError: string
  tableColTuple: string
  tableColSnapshot: string
  tableColProviderModel: string
  tableColHealth: string
  tableColAction: string
  healthLine: (release: string, runtime: string, visibility: string) => string
  healthSignalPrefix: string
  notAvailable: string
  openDetail: string
  catalogFooterLines: (total: number, minutes: string) => string
  catalogPrev: string
  catalogNext: string
  catalogPage: (n: number) => string
  detailPanelAria: string
  detailSummaryTitle: string
  detailManifestEntryDt: string
  detailAssemblyDt: string
  detailExecutionProfileDt: string
  detailOutputContractDt: string
  detailCatalogVisibilityDt: string
  detailOffPageFromResolved: string
  detailOffPageIdOnly: string
  resolvedPanelAria: string
  inspectionBannerAria: string
  inspectionBannerKicker: string
  inspectionSectionAria: string
  inspectionHeading: string
  inspectionModeFieldCaption: string
  inspectionModeSelectAria: string
  executionStateSectionAria: string
  resolvedStateLead: (modeShort: string, sourceLabel: string, snapshot: string) => string
  sourceWord: string
  actionsSectionAria: string
  actionsTitle: string
  actionsRiskNote: string
  samplePayloadFieldCaption: string
  samplePayloadSelectAria: string
  noSamplePayloadOption: string
  executeWithLlm: string
  executeWithLlmPending: string
  promptsZoneAria: string
  promptsZoneTitle: string
  promptsSourceLine: (sourceLabel: string, snapshot: string) => string
  disclosureAssembled: string
  disclosurePostInjectors: string
  disclosureRendered: string
  disclosureSystemPolicy: string
  disclosureDeveloper: string
  disclosurePersona: string
  disclosureExecParamsPreview: string
  disclosureRuntimeResolved: string
  disclosurePromptSent: string
  disclosureStructuredOut: string
  disclosureRawOut: string
  placeholdersZoneAria: string
  placeholdersZoneTitle: string
  placeholdersIntro: string
  placeholdersEmpty: string
  llmReturnZoneAria: string
  llmReturnZoneTitle: string
  contextQualityLine: (status: string) => string
  llmOutputLead: string
  validationStatusDt: string
  durationDt: string
  pathDt: string
  providerModelDt: string
  tokensDt: string
  gatewayRequestDt: string
  graphZoneAria: string
  graphZoneTitle: string
  graphIntro: string
  compositionSourcesSummary: string
  execProfileGridLabel: string
  reasoningGridLabel: string
  verbosityGridLabel: string
  detailEmptySelectRow: string
  resolvedLoading: string
  resolvedLoadingSamples: string
  runtimePreviewIdle: string
  manualExecIncomplete: string
  manualExecFailed: string
  manualExecSuccessNoData: string
  manualExecHintReady: string
  manualExecHintNeedSample: string
  manualExecPassToRuntime: string
  modeBadge: (short: string) => string
  releaseRegionAria: string
  releaseLoadingTimeline: string
  releaseErrorTimeline: string
  releaseEmptySnapshots: string
  releaseKicker: string
  releaseSurfaceTitle: string
  releaseSurfaceIntro: string
  releaseTimelineHeading: string
  releaseTimelineHint: string
  releaseEventLine: (eventType: string, when: string, count: string) => string
  releaseCurrentLine: (status: string, transitions: number) => string
  releaseRollbackLine: (from: string, to: string) => string
  releaseReasonPrefix: string
  releaseProofsLead: string
  releaseCompareHeading: string
  releaseCompareHint: string
  releaseSnapshotSourceLabel: string
  releaseSnapshotTargetLabel: string
  releaseDiffLoading: string
  releaseDiffError: string
  releaseDiffTitle: string
  releaseCompareBannerAria: string
  releaseCompareRoleSource: string
  releaseCompareRoleTarget: string
  releaseDiffTableHeading: string
  releaseDiffTableLead: string
  releaseDiffColManifest: string
  releaseDiffColScope: string
  releaseDiffColAssembly: string
  releaseDiffColExec: string
  releaseDiffColContract: string
  releaseDiffColCatalog: string
  releaseDiffChanged: string
  releaseDiffUnchanged: string
  releaseOpenCatalogAria: (manifestId: string) => string
  releaseOpenCatalogTitle: string
  manifestEntriesCount: (n: number) => string
  labelReleaseEventType: (raw: string) => string
  labelReleaseCurrentStatus: (raw: string) => string
  labelReleaseProofType: (raw: string) => string
  labelReleaseProofOutcome: (verdict: string | null, status: string) => string
  catalogRowAria: (tupleHint: string, selected: boolean) => string
  labelSourceOfTruthStatus: (raw: string) => string
  labelReleaseHealthStatus: (raw: string) => string
  labelCatalogVisibilityStatus: (raw: string) => string
  labelRuntimeSignalStatus: (raw: string) => string
  labelAssemblyStatus: (raw: string) => string
  labelContextCompensation: (raw: string) => string
  inspectionModeOptions: { value: AdminInspectionMode; label: string }[]
  inspectionModeShortLabel: (mode: AdminInspectionMode) => string
  inspectionModeFullLabel: (mode: AdminInspectionMode) => string
  inspectionModeHelpText: (mode: AdminInspectionMode) => string
  placeholderStatusLabel: (status: AdminResolvedPlaceholder["status"]) => string
  placeholderRedactionLevelLabel: (item: AdminResolvedPlaceholder) => string
  placeholderSourceLabel: (source: string | null) => string
  placeholderPreviewValue: (item: AdminResolvedPlaceholder) => string
  placeholderUnknownClassification: string
  placeholderUnknownReason: string
  consumptionUnknownFeatureCell: (
    feature: string | null | undefined,
    subfeature: string | null | undefined,
  ) => string
  consumptionUnknownProvider: string
  formatConsumptionAxisLabel: (view: AdminConsumptionView, row: AdminConsumptionRow) => string
  /** Modale confirmation exécution LLM manuelle (catalogue résolu) */
  manualLlmModalTitle: string
  manualLlmModalIntroBeforeSample: string
  manualLlmModalBetweenSampleAndManifest: string
  manualLlmModalAfterManifest: string
  manualLlmModalModePrefix: string
  manualLlmModalModeTraced: string
  manualLlmModalCancel: string
  manualLlmModalConfirm: string
  manualLlmModalExecuting: string
  resolvedErrorLoadDetailGeneric: string
  resolvedErrorSecondaryCodeHttp: (code: string, status: number) => string
  renderErrorLeadLine: (
    inspectionMode: AdminInspectionMode,
    renderErrorKind: string | null | undefined,
  ) => string
  releaseDiffCategoryLabel: (category: string) => string
  resolvedAssemblyErrorMessage: (code: string) => string | undefined
  manualExecutionFailureLeadMessage: (kind: string) => string | undefined
  /** Erreur mutation sans détail API (repli court) */
  manualExecErrorGeneric: string
}

function buildStrings(lang: AstrologyLang) {
  const L =
    lang === "en"
      ? {
          subNavAriaLabel: "Prompt administration sections",
          catalogRegionAria: "Canonical LLM prompt catalog",
          filterSearchLabel: "Search",
          filterSearchPlaceholder: "Canonical tuple or manifest_entry_id",
          filterFeatureLabel: "Feature",
          filterSubfeatureLabel: "Subfeature",
          filterPlanLabel: "Plan",
          filterLocaleLabel: "Locale",
          filterProviderLabel: "Provider",
          filterSortLabel: "Sort",
          filterSortOrderLabel: "Order",
          sortOrderAsc: "Ascending",
          sortOrderDesc: "Descending",
          resetCatalogFilters: "Reset filters",
          sortAriaCatalog: "Catalog sort field",
          sortOrderAriaCatalog: "Catalog sort order",
          activeFiltersAria: "Active filters",
          sortOptionFeature: "Feature",
          sortOptionSubfeature: "Subfeature",
          sortOptionPlan: "Plan",
          sortOptionLocale: "Locale",
          sortOptionManifestEntry: "Manifest entry",
          sortOptionProvider: "Provider",
          sortOptionSourceOfTruth: "Source of truth",
          sortOptionAssemblyStatus: "Assembly status",
          sortOptionReleaseHealth: "Release health",
          sortOptionCatalogVisibility: "Catalog visibility",
          filterAllFeminine: "All",
          filterAllMasculine: "All",
          filterSourceOfTruth: "Source of truth",
          filterAssemblyStatus: "Assembly status",
          filterReleaseHealth: "Release health",
          filterCatalogVisibility: "Catalog visibility",
          noActiveFilters: "No active filters",
          advancedFiltersToggle: "Advanced filters",
          catalogLoading: "Loading canonical catalog…",
          catalogError: "Could not load the canonical catalog.",
          tableColTuple: "Canonical tuple",
          tableColSnapshot: "Active snapshot",
          tableColProviderModel: "Provider / model",
          tableColHealth: "Health",
          tableColAction: "Action",
          healthSignalPrefix: "signal",
          notAvailable: "n/a",
          openDetail: "Open detail",
          catalogPrev: "Previous",
          catalogNext: "Next",
          detailPanelAria: "Catalog entry detail",
          detailSummaryTitle: "Summary",
          detailManifestEntryDt: "Manifest entry",
          detailAssemblyDt: "Assembly",
          detailExecutionProfileDt: "Execution profile",
          detailOutputContractDt: "Output contract",
          detailCatalogVisibilityDt: "Catalog visibility",
          detailOffPageFromResolved:
            "Entry outside the current table page — summary above comes from resolved detail.",
          detailOffPageIdOnly: "Entry outside current page — identifier",
          resolvedPanelAria: "Resolved assembly detail",
          inspectionBannerAria: "Active inspection mode for this detail",
          inspectionBannerKicker: "Inspection mode",
          inspectionSectionAria: "Inspection mode",
          inspectionHeading: "Inspection mode",
          inspectionModeFieldCaption: "Inspection mode",
          inspectionModeSelectAria: "Detail inspection mode",
          executionStateSectionAria: "Execution state",
          sourceWord: "source",
          actionsSectionAria: "Actions",
          actionsTitle: "Actions",
          actionsRiskNote:
            "Risk: real provider execution off nominal traffic — server traced, confirmation required before send.",
          samplePayloadFieldCaption: "Sample payload (execution precondition)",
          samplePayloadSelectAria: "Runtime sample payload selector",
          noSamplePayloadOption: "No sample payload",
          executeWithLlm: "Execute with LLM",
          executeWithLlmPending: "LLM execution…",
          promptsZoneAria: "Prompts",
          promptsZoneTitle: "Prompts",
          placeholdersZoneAria: "Placeholders",
          placeholdersZoneTitle: "Placeholders",
          placeholdersIntro:
            "Resolved/partial placeholders for operator reading (no raw JSON parsing). Sample payload actions are grouped under Actions.",
          placeholdersEmpty: "No placeholders for this target.",
          llmReturnZoneAria: "LLM return",
          llmReturnZoneTitle: "LLM return",
          llmOutputLead: "Live execution output",
          validationStatusDt: "Validation status",
          durationDt: "Duration",
          pathDt: "Path",
          providerModelDt: "Provider / model",
          tokensDt: "Tokens (in / out)",
          gatewayRequestDt: "Gateway request",
          graphZoneAria: "Logic graph",
          graphZoneTitle: "Logic graph",
          graphIntro:
            "Inspectable chain: interactive schema (zoom/pan) with text fallback. Composition sources, pipeline, provider messages and runtime data.",
          compositionSourcesSummary: "Composition sources (full text)",
          execProfileGridLabel: "Execution profile",
          reasoningGridLabel: "Reasoning",
          verbosityGridLabel: "Verbosity",
          detailEmptySelectRow: "Select a catalog row to show resolved detail.",
          resolvedLoading: "Loading detail…",
          resolvedLoadingSamples: "Loading sample payloads…",
          runtimePreviewIdle: 'Select "Runtime preview" to enable sample payloads and LLM execution from this panel.',
          manualExecIncomplete:
            "Incomplete runtime preview: fix blocking placeholders or complete the sample before executing.",
          manualExecFailed: "Execution failed — see the Actions panel.",
          manualExecSuccessNoData:
            "Execution reported success but returned no data. Retry or check API logs.",
          manualExecHintReady:
            'Use Actions ("Execute with LLM") to show the full return (metadata, effective prompt, outputs).',
          manualExecHintNeedSample: "Select a valid sample payload in Actions, then execute to show operator output.",
          manualExecPassToRuntime: "Switch to runtime preview to execute the provider and show the full return here.",
          releaseRegionAria: "Release snapshot investigation",
          releaseLoadingTimeline: "Loading release timeline…",
          releaseErrorTimeline: "Could not load release timeline.",
          releaseEmptySnapshots: "No snapshots available.",
          releaseKicker: "Release investigation",
          releaseSurfaceTitle: "Snapshot timeline and comparison",
          releaseSurfaceIntro:
            "Read current state and history, qualify the snapshot with evidence, then compare two versions before opening a canonical catalog entry.",
          releaseTimelineHeading: "Event timeline",
          releaseTimelineHint:
            "Each card groups release status, reason, optional rollback and evidence correlated to the snapshot.",
          releaseReasonPrefix: "Reason: ",
          releaseProofsLead: "Quality evidence (snapshot correlation)",
          releaseCompareHeading: "Compare two snapshots",
          releaseCompareHint:
            "Choose the reference (source) and compared version (target). The table below summarizes gaps by technical axis.",
          releaseSnapshotSourceLabel: "Source snapshot (reference)",
          releaseSnapshotTargetLabel: "Target snapshot (compared)",
          releaseDiffLoading: "Loading snapshot diff…",
          releaseDiffError: "Could not load snapshot diff.",
          releaseDiffTitle: "Comparison summary",
          releaseCompareBannerAria: "Compared versions for this diff",
          releaseCompareRoleSource: "Reference (source)",
          releaseCompareRoleTarget: "Compared (target)",
          releaseDiffTableHeading: "Gaps by canonical entry",
          releaseDiffTableLead:
            "Assembly, execution profile and output contract: synthetic state before opening catalog detail.",
          releaseDiffColManifest: "Manifest entry",
          releaseDiffColScope: "Change scope",
          releaseDiffColAssembly: "Assembly",
          releaseDiffColExec: "Execution profile",
          releaseDiffColContract: "Output contract",
          releaseDiffColCatalog: "Catalog",
          releaseDiffChanged: "Changed",
          releaseDiffUnchanged: "Unchanged",
          releaseOpenCatalogTitle: "Open in catalog",
          placeholderUnknownClassification: "n/a",
          placeholderUnknownReason: "n/a",
          consumptionUnknownProvider: "unknown",
        }
      : lang === "es"
        ? {
            subNavAriaLabel: "Secciones de administración de prompts",
            catalogRegionAria: "Catálogo canónico de prompts LLM",
            filterSearchLabel: "Búsqueda",
            filterSearchPlaceholder: "Tupla canónica o manifest_entry_id",
            filterFeatureLabel: "Feature",
            filterSubfeatureLabel: "Subfeature",
            filterPlanLabel: "Plan",
            filterLocaleLabel: "Locale",
            filterProviderLabel: "Proveedor",
            filterSortLabel: "Ordenar",
            filterSortOrderLabel: "Dirección",
            sortOrderAsc: "Ascendente",
            sortOrderDesc: "Descendente",
            resetCatalogFilters: "Restablecer filtros",
            sortAriaCatalog: "Campo de ordenación del catálogo",
            sortOrderAriaCatalog: "Orden del catálogo",
            activeFiltersAria: "Filtros activos",
            sortOptionFeature: "Feature",
            sortOptionSubfeature: "Subfeature",
            sortOptionPlan: "Plan",
            sortOptionLocale: "Locale",
            sortOptionManifestEntry: "Entrada de manifiesto",
            sortOptionProvider: "Proveedor",
            sortOptionSourceOfTruth: "Fuente de verdad",
            sortOptionAssemblyStatus: "Estado del ensamblado",
            sortOptionReleaseHealth: "Salud de release",
            sortOptionCatalogVisibility: "Visibilidad del catálogo",
            filterAllFeminine: "Todas",
            filterAllMasculine: "Todos",
            filterSourceOfTruth: "Fuente de verdad",
            filterAssemblyStatus: "Estado del ensamblado",
            filterReleaseHealth: "Salud de release",
            filterCatalogVisibility: "Visibilidad del catálogo",
            noActiveFilters: "Sin filtros activos",
            advancedFiltersToggle: "Filtros avanzados",
            catalogLoading: "Cargando catálogo canónico…",
            catalogError: "No se pudo cargar el catálogo canónico.",
            tableColTuple: "Tupla canónica",
            tableColSnapshot: "Snapshot activo",
            tableColProviderModel: "Proveedor / modelo",
            tableColHealth: "Salud",
            tableColAction: "Acción",
            healthSignalPrefix: "señal",
            notAvailable: "n/d",
            openDetail: "Abrir detalle",
            catalogPrev: "Anterior",
            catalogNext: "Siguiente",
            detailPanelAria: "Detalle de entrada del catálogo",
            detailSummaryTitle: "Resumen",
            detailManifestEntryDt: "Entrada de manifiesto",
            detailAssemblyDt: "Ensamblado",
            detailExecutionProfileDt: "Perfil de ejecución",
            detailOutputContractDt: "Contrato de salida",
            detailCatalogVisibilityDt: "Visibilidad del catálogo",
            detailOffPageFromResolved:
              "Entrada fuera de la página actual — el resumen proviene del detalle resuelto.",
            detailOffPageIdOnly: "Entrada fuera de la página actual — identificador",
            resolvedPanelAria: "Detalle del ensamblado resuelto",
            inspectionBannerAria: "Modo de inspección activo para este detalle",
            inspectionBannerKicker: "Modo de inspección",
            inspectionSectionAria: "Modo de inspección",
            inspectionHeading: "Modo de inspección",
            inspectionModeFieldCaption: "Modo de inspección",
            inspectionModeSelectAria: "Modo de inspección del detalle",
            executionStateSectionAria: "Estado de ejecución",
            sourceWord: "fuente",
            actionsSectionAria: "Acciones",
            actionsTitle: "Acciones",
            actionsRiskNote:
              "Riesgo: ejecución real del proveedor fuera del tráfico nominal — trazada en servidor, confirmación obligatoria antes del envío.",
            samplePayloadFieldCaption: "Sample payload (precondición de ejecución)",
            samplePayloadSelectAria: "Selector de sample payload en runtime",
            noSamplePayloadOption: "Sin sample payload",
            executeWithLlm: "Ejecutar con el LLM",
            executeWithLlmPending: "Ejecución LLM…",
            promptsZoneAria: "Prompts",
            promptsZoneTitle: "Prompts",
            placeholdersZoneAria: "Placeholders",
            placeholdersZoneTitle: "Placeholders",
            placeholdersIntro:
              "Placeholders resueltos/parciales para lectura operativa (sin JSON bruto). Las acciones de sample payload están en Acciones.",
            placeholdersEmpty: "Sin placeholders para este objetivo.",
            llmReturnZoneAria: "Retorno LLM",
            llmReturnZoneTitle: "Retorno LLM",
            llmOutputLead: "Salida de ejecución en vivo",
            validationStatusDt: "Estado de validación",
            durationDt: "Duración",
            pathDt: "Ruta",
            providerModelDt: "Proveedor / modelo",
            tokensDt: "Tokens (entrada / salida)",
            gatewayRequestDt: "Petición gateway",
            graphZoneAria: "Grafo lógico",
            graphZoneTitle: "Grafo lógico",
            graphIntro:
              "Cadena inspeccionable: esquema interactivo (zoom/pan) con respaldo textual. Fuentes de composición, pipeline, mensajes del proveedor y datos runtime.",
            compositionSourcesSummary: "Fuentes de composición (texto completo)",
            execProfileGridLabel: "Perfil de ejecución",
            reasoningGridLabel: "Razonamiento",
            verbosityGridLabel: "Verbosidad",
            detailEmptySelectRow: "Seleccione una fila del catálogo para mostrar el detalle resuelto.",
            resolvedLoading: "Cargando detalle…",
            resolvedLoadingSamples: "Cargando sample payloads…",
            runtimePreviewIdle:
              'Seleccione «Vista previa runtime» para activar los sample payloads y la ejecución LLM desde este panel.',
            manualExecIncomplete:
              "Vista previa runtime incompleta: corrija los placeholders bloqueantes o complete el sample antes de ejecutar.",
            manualExecFailed: "La ejecución falló — véase el panel Acciones.",
            manualExecSuccessNoData:
              "Ejecución marcada como correcta pero sin datos de retorno. Reintente o revise los logs de la API.",
            manualExecHintReady:
              'Use Acciones («Ejecutar con el LLM») para mostrar el retorno completo (metadatos, prompt efectivo, salidas).',
            manualExecHintNeedSample:
              "Seleccione un sample payload válido en Acciones y ejecute para mostrar el retorno operador.",
            manualExecPassToRuntime:
              "Pase a vista previa runtime para ejecutar el proveedor y mostrar aquí el retorno completo.",
            releaseRegionAria: "Investigación de snapshots de release",
            releaseLoadingTimeline: "Cargando línea de tiempo release…",
            releaseErrorTimeline: "No se pudo cargar la línea de tiempo release.",
            releaseEmptySnapshots: "No hay snapshots disponibles.",
            releaseKicker: "Investigación release",
            releaseSurfaceTitle: "Línea de tiempo y comparación de snapshots",
            releaseSurfaceIntro:
              "Lea el estado actual y el historial, califique el snapshot con pruebas, luego compare dos versiones antes de abrir una entrada canónica del catálogo.",
            releaseTimelineHeading: "Cronología de eventos",
            releaseTimelineHint:
              "Cada tarjeta agrupa el estado release, el motivo, un rollback opcional y pruebas correlacionadas al snapshot.",
            releaseReasonPrefix: "Motivo: ",
            releaseProofsLead: "Pruebas de calidad (correlación snapshot)",
            releaseCompareHeading: "Comparar dos snapshots",
            releaseCompareHint:
              "Elija la referencia (origen) y la versión comparada (destino). La tabla resume las diferencias por eje técnico.",
            releaseSnapshotSourceLabel: "Snapshot origen (referencia)",
            releaseSnapshotTargetLabel: "Snapshot destino (comparado)",
            releaseDiffLoading: "Cargando diff de snapshots…",
            releaseDiffError: "No se pudo cargar el diff de snapshots.",
            releaseDiffTitle: "Síntesis de comparación",
            releaseCompareBannerAria: "Versiones comparadas para este diff",
            releaseCompareRoleSource: "Referencia (origen)",
            releaseCompareRoleTarget: "Comparada (destino)",
            releaseDiffTableHeading: "Diferencias por entrada canónica",
            releaseDiffTableLead:
              "Ensamblado, perfil de ejecución y contrato de salida: estado sintético antes de abrir el detalle del catálogo.",
            releaseDiffColManifest: "Entrada manifiesto",
            releaseDiffColScope: "Alcance del cambio",
            releaseDiffColAssembly: "Ensamblado",
            releaseDiffColExec: "Perfil de ejecución",
            releaseDiffColContract: "Contrato de salida",
            releaseDiffColCatalog: "Catálogo",
            releaseDiffChanged: "Modificado",
            releaseDiffUnchanged: "Sin cambios",
            releaseOpenCatalogTitle: "Abrir en el catálogo",
            placeholderUnknownClassification: "n/d",
            placeholderUnknownReason: "n/d",
            consumptionUnknownProvider: "desconocido",
          }
        : {
            subNavAriaLabel: "Sections administration des prompts",
            catalogRegionAria: "Catalogue canonique des prompts LLM",
            filterSearchLabel: "Recherche",
            filterSearchPlaceholder: "Tuple canonique ou manifest_entry_id",
            filterFeatureLabel: "Fonctionnalité",
            filterSubfeatureLabel: "Sous-fonctionnalité",
            filterPlanLabel: "Formule",
            filterLocaleLabel: "Locale",
            filterProviderLabel: "Fournisseur",
            filterSortLabel: "Tri",
            filterSortOrderLabel: "Ordre",
            sortOrderAsc: "Ascendant",
            sortOrderDesc: "Descendant",
            resetCatalogFilters: "Réinitialiser les filtres",
            sortAriaCatalog: "Tri catalogue",
            sortOrderAriaCatalog: "Ordre tri catalogue",
            activeFiltersAria: "Filtres actifs",
            sortOptionFeature: "Fonctionnalité",
            sortOptionSubfeature: "Sous-fonctionnalité",
            sortOptionPlan: "Formule",
            sortOptionLocale: "Locale",
            sortOptionManifestEntry: "Entrée manifeste",
            sortOptionProvider: "Fournisseur",
            sortOptionSourceOfTruth: "Référence cataloguée",
            sortOptionAssemblyStatus: "Statut d'assembly",
            sortOptionReleaseHealth: "Santé release",
            sortOptionCatalogVisibility: "Visibilité catalogue",
            filterAllFeminine: "Toutes",
            filterAllMasculine: "Tous",
            filterSourceOfTruth: "Référence cataloguée",
            filterAssemblyStatus: "Statut d'assembly",
            filterReleaseHealth: "Santé release",
            filterCatalogVisibility: "Visibilité catalogue",
            noActiveFilters: "Aucun filtre actif",
            advancedFiltersToggle: "Filtres avancés",
            catalogLoading: "Chargement du catalogue canonique…",
            catalogError: "Impossible de charger le catalogue canonique.",
            tableColTuple: "Tuple canonique",
            tableColSnapshot: "Snapshot actif",
            tableColProviderModel: "Fournisseur / modèle",
            tableColHealth: "Indicateurs",
            tableColAction: "Action",
            healthSignalPrefix: "signal",
            notAvailable: "n/d",
            openDetail: "Ouvrir le détail",
            catalogPrev: "Précédent",
            catalogNext: "Suivant",
            detailPanelAria: "Détail catalogue entrée",
            detailSummaryTitle: "Résumé",
            detailManifestEntryDt: "Entrée manifeste",
            detailAssemblyDt: "Assemblage",
            detailExecutionProfileDt: "Profil d'exécution",
            detailOutputContractDt: "Contrat de sortie",
            detailCatalogVisibilityDt: "Visibilité catalogue",
            detailOffPageFromResolved:
              "Entrée hors page courante du tableau — le résumé ci-dessus provient du détail résolu.",
            detailOffPageIdOnly: "Entrée hors page courante — identifiant",
            resolvedPanelAria: "Détail d'assemblage résolu",
            inspectionBannerAria: "Mode d'inspection actif pour ce détail",
            inspectionBannerKicker: "Mode d'inspection",
            inspectionSectionAria: "Mode d'inspection",
            inspectionHeading: "Mode d'inspection",
            inspectionModeFieldCaption: "Mode d'inspection",
            inspectionModeSelectAria: "Mode d'inspection du détail",
            executionStateSectionAria: "État d'exécution",
            sourceWord: "source",
            actionsSectionAria: "Actions",
            actionsTitle: "Actions",
            actionsRiskNote:
              "Risque : exécution fournisseur réelle hors trafic nominal — tracée côté serveur, confirmation obligatoire avant envoi.",
            samplePayloadFieldCaption: "Sample payload (précondition exécution)",
            samplePayloadSelectAria: "Sélecteur sample payload runtime",
            noSamplePayloadOption: "Aucun sample payload",
            executeWithLlm: "Exécuter avec le LLM",
            executeWithLlmPending: "Exécution LLM…",
            promptsZoneAria: "Prompts",
            promptsZoneTitle: "Prompts",
            placeholdersZoneAria: "Placeholders",
            placeholdersZoneTitle: "Placeholders",
            placeholdersIntro:
              "Placeholders résolus ou partiels pour une lecture opérable (sans analyse de JSON brut). Les actions sur les sample payloads sont regroupées dans la zone Actions.",
            placeholdersEmpty: "Aucun placeholder disponible pour cette cible.",
            llmReturnZoneAria: "Retour LLM",
            llmReturnZoneTitle: "Retour LLM",
            llmOutputLead: "Sortie d'exécution live",
            validationStatusDt: "Statut validation",
            durationDt: "Durée",
            pathDt: "Chemin",
            providerModelDt: "Fournisseur / modèle",
            tokensDt: "Tokens (entrée / sortie)",
            gatewayRequestDt: "Requête gateway",
            graphZoneAria: "Graphe logique",
            graphZoneTitle: "Graphe logique",
            graphIntro:
              "Chaîne inspectable : schéma interactif (zoom / déplacement) avec secours texte. Sources de composition, pipeline, messages fournisseur et données runtime.",
            compositionSourcesSummary: "Sources de composition (texte intégral)",
            execProfileGridLabel: "Profil d'exécution",
            reasoningGridLabel: "Raisonnement",
            verbosityGridLabel: "Verbosité",
            detailEmptySelectRow: "Sélectionnez une ligne du catalogue pour afficher le détail résolu.",
            resolvedLoading: "Chargement du détail…",
            resolvedLoadingSamples: "Chargement des sample payloads…",
            runtimePreviewIdle:
              "Sélectionnez « Prévisualisation runtime » pour activer les sample payloads et l'exécution LLM depuis cette zone.",
            manualExecIncomplete:
              "Prévisualisation runtime incomplète : corrigez les placeholders bloquants ou complétez le sample avant d'exécuter.",
            manualExecFailed: "L'exécution a échoué — le détail est affiché dans la zone Actions.",
            manualExecSuccessNoData:
              "Exécution signalée comme réussie mais sans données de retour. Réessayez ou vérifiez les journaux côté API.",
            manualExecHintReady:
              "Utilisez la zone Actions (« Exécuter avec le LLM ») pour afficher le retour complet (métadonnées, prompt effectif, sorties).",
            manualExecHintNeedSample:
              "Sélectionnez un sample payload valide dans la zone Actions puis exécutez pour afficher le retour opérateur.",
            manualExecPassToRuntime:
              "Passez en prévisualisation runtime pour exécuter le fournisseur et afficher ici le retour complet.",
            releaseRegionAria: "Investigation des snapshots release",
            releaseLoadingTimeline: "Chargement de la timeline release…",
            releaseErrorTimeline: "Impossible de charger la timeline release.",
            releaseEmptySnapshots: "Aucun snapshot disponible.",
            releaseKicker: "Investigation release",
            releaseSurfaceTitle: "Timeline et comparaison de snapshots",
            releaseSurfaceIntro:
              "Lire l'état courant et l'historique, qualifier le snapshot via les preuves, puis comparer deux versions avant d'ouvrir une entrée canonique dans le catalogue.",
            releaseTimelineHeading: "Chronologie des événements",
            releaseTimelineHint:
              "Chaque carte regroupe statut release, motif, rollback éventuel et preuves corrélées au snapshot.",
            releaseReasonPrefix: "Motif : ",
            releaseProofsLead: "Preuves qualité (corrélation snapshot)",
            releaseCompareHeading: "Comparer deux snapshots",
            releaseCompareHint:
              "Choisissez la référence (source) et la version comparée (cible). Le tableau ci-dessous synthétise les écarts par axe technique.",
            releaseSnapshotSourceLabel: "Snapshot source (référence)",
            releaseSnapshotTargetLabel: "Snapshot cible (comparée)",
            releaseDiffLoading: "Chargement du diff snapshots…",
            releaseDiffError: "Impossible de charger le diff snapshots.",
            releaseDiffTitle: "Synthèse de comparaison",
            releaseCompareBannerAria: "Versions comparées pour ce diff",
            releaseCompareRoleSource: "Référence (source)",
            releaseCompareRoleTarget: "Comparée (cible)",
            releaseDiffTableHeading: "Écarts par entrée canonique",
            releaseDiffTableLead:
              "Assemblage, profil d'exécution et contrat de sortie : état synthétique avant d'ouvrir le détail catalogue.",
            releaseDiffColManifest: "Entrée manifeste",
            releaseDiffColScope: "Portée du changement",
            releaseDiffColAssembly: "Assemblage",
            releaseDiffColExec: "Profil d'exécution",
            releaseDiffColContract: "Contrat de sortie",
            releaseDiffColCatalog: "Catalogue",
            releaseDiffChanged: "Modifié",
            releaseDiffUnchanged: "Inchangé",
            releaseOpenCatalogTitle: "Ouvrir dans le catalogue",
            placeholderUnknownClassification: "n/d",
            placeholderUnknownReason: "n/d",
            consumptionUnknownProvider: "inconnu",
          }

  return L
}

export function adminPromptsCatalogStrings(lang: AstrologyLang): AdminPromptsCatalogStrings {
  const sot = SOURCE_OF_TRUTH[lang]
  const rel = RELEASE_HEALTH[lang]
  const vis = CATALOG_VISIBILITY[lang]
  const run = RUNTIME_SIGNAL[lang]
  const asm = ASSEMBLY_STATUS[lang]
  const ctx = CONTEXT_COMPENSATION[lang]
  const releaseEvents = RELEASE_EVENT_TYPE[lang]
  const releaseStatuses = RELEASE_CURRENT_STATUS[lang]
  const proofTypes = RELEASE_PROOF_TYPE[lang]
  const proofVerdicts = RELEASE_PROOF_VERDICT[lang]
  const proofStatuses = RELEASE_PROOF_STATUS[lang]
  const base = buildStrings(lang)

  const inspectionModeOptions: { value: AdminInspectionMode; label: string }[] =
    lang === "en"
      ? [
          { value: "assembly_preview", label: "Assembly preview" },
          { value: "runtime_preview", label: "Runtime preview" },
          { value: "live_execution", label: "Live execution (runtime semantics)" },
        ]
      : lang === "es"
        ? [
            { value: "assembly_preview", label: "Previsualización de assembly" },
            { value: "runtime_preview", label: "Previsualización runtime" },
            { value: "live_execution", label: "Ejecución en vivo (semántica runtime)" },
          ]
        : [
            { value: "assembly_preview", label: "Prévisualisation d'assemblage" },
            { value: "runtime_preview", label: "Prévisualisation runtime" },
            { value: "live_execution", label: "Exécution en direct (sémantique runtime)" },
          ]

  const inspectionShort: Record<AdminInspectionMode, string> =
    lang === "en"
      ? { assembly_preview: "Assembly", runtime_preview: "Runtime", live_execution: "Live" }
      : lang === "es"
        ? { assembly_preview: "Assembly", runtime_preview: "Runtime", live_execution: "Live" }
        : {
            assembly_preview: "Préassemblage",
            runtime_preview: "Prévisualisation runtime",
            live_execution: "Inspection en direct",
          }

  const inspectionHelp: Record<AdminInspectionMode, string> =
    lang === "en"
      ? {
          assembly_preview:
            "Static preview: placeholders only available at runtime are flagged as missing but non-blocking.",
          runtime_preview:
            "Runtime preview: missing required placeholders are blocking. Real provider execution uses “Execute with LLM” when preview is complete.",
          live_execution:
            "Live inspection: same placeholder semantics as runtime_preview. Real provider calls are explicitly triggered from runtime mode (dedicated button).",
        }
      : lang === "es"
        ? {
            assembly_preview:
              "Previsualización estática: los placeholders solo disponibles en runtime aparecen como ausentes pero no bloquean.",
            runtime_preview:
              "Previsualización runtime: los placeholders obligatorios ausentes bloquean. La ejecución real del proveedor usa « Ejecutar con el LLM » cuando la previsualización está completa.",
            live_execution:
              "Inspección en vivo: misma semántica de placeholders que runtime_preview. Las llamadas reales al proveedor se disparan explícitamente desde el modo runtime (botón dedicado).",
          }
        : {
            assembly_preview:
              "Prévisualisation statique : les placeholders attendus uniquement au runtime restent signalés comme absents mais non bloquants.",
            runtime_preview:
              "Prévisualisation runtime : les placeholders requis manquants sont bloquants. L'exécution réelle du fournisseur se fait via « Exécuter avec le LLM » lorsque la prévisualisation est complète.",
            live_execution:
              "Inspection live : même sémantique placeholder que runtime_preview. L'appel fournisseur réel reste explicitement déclenché depuis le mode runtime (bouton dédié).",
          }

  const disclosureFr = {
    disclosureAssembled: "Prompt assemblé",
    disclosurePostInjectors: "Après injecteurs",
    disclosureRendered: "Prompt rendu",
    disclosureSystemPolicy: "Politique système stricte",
    disclosureDeveloper: "Contenu développeur rendu",
    disclosurePersona: "Bloc persona",
    disclosureExecParamsPreview: "Paramètres d'exécution (prévisualisation assembly)",
    disclosureRuntimeResolved: "Paramètres runtime résolus (exécution)",
    disclosurePromptSent: "Prompt envoyé au fournisseur (anonymisé)",
    disclosureStructuredOut: "Sortie structurée (validée / rédaction admin)",
    disclosureRawOut: "Réponse brute fournisseur (anonymisée)",
  }
  const disclosureEn = {
    disclosureAssembled: "Assembled prompt",
    disclosurePostInjectors: "Post-injectors prompt",
    disclosureRendered: "Rendered prompt",
    disclosureSystemPolicy: "System hard policy",
    disclosureDeveloper: "Rendered developer content",
    disclosurePersona: "Persona block",
    disclosureExecParamsPreview: "Execution parameters (assembly preview)",
    disclosureRuntimeResolved: "Resolved runtime parameters (execution)",
    disclosurePromptSent: "Prompt sent to provider (redacted)",
    disclosureStructuredOut: "Structured output (validated / admin redaction)",
    disclosureRawOut: "Raw provider response (redacted)",
  }
  const disclosureEs = {
    disclosureAssembled: "Prompt ensamblado",
    disclosurePostInjectors: "Tras inyectores",
    disclosureRendered: "Prompt renderizado",
    disclosureSystemPolicy: "Política estricta del sistema",
    disclosureDeveloper: "Contenido desarrollador renderizado",
    disclosurePersona: "Bloque persona",
    disclosureExecParamsPreview: "Parámetros de ejecución (previsualización assembly)",
    disclosureRuntimeResolved: "Parámetros runtime resueltos (ejecución)",
    disclosurePromptSent: "Prompt enviado al proveedor (anonimizado)",
    disclosureStructuredOut: "Salida estructurada (validada / redacción admin)",
    disclosureRawOut: "Respuesta cruda del proveedor (anonimizada)",
  }
  const disclosure = lang === "en" ? disclosureEn : lang === "es" ? disclosureEs : disclosureFr

  return {
    ...base,
    ...disclosure,
    healthLine: (releaseLabel, runtimeLabel, visibilityLabel) =>
      lang === "en"
        ? `${releaseLabel} · ${base.healthSignalPrefix} ${runtimeLabel} · ${visibilityLabel}`
        : lang === "es"
          ? `${releaseLabel} · ${base.healthSignalPrefix} ${runtimeLabel} · ${visibilityLabel}`
          : `${releaseLabel} · ${base.healthSignalPrefix} ${runtimeLabel} · ${visibilityLabel}`,
    activeFilterSearch: (value) =>
      lang === "en"
        ? `Search: ${value}`
        : lang === "es"
          ? `Búsqueda: ${value}`
          : `Recherche : ${value}`,
    activeFilterFeature: (value) =>
      lang === "en" ? `Feature: ${value}` : lang === "es" ? `Feature: ${value}` : `Fonctionnalité : ${value}`,
    activeFilterSubfeature: (value) =>
      lang === "en"
        ? `Subfeature: ${value}`
        : lang === "es"
          ? `Subfeature: ${value}`
          : `Sous-fonctionnalité : ${value}`,
    activeFilterPlan: (value) =>
      lang === "en" ? `Plan: ${value}` : lang === "es" ? `Plan: ${value}` : `Formule : ${value}`,
    activeFilterLocale: (value) =>
      lang === "en" ? `Locale: ${value}` : lang === "es" ? `Locale: ${value}` : `Locale : ${value}`,
    activeFilterProvider: (value) =>
      lang === "en"
        ? `Provider: ${value}`
        : lang === "es"
          ? `Proveedor: ${value}`
          : `Fournisseur : ${value}`,
    activeFilterSourceOfTruth: (value) =>
      lang === "en"
        ? `Source of truth: ${value}`
        : lang === "es"
          ? `Fuente de verdad: ${value}`
          : `Référence cataloguée : ${value}`,
    activeFilterAssembly: (value) =>
      lang === "en"
        ? `Assembly: ${value}`
        : lang === "es"
          ? `Ensamblado: ${value}`
          : `Assembly : ${value}`,
    activeFilterReleaseHealth: (value) =>
      lang === "en"
        ? `Release health: ${value}`
        : lang === "es"
          ? `Salud release: ${value}`
          : `Santé release : ${value}`,
    activeFilterVisibility: (value) =>
      lang === "en"
        ? `Visibility: ${value}`
        : lang === "es"
          ? `Visibilidad: ${value}`
          : `Visibilité : ${value}`,
    catalogFooterLines: (total, minutes) =>
      lang === "en"
        ? `${total} rows · runtime window: ${minutes} min`
        : lang === "es"
          ? `${total} filas · ventana runtime: ${minutes} min`
          : `${total} lignes · fenêtre runtime : ${minutes} min`,
    catalogPage: (n) => (lang === "en" ? `Page ${n}` : lang === "es" ? `Página ${n}` : `Page ${n}`),
    resolvedStateLead: (modeShort, sourceLabel, snapshot) =>
      lang === "en"
        ? `Resolved state: ${modeShort} · source ${sourceLabel}${snapshot ? ` · snapshot ${snapshot}` : ""}`
        : lang === "es"
          ? `Estado resuelto: ${modeShort} · fuente ${sourceLabel}${snapshot ? ` · snapshot ${snapshot}` : ""}`
          : `État résolu : ${modeShort} · source ${sourceLabel}${snapshot ? ` · snapshot ${snapshot}` : ""}`,
    promptsSourceLine: (sourceLabel, snapshot) =>
      lang === "en"
        ? `Source: ${sourceLabel} · snapshot: ${snapshot}`
        : lang === "es"
          ? `Fuente: ${sourceLabel} · snapshot: ${snapshot}`
          : `Source : ${sourceLabel} · snapshot : ${snapshot}`,
    contextQualityLine: (status) =>
      lang === "en"
        ? `Context handling: ${status}`
        : lang === "es"
          ? `Manejo de contexto: ${status}`
          : `Qualité de contexte (compensation) : ${status}`,
    modeBadge: (short) =>
      lang === "en" ? `Mode: ${short}` : lang === "es" ? `Modo: ${short}` : `Mode : ${short}`,
    releaseEventLine: (eventType, when, count) =>
      lang === "en"
        ? `Event: ${eventType} · ${when} · ${count}`
        : lang === "es"
          ? `Evento: ${eventType} · ${when} · ${count}`
          : `Événement : ${eventType} · ${when} · ${count}`,
    releaseCurrentLine: (status, transitions) =>
      lang === "en"
        ? `Current state: ${status} · recorded transitions: ${transitions}`
        : lang === "es"
          ? `Estado actual: ${status} · transiciones registradas: ${transitions}`
          : `État courant : ${status} · transitions enregistrées : ${transitions}`,
    releaseRollbackLine: (from, to) =>
      lang === "en"
        ? `Rollback: ${from} → ${to}`
        : lang === "es"
          ? `Rollback: ${from} → ${to}`
          : `Rollback : ${from} → ${to}`,
    releaseOpenCatalogAria: (manifestId) =>
      lang === "en"
        ? `Open canonical entry ${manifestId} in catalog`
        : lang === "es"
          ? `Abrir la entrada canónica ${manifestId} en el catálogo`
          : `Ouvrir l'entrée canonique ${manifestId} dans le catalogue`,
    manifestEntriesCount: (n) =>
      lang === "en"
        ? `${n} manifest ${n === 1 ? "entry" : "entries"}`
        : lang === "es"
          ? `${n} entrada(s) de manifiesto`
          : `${n} entrée(s) manifeste`,
    labelReleaseEventType: (raw) =>
      releaseEvents[raw] ??
      (lang === "en"
        ? `API event: ${raw}`
        : lang === "es"
          ? `Evento API: ${raw}`
          : `Événement API : ${raw}`),
    labelReleaseCurrentStatus: (raw) =>
      releaseStatuses[raw] ??
      (lang === "en"
        ? `API status: ${raw}`
        : lang === "es"
          ? `Estado API: ${raw}`
          : `Statut API : ${raw}`),
    labelReleaseProofType: (raw) =>
      proofTypes[raw] ??
      (lang === "en"
        ? `API proof: ${raw}`
        : lang === "es"
          ? `Prueba API: ${raw}`
          : `Preuve API : ${raw}`),
    labelReleaseProofOutcome: (verdict, status) => {
      if (verdict) {
        return (
          proofVerdicts[verdict] ??
          (lang === "en"
            ? `API verdict: ${verdict}`
            : lang === "es"
              ? `Veredicto API: ${verdict}`
              : `Verdict API : ${verdict}`)
        )
      }
      return (
        proofStatuses[status] ??
        (lang === "en"
          ? `API status: ${status}`
          : lang === "es"
            ? `Estado API: ${status}`
            : `Statut API : ${status}`)
      )
    },
    catalogRowAria: (tupleHint, selected) =>
      lang === "en"
        ? `${selected ? "Selected catalog row" : "Catalog row"}: ${tupleHint}. Activate with Enter or Space.`
        : lang === "es"
          ? `${selected ? "Fila de catálogo seleccionada" : "Fila de catálogo"}: ${tupleHint}. Activar con Intro o Espacio.`
          : `${selected ? "Ligne catalogue sélectionnée" : "Ligne catalogue"} : ${tupleHint}. Activer avec Entrée ou Espace.`,
    labelSourceOfTruthStatus: (raw) => mapOrRaw(sot, raw),
    labelReleaseHealthStatus: (raw) => mapOrRaw(rel, raw),
    labelCatalogVisibilityStatus: (raw) => mapOrRaw(vis, raw),
    labelRuntimeSignalStatus: (raw) => mapOrRaw(run, raw),
    labelAssemblyStatus: (raw) => mapOrRaw(asm, raw),
    labelContextCompensation: (raw) => mapOrRaw(ctx, raw),
    inspectionModeOptions,
    inspectionModeShortLabel: (mode) => inspectionShort[mode] ?? mode,
    inspectionModeFullLabel: (mode) => inspectionModeOptions.find((o) => o.value === mode)?.label ?? mode,
    inspectionModeHelpText: (mode) => inspectionHelp[mode] ?? "",
    placeholderStatusLabel: (status) => {
      const map =
        lang === "en"
          ? {
              resolved: "Resolved",
              optional_missing: "Optional missing",
              fallback_used: "Fallback applied",
              blocking_missing: "Blocking (missing)",
              expected_missing_in_preview: "Missing in preview (expected at runtime)",
              unknown: "Unknown",
            }
          : lang === "es"
            ? {
                resolved: "Resuelto",
                optional_missing: "Opcional ausente",
                fallback_used: "Respaldo aplicado",
                blocking_missing: "Bloqueante (ausente)",
                expected_missing_in_preview: "Ausente en vista previa (esperado en runtime)",
                unknown: "Desconocido",
              }
            : {
                resolved: "Résolu",
                optional_missing: "Optionnel absent",
                fallback_used: "Repli appliqué",
                blocking_missing: "Bloquant (manquant)",
                expected_missing_in_preview: "Absent en prévisualisation (attendu au runtime)",
                unknown: "Inconnu",
              }
      return map[status] ?? status
    },
    placeholderRedactionLevelLabel: (item) => {
      if (!item.safe_to_display) {
        return lang === "en" ? "Redacted" : lang === "es" ? "Oculto" : "Masqué"
      }
      return lang === "en" ? "Displayable" : lang === "es" ? "Mostrable" : "Affichable"
    },
    placeholderSourceLabel: (source) => {
      if (!source) return base.notAvailable
      const map =
        lang === "en"
          ? {
              runtime_context: "Runtime context",
              static_preview_gap: "Partial preview",
              fallback: "Fallback",
              missing_required: "Missing required",
              missing_optional: "Missing optional",
            }
          : lang === "es"
            ? {
                runtime_context: "Contexto runtime",
                static_preview_gap: "Vista previa parcial",
                fallback: "Respaldo",
                missing_required: "Requerido ausente",
                missing_optional: "Opcional ausente",
              }
            : {
                runtime_context: "Contexte runtime",
                static_preview_gap: "Preview partielle",
                fallback: "Repli",
                missing_required: "Manquant requis",
                missing_optional: "Manquant optionnel",
              }
      return map[source as keyof typeof map] ?? source
    },
    placeholderPreviewValue: (item) => {
      if (!item.safe_to_display) {
        return lang === "en" ? "redacted" : lang === "es" ? "oculto" : "masqué"
      }
      return item.value_preview ?? ""
    },
    formatConsumptionAxisLabel: (view, row) => {
      if (view === "user") {
        const uid = row.user_id
        const uidStr = uid === null || uid === undefined ? base.notAvailable : String(uid)
        return row.user_email ?? `user:${uidStr}`
      }
      if (view === "subscription") {
        return row.subscription_plan ?? (lang === "en" ? "unknown" : lang === "es" ? "desconocido" : "inconnu")
      }
      return `${row.feature ?? (lang === "en" ? "unknown" : lang === "es" ? "desconocido" : "inconnu")} / ${row.subfeature ?? "—"}`
    },
    consumptionUnknownFeatureCell: (feature, subfeature) =>
      `${feature ?? (lang === "en" ? "unknown" : lang === "es" ? "desconocido" : "inconnu")} / ${subfeature ?? "—"}`,
    ...(() => {
      const modal = MANUAL_LLM_MODAL[lang]
      const resolvedAsm = RESOLVED_ASSEMBLY_ERRORS[lang]
      const manualFail = MANUAL_EXEC_FAILURE_LEADS[lang]
      const renderErr = RENDER_ERROR_LEADS[lang]
      const relDiff = RELEASE_DIFF_CATEGORY[lang]
      return {
        manualLlmModalTitle: modal.title,
        manualLlmModalIntroBeforeSample: modal.introBeforeSample,
        manualLlmModalBetweenSampleAndManifest: modal.betweenSampleAndManifest,
        manualLlmModalAfterManifest: modal.afterManifest,
        manualLlmModalModePrefix: modal.modePrefix,
        manualLlmModalModeTraced: modal.modeTraced,
        manualLlmModalCancel: modal.cancel,
        manualLlmModalConfirm: modal.confirm,
        manualLlmModalExecuting: modal.executing,
        resolvedErrorLoadDetailGeneric:
          lang === "en"
            ? "Could not load assembly detail."
            : lang === "es"
              ? "No se pudo cargar el detalle del ensamblado."
              : "Impossible de charger le détail d'assembly.",
        resolvedErrorSecondaryCodeHttp: (code, status) =>
          lang === "en"
            ? `Code: ${code} · HTTP ${status}`
            : lang === "es"
              ? `Código: ${code} · HTTP ${status}`
              : `Code : ${code} · HTTP ${status}`,
        renderErrorLeadLine: (inspectionMode, renderErrorKind) => {
          if (renderErrorKind === "static_preview_incomplete") {
            return renderErr.staticIncomplete
          }
          if (inspectionMode === "live_execution") {
            return renderErr.live
          }
          return renderErr.default
        },
        releaseDiffCategoryLabel: (category) => {
          const trimmed = category.trim()
          if (category === "changed") return relDiff.changed
          if (category === "added") return relDiff.added
          if (category === "removed") return relDiff.removed
          if (category === "stable" || category === "unchanged") return relDiff.stable
          return trimmed.length > 0 ? relDiff.apiUnknown(trimmed) : relDiff.empty
        },
        resolvedAssemblyErrorMessage: (code) => resolvedAsm[code],
        manualExecutionFailureLeadMessage: (kind) => manualFail[kind],
        manualExecErrorGeneric:
          lang === "en"
            ? "Execution not possible."
            : lang === "es"
              ? "Ejecución imposible."
              : "Exécution impossible.",
      }
    })(),
  }
}

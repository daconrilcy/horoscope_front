import { useEffect, useMemo, useState, type ReactNode } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom"

import { useTranslation } from "../../i18n"
import { useAstrologyLabels } from "../../i18n/astrology"
import type { AppLocale } from "../../i18n/types"
import {
  formatLegacyPromptTimestamp,
  interpolateLegacyTemplate,
  legacyPromptStatusLabel,
  type AdminPromptsLegacyStrings,
} from "../../i18n/adminPromptsLegacy"

import {
  useAdminLlmCatalog,
  useAdminLlmUseCases,
  useAdminPromptHistory,
  useRollbackPromptVersion,
  useAdminResolvedAssembly,
  useAdminConsumption,
  useAdminConsumptionDrilldown,
  useDownloadAdminConsumptionCsv,
  useAdminLlmSamplePayloads,
  useReleaseSnapshotsTimeline,
  useReleaseSnapshotDiff,
  toUtcIsoFromDateTimeInput,
  AdminPromptsApiError,
  executeAdminCatalogSamplePayload,
  isAdminRuntimePreviewExecutable,
  type AdminConsumptionRow,
  type AdminConsumptionView,
  type AdminPromptVersion,
  type AdminInspectionMode,
  type AdminResolvedPlaceholder,
  type SnapshotTimelineItem,
} from "@api"
import { PersonasAdmin } from "./PersonasAdmin"
import { AdminSamplePayloadsAdmin } from "./AdminSamplePayloadsAdmin"
import { buildLogicGraphProjection } from "./adminPromptsLogicGraphProjection"
import { AdminPromptsLogicGraph } from "./AdminPromptsLogicGraph"
import "./AdminPromptsPage.css"

function useMatchMediaMaxWidth(maxPx: number, enabled: boolean): boolean {
  const [matches, setMatches] = useState(() => {
    if (!enabled || typeof window === "undefined" || typeof window.matchMedia !== "function") {
      return false
    }
    return window.matchMedia(`(max-width: ${maxPx}px)`).matches
  })
  useEffect(() => {
    if (!enabled || typeof window.matchMedia !== "function") {
      setMatches(false)
      return
    }
    const mq = window.matchMedia(`(max-width: ${maxPx}px)`)
    const apply = () => setMatches(mq.matches)
    apply()
    mq.addEventListener("change", apply)
    return () => mq.removeEventListener("change", apply)
  }, [enabled, maxPx])
  return matches
}

type PromptPageTab = "catalog" | "legacy" | "release" | "consumption" | "personas" | "samplePayloads"

const ADMIN_PROMPTS_BASE = "/admin/prompts"

export function resolvePromptsTabFromPath(pathname: string): PromptPageTab {
  const normalized = (pathname.replace(/\/$/, "") || "/").toLowerCase()
  if (!normalized.startsWith(ADMIN_PROMPTS_BASE)) {
    return "catalog"
  }
  const rest = normalized.slice(ADMIN_PROMPTS_BASE.length).replace(/^\//, "")
  const segment = rest.split("/")[0] ?? ""
  if (segment === "" || segment === "catalog") {
    return "catalog"
  }
  const map: Record<string, PromptPageTab> = {
    legacy: "legacy",
    release: "release",
    consumption: "consumption",
    personas: "personas",
    "sample-payloads": "samplePayloads",
  }
  return map[segment] ?? "catalog"
}

function consumptionRowKey(row: AdminConsumptionRow): string {
  return `${row.period_start_utc}::${row.user_id ?? "none"}::${row.subscription_plan ?? "none"}::${row.feature ?? "none"}::${row.subfeature ?? "none"}`
}

function formatConsumptionAxisLabel(view: AdminConsumptionView, row: AdminConsumptionRow): string {
  if (view === "user") {
    return row.user_email ?? `user:${row.user_id ?? "n/a"}`
  }
  if (view === "subscription") {
    return row.subscription_plan ?? "unknown"
  }
  return `${row.feature ?? "unknown"} / ${row.subfeature ?? "-"}`
}

function formatReleaseSnapshotIdShort(id: string): string {
  return id.length > 10 ? `${id.slice(0, 8)}…` : id
}

/** Segments complets du manifest (feature, sous-fonction, plan, locale, …) pour distinguer les variantes canoniques. */
function formatManifestEntryCatalogHint(manifestEntryId: string): string {
  const parts = manifestEntryId
    .split(":")
    .map((segment) => segment.trim())
    .filter((segment) => segment.length > 0)
  if (parts.length === 0) {
    return manifestEntryId.trim() || "—"
  }
  return parts.join(" · ")
}

function releaseDiffAxisBadgeClass(changed: boolean): string {
  return changed ? "badge badge--warning" : "badge badge--info"
}

function releaseDiffCategoryLabel(category: string): string {
  const map: Record<string, string> = {
    changed: "Écart sur cette fiche",
    added: "Ajout",
    removed: "Retrait",
    stable: "Sans écart",
  }
  const known = map[category]
  if (known !== undefined) {
    return known
  }
  const trimmed = category.trim()
  return trimmed.length > 0 ? `Catégorie (API) : ${trimmed}` : "Catégorie non renseignée"
}

type ManualLlmExecuteConfirmModalProps = {
  isPending: boolean
  manifestEntryId: string
  samplePayloadId: string
  inspectionModeLabel: string
  onCancel: () => void
  onConfirm: () => void
}

function ManualLlmExecuteConfirmModal({
  isPending,
  manifestEntryId,
  samplePayloadId,
  inspectionModeLabel,
  onCancel,
  onConfirm,
}: ManualLlmExecuteConfirmModalProps) {
  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content admin-prompts-modal admin-prompts-modal--manual-llm"
        aria-labelledby="manual-llm-exec-title"
        role="dialog"
        aria-modal="true"
      >
        <h3 id="manual-llm-exec-title">Confirmer l&apos;exécution LLM réelle</h3>
        <p className="admin-prompts-modal__copy">
          Vous allez lancer un appel fournisseur réel (hors trafic utilisateur nominal), avec le sample{" "}
          <code>{samplePayloadId}</code> sur l&apos;entrée <code>{manifestEntryId}</code>.
        </p>
        <p className="admin-prompts-modal__copy admin-prompts-modal__copy--emphasis">
          Mode actif : <strong>{inspectionModeLabel}</strong>. Cette action est tracée côté serveur.
        </p>
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            Annuler
          </button>
          <button
            className="action-button action-button--primary"
            type="button"
            disabled={isPending}
            onClick={onConfirm}
          >
            {isPending ? "Exécution en cours..." : "Confirmer l'exécution"}
          </button>
        </div>
      </div>
    </div>
  )
}

type LegacyVersionMetaStripProps = {
  version: AdminPromptVersion
  headingId: string
  variant: "reference" | "active" | "peer"
  legacy: AdminPromptsLegacyStrings
  lang: AppLocale
}

function LegacyVersionMetaStrip({ version, headingId, variant, legacy, lang }: LegacyVersionMetaStripProps) {
  const variantLabel =
    variant === "reference"
      ? legacy.metaVariantReference
      : variant === "active"
        ? legacy.metaVariantProduction
        : legacy.metaVariantPeer
  return (
    <div className="admin-prompts-legacy__meta-strip-wrap" aria-labelledby={headingId}>
      <div className="admin-prompts-legacy__meta-strip-kicker">
        <span className="admin-prompts-legacy__pill">{variantLabel}</span>
      </div>
      <dl className="admin-prompts-legacy__meta-strip">
        <div>
          <dt>{legacy.metaStatus}</dt>
          <dd>
            <span
              className={`badge ${version.status === "published" ? "badge--info" : "badge--warning"}`}
            >
              {legacyPromptStatusLabel(version.status, legacy)}
            </span>
          </dd>
        </div>
        <div>
          <dt>{legacy.metaModel}</dt>
          <dd>{version.model}</dd>
        </div>
        <div>
          <dt>{legacy.metaAuthor}</dt>
          <dd>{version.created_by}</dd>
        </div>
        <div>
          <dt>{legacy.metaCreated}</dt>
          <dd>{formatLegacyPromptTimestamp(version.created_at, lang)}</dd>
        </div>
        <div>
          <dt>{legacy.metaId}</dt>
          <dd>
            <code>{version.id}</code>
          </dd>
        </div>
      </dl>
    </div>
  )
}

type LegacyRollbackModalProps = {
  isPending: boolean
  useCaseKey: string
  useCaseDisplayName: string
  activeVersion: AdminPromptVersion | null
  targetVersion: AdminPromptVersion
  legacy: AdminPromptsLegacyStrings
  onCancel: () => void
  onConfirm: () => void
}

function LegacyRollbackModal({
  isPending,
  useCaseKey,
  useCaseDisplayName,
  activeVersion,
  targetVersion,
  legacy,
  onCancel,
  onConfirm,
}: LegacyRollbackModalProps) {
  const activeShort = activeVersion ? `${activeVersion.id.slice(0, 8)}…` : "—"
  const targetShort = `${targetVersion.id.slice(0, 8)}…`
  const statusTarget = legacyPromptStatusLabel(targetVersion.status, legacy)
  const statusActive = activeVersion ? legacyPromptStatusLabel(activeVersion.status, legacy) : ""
  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content admin-prompts-modal admin-prompts-modal--legacy-rollback"
        aria-labelledby="legacy-rollback-title"
        role="dialog"
        aria-modal="true"
      >
        <h3 id="legacy-rollback-title">{legacy.modalTitle}</h3>
        <p className="admin-prompts-modal__copy">
          {interpolateLegacyTemplate(legacy.modalPublishTarget, {
            code: targetShort,
            status: statusTarget,
            name: useCaseDisplayName,
            key: useCaseKey,
          })}
        </p>
        {activeVersion ? (
          <p className="admin-prompts-modal__copy">
            {interpolateLegacyTemplate(legacy.modalReplaceActive, {
              code: activeShort,
              status: statusActive,
            })}
          </p>
        ) : (
          <p className="admin-prompts-modal__copy text-muted">{legacy.modalNoActiveResolved}</p>
        )}
        <p className="admin-prompts-modal__copy admin-prompts-modal__copy--emphasis">{legacy.modalEmphasis}</p>
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            {legacy.modalCancel}
          </button>
          <button className="action-button action-button--primary" type="button" disabled={isPending} onClick={onConfirm}>
            {isPending ? legacy.modalConfirming : legacy.modalConfirm}
          </button>
        </div>
      </div>
    </div>
  )
}

type PromptDisclosureProps = {
  summary: string
  children: ReactNode
}

function PromptDisclosure({ summary, children }: PromptDisclosureProps) {
  return (
    <details className="admin-prompts-detail__disclosure">
      <summary className="admin-prompts-detail__disclosure-summary">{summary}</summary>
      <div className="admin-prompts-detail__disclosure-body">{children}</div>
    </details>
  )
}

type DiffRow = {
  leftText: string
  rightText: string
  leftType: "unchanged" | "removed"
  rightType: "unchanged" | "added"
}

const INSPECTION_MODE_OPTIONS: { value: AdminInspectionMode; label: string }[] = [
  { value: "assembly_preview", label: "Prévisualisation assembly" },
  { value: "runtime_preview", label: "Prévisualisation runtime" },
  { value: "live_execution", label: "Exécution live (sémantique runtime)" },
]

function inspectionModeShortLabel(mode: AdminInspectionMode): string {
  switch (mode) {
    case "assembly_preview":
      return "Assembly"
    case "runtime_preview":
      return "Runtime"
    case "live_execution":
      return "Live inspecté"
    default:
      return mode
  }
}

function inspectionModeFullLabel(mode: AdminInspectionMode): string {
  return INSPECTION_MODE_OPTIONS.find((opt) => opt.value === mode)?.label ?? mode
}

function inspectionModeHelpText(mode: AdminInspectionMode): string {
  switch (mode) {
    case "assembly_preview":
      return "Prévisualisation statique: les placeholders attendus uniquement au runtime restent signalés comme absents mais non bloquants."
    case "runtime_preview":
      return "Prévisualisation runtime: les placeholders requis manquants sont bloquants. L’exécution réelle du provider se fait via « Exécuter avec le LLM » lorsque la prévisualisation est complète."
    case "live_execution":
      return "Inspection live: même sémantique placeholder que runtime_preview. L’appel provider réel reste explicitement déclenché depuis le mode runtime (bouton dédié)."
    default:
      return ""
  }
}

const RESOLVED_ASSEMBLY_ERROR_MESSAGES_FR: Readonly<Record<string, string>> = {
  sample_payload_inactive:
    "Ce sample payload est inactif. Choisissez un autre payload ou réactivez-le dans le catalogue.",
  sample_payload_not_found: "Sample payload introuvable.",
  sample_payload_target_mismatch:
    "Ce sample payload ne correspond pas à cette entrée (feature ou locale différente).",
  sample_payload_runtime_preview_only:
    "Un sample payload ne peut être utilisé qu’en mode prévisualisation runtime.",
  invalid_sample_payload: "Le sample payload est invalide (JSON attendu : un objet).",
  manifest_entry_not_found: "Entrée de catalogue introuvable.",
  invalid_manifest_entry_id: "Identifiant d’entrée manifeste invalide.",
  runtime_preview_incomplete_for_execution:
    "La prévisualisation runtime est incomplète : corrigez les placeholders bloquants avant d’exécuter le LLM.",
  admin_manual_execution_failed: "L’exécution manuelle LLM a échoué. Consultez le message détaillé ou les journaux.",
}

function resolvedAssemblyErrorPresentation(error: unknown): { primary: string; secondary: string | null } {
  if (!(error instanceof AdminPromptsApiError)) {
    return { primary: "Impossible de charger le detail d'assembly.", secondary: null }
  }
  const mapped = RESOLVED_ASSEMBLY_ERROR_MESSAGES_FR[error.code]
  const primary = mapped ?? error.message
  const secondary =
    mapped && mapped !== error.message
      ? error.message
      : !mapped
        ? `Code : ${error.code} · HTTP ${error.status}`
        : null
  return { primary, secondary }
}

const MANUAL_EXEC_FAILURE_LEAD_FR: Readonly<Record<string, string>> = {
  runtime_preview_incomplete: "Prévisualisation runtime incomplète (placeholders bloquants)",
  input_validation: "Validation des entrées (schéma ou contexte)",
  gateway_config: "Configuration gateway ou profil d'exécution",
  output_validation: "Validation de sortie (schéma)",
  prompt_render: "Erreur de rendu du prompt (gateway)",
  provider_error: "Erreur fournisseur LLM",
  unknown_use_case: "Use case ou résolution catalogue inconnue",
  unexpected: "Erreur interne inattendue",
}

function manualExecutionFailureLead(error: unknown): string | null {
  if (!(error instanceof AdminPromptsApiError)) {
    return null
  }
  const kind = error.details.failure_kind
  return typeof kind === "string" && kind in MANUAL_EXEC_FAILURE_LEAD_FR ? MANUAL_EXEC_FAILURE_LEAD_FR[kind] : null
}

function AdminPromptsResolvedAssemblyError({ error }: { error: unknown }) {
  const { primary, secondary } = resolvedAssemblyErrorPresentation(error)
  return (
    <div className="admin-prompts-resolved__error" role="alert">
      <p className="admin-prompts-resolved__error-primary">{primary}</p>
      {secondary ? (
        <p className="admin-prompts-resolved__error-secondary text-muted">{secondary}</p>
      ) : null}
    </div>
  )
}

function placeholderStatusLabel(status: AdminResolvedPlaceholder["status"]): string {
  switch (status) {
    case "resolved":
      return "Résolu"
    case "optional_missing":
      return "Optionnel absent"
    case "fallback_used":
      return "Repli appliqué"
    case "blocking_missing":
      return "Bloquant (manquant)"
    case "expected_missing_in_preview":
      return "Absent en prévisualisation (attendu au runtime)"
    case "unknown":
      return "Inconnu"
    default:
      return status
  }
}

function placeholderStatusClassName(status: AdminResolvedPlaceholder["status"]): string {
  switch (status) {
    case "blocking_missing":
      return "admin-prompts-resolved__placeholder-status--blocking"
    case "expected_missing_in_preview":
      return "admin-prompts-resolved__placeholder-status--expected-preview"
    default:
      return "admin-prompts-resolved__placeholder-status--neutral"
  }
}

function placeholderRedactionLevelLabel(item: AdminResolvedPlaceholder): string {
  if (!item.safe_to_display) {
    return "Masqué"
  }
  return "Affichable"
}

function placeholderSourceLabel(source: string | null): string {
  if (!source) {
    return "n/a"
  }
  if (source === "runtime_context") {
    return "Contexte runtime"
  }
  if (source === "static_preview_gap") {
    return "Preview partielle"
  }
  if (source === "fallback") {
    return "Fallback"
  }
  if (source === "missing_required") {
    return "Manquant requis"
  }
  if (source === "missing_optional") {
    return "Manquant optionnel"
  }
  return source
}

function placeholderPreviewValue(item: AdminResolvedPlaceholder): string {
  if (!item.safe_to_display) {
    return "redacted"
  }
  return item.value_preview ?? ""
}

function renderErrorLeadText(
  inspectionMode: AdminInspectionMode,
  renderErrorKind: string | null | undefined,
): string {
  if (renderErrorKind === "static_preview_incomplete") {
    return "Prévisualisation partielle : certaines substitutions nécessitent des données runtime. "
  }
  if (inspectionMode === "live_execution") {
    return "Erreur détectée pendant l'inspection live. "
  }
  return "Erreur de rendu détectée dans la prévisualisation. "
}

function buildDiffRows(basePrompt: string, nextPrompt: string): DiffRow[] {
  const leftLines = basePrompt.split("\n")
  const rightLines = nextPrompt.split("\n")
  const rowCount = Math.max(leftLines.length, rightLines.length)
  const rows: DiffRow[] = []

  for (let index = 0; index < rowCount; index += 1) {
    const leftText = leftLines[index] ?? ""
    const rightText = rightLines[index] ?? ""
    rows.push({
      leftText,
      rightText,
      leftType: leftText === rightText ? "unchanged" : "removed",
      rightType: leftText === rightText ? "unchanged" : "added",
    })
  }

  return rows
}

export function AdminPromptsPage() {
  const queryClient = useQueryClient()
  const location = useLocation()
  const navigate = useNavigate()
  const { lang } = useAstrologyLabels()
  const tAdmin = useTranslation("admin")
  const tLegacy = tAdmin.promptsLegacy
  const tConsumption = tAdmin.promptsConsumption
  const sub = tAdmin.promptsSubNav
  const activeTab = useMemo(() => resolvePromptsTabFromPath(location.pathname), [location.pathname])
  const consumptionNarrowLayout = useMatchMediaMaxWidth(960, activeTab === "consumption")
  const pageHeader = tAdmin.promptsPageHeader[activeTab]

  const [page, setPage] = useState(1)
  const [pageSize] = useState(25)
  const [search, setSearch] = useState("")
  const [feature, setFeature] = useState("")
  const [subfeature, setSubfeature] = useState("")
  const [plan, setPlan] = useState("")
  const [locale, setLocale] = useState("")
  const [provider, setProvider] = useState("")
  const [sourceOfTruthStatus, setSourceOfTruthStatus] = useState("")
  const [assemblyStatus, setAssemblyStatus] = useState("")
  const [releaseHealthStatus, setReleaseHealthStatus] = useState("")
  const [catalogVisibilityStatus, setCatalogVisibilityStatus] = useState("")
  const [sortBy, setSortBy] = useState("feature")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc")

  const [legacyUseCaseKey, setLegacyUseCaseKey] = useState<string | null>(null)
  const [legacyCompareVersionId, setLegacyCompareVersionId] = useState<string | null>(null)
  const [legacyRollbackCandidate, setLegacyRollbackCandidate] = useState<AdminPromptVersion | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [selectedManifestEntryId, setSelectedManifestEntryId] = useState<string | null>(null)
  const [resolvedInspectionMode, setResolvedInspectionMode] = useState<AdminInspectionMode>("assembly_preview")
  const [selectedSamplePayloadId, setSelectedSamplePayloadId] = useState<string | null>(null)
  const [fromSnapshotId, setFromSnapshotId] = useState<string | null>(null)
  const [toSnapshotId, setToSnapshotId] = useState<string | null>(null)
  const [consumptionView, setConsumptionView] = useState<AdminConsumptionView>("user")
  const [consumptionGranularity, setConsumptionGranularity] = useState<"day" | "month">("day")
  const [consumptionFrom, setConsumptionFrom] = useState("")
  const [consumptionTo, setConsumptionTo] = useState("")
  const [consumptionSearch, setConsumptionSearch] = useState("")
  const [consumptionPage, setConsumptionPage] = useState(1)
  const [consumptionExportError, setConsumptionExportError] = useState<string | null>(null)
  const [selectedDrilldownKey, setSelectedDrilldownKey] = useState<string | null>(null)
  const [samplePayloadsSeed, setSamplePayloadsSeed] = useState<{ feature: string; locale: string } | null>(null)
  const [manualExecuteConfirmOpen, setManualExecuteConfirmOpen] = useState(false)
  const [catalogAdvancedFiltersOpen, setCatalogAdvancedFiltersOpen] = useState(false)
  const consumptionFromUtc = consumptionFrom ? toUtcIsoFromDateTimeInput(consumptionFrom) : undefined
  const consumptionToUtc = consumptionTo ? toUtcIsoFromDateTimeInput(consumptionTo) : undefined

  useEffect(() => {
    setConsumptionExportError(null)
  }, [consumptionView, consumptionGranularity, consumptionFrom, consumptionTo, consumptionSearch])

  // Drill-down : la clé de ligne est stable sur l’axe, pas sur le jeu d’agrégats — vider dès que périmètre ou page change.
  useEffect(() => {
    setSelectedDrilldownKey(null)
  }, [
    consumptionView,
    consumptionGranularity,
    consumptionFrom,
    consumptionTo,
    consumptionSearch,
    consumptionPage,
  ])

  const effectiveSamplePayloadId =
    resolvedInspectionMode === "runtime_preview" ? selectedSamplePayloadId : null

  const catalogQuery = useAdminLlmCatalog(
    {
      page,
      pageSize,
      search: search || undefined,
      feature: feature || undefined,
      subfeature: subfeature || undefined,
      plan: plan || undefined,
      locale: locale || undefined,
      provider: provider || undefined,
      sourceOfTruthStatus: sourceOfTruthStatus || undefined,
      assemblyStatus: assemblyStatus || undefined,
      releaseHealthStatus: releaseHealthStatus || undefined,
      catalogVisibilityStatus: catalogVisibilityStatus || undefined,
      sortBy,
      sortOrder,
    },
    activeTab === "catalog",
  )

  /** Facettes globales (sans filtres catalogue) : l’API les calcule sur la liste complète avant pagination. */
  const samplePayloadsFacetsCatalogQuery = useAdminLlmCatalog(
    { page: 1, pageSize: 25, sortBy: "feature", sortOrder: "asc" },
    activeTab === "samplePayloads",
  )

  const catalogEntries = catalogQuery.data?.data ?? []
  const catalogMeta = catalogQuery.data?.meta
  const selectedCatalogEntry =
    catalogEntries.find((entry) => entry.manifest_entry_id === selectedManifestEntryId) ?? null
  const resolvedQuery = useAdminResolvedAssembly(
    selectedManifestEntryId,
    resolvedInspectionMode,
    effectiveSamplePayloadId,
    activeTab === "catalog" && Boolean(selectedManifestEntryId),
  )

  /** Hors page courante, `selectedCatalogEntry` est null mais le détail résolu porte toujours feature/locale (sample payloads + CTA). */
  const catalogFeatureForSamplePayloads =
    selectedCatalogEntry?.feature ?? resolvedQuery.data?.feature ?? null
  const catalogLocaleForSamplePayloads =
    selectedCatalogEntry?.locale ?? resolvedQuery.data?.locale ?? null

  const manualExecuteMutation = useMutation({
    mutationFn: async () => {
      if (!selectedManifestEntryId || !selectedSamplePayloadId) {
        throw new Error("missing selection")
      }
      return executeAdminCatalogSamplePayload(selectedManifestEntryId, selectedSamplePayloadId)
    },
  })
  const samplePayloadsQuery = useAdminLlmSamplePayloads(
    catalogFeatureForSamplePayloads,
    catalogLocaleForSamplePayloads,
    {
      enabled:
        activeTab === "catalog" &&
        Boolean(selectedManifestEntryId) &&
        resolvedInspectionMode === "runtime_preview",
    },
  )

  useEffect(() => {
    setResolvedInspectionMode("assembly_preview")
    setSelectedSamplePayloadId(null)
  }, [selectedManifestEntryId])

  useEffect(() => {
    if (activeTab !== "samplePayloads") {
      setSamplePayloadsSeed(null)
    }
  }, [activeTab])

  useEffect(() => {
    if (resolvedInspectionMode !== "runtime_preview") {
      setSelectedSamplePayloadId(null)
    }
  }, [resolvedInspectionMode])

  useEffect(() => {
    manualExecuteMutation.reset()
    setManualExecuteConfirmOpen(false)
  }, [selectedManifestEntryId, selectedSamplePayloadId, resolvedInspectionMode])

  useEffect(() => {
    if (resolvedInspectionMode !== "runtime_preview") {
      return
    }
    const data = samplePayloadsQuery.data
    if (!data) {
      return
    }
    const itemIds = new Set(data.items.map((row) => row.id))
    const recommendedId = data.recommended_default_id ?? null

    setSelectedSamplePayloadId((current) => {
      if (current && itemIds.has(current)) {
        return current
      }
      if (recommendedId && itemIds.has(recommendedId)) {
        return recommendedId
      }
      return null
    })
  }, [resolvedInspectionMode, samplePayloadsQuery.data])

  const facets = catalogMeta?.facets
  const availableFeatures = facets?.feature ?? []
  const availableSubfeatures = facets?.subfeature ?? []
  const availablePlans = facets?.plan ?? []
  const availableLocales = facets?.locale ?? []
  const availableProviders = facets?.provider ?? []
  const availableSourceStatuses = facets?.source_of_truth_status ?? []
  const availableAssemblyStatuses = facets?.assembly_status ?? []
  const availableReleaseHealthStatuses = facets?.release_health_status ?? []
  const availableVisibilityStatuses = facets?.catalog_visibility_status ?? []

  const resetCatalogFilters = () => {
    setSearch("")
    setFeature("")
    setSubfeature("")
    setPlan("")
    setLocale("")
    setProvider("")
    setSourceOfTruthStatus("")
    setAssemblyStatus("")
    setReleaseHealthStatus("")
    setCatalogVisibilityStatus("")
    setSortBy("feature")
    setSortOrder("asc")
    setPage(1)
    setCatalogAdvancedFiltersOpen(false)
  }

  const catalogHasActiveFilters = useMemo(
    () =>
      Boolean(
        search.trim() ||
          feature ||
          subfeature ||
          plan ||
          locale ||
          provider ||
          sourceOfTruthStatus ||
          assemblyStatus ||
          releaseHealthStatus ||
          catalogVisibilityStatus,
      ),
    [
      search,
      feature,
      subfeature,
      plan,
      locale,
      provider,
      sourceOfTruthStatus,
      assemblyStatus,
      releaseHealthStatus,
      catalogVisibilityStatus,
    ],
  )

  const useCasesQuery = useAdminLlmUseCases({ enabled: activeTab === "legacy" })
  const useCases = useCasesQuery.data ?? []

  useEffect(() => {
    if (!legacyUseCaseKey && useCases.length > 0) {
      setLegacyUseCaseKey(useCases[0].key)
    }
  }, [legacyUseCaseKey, useCases])

  const legacyHistoryQuery = useAdminPromptHistory(
    legacyUseCaseKey ?? "",
    activeTab === "legacy" && Boolean(legacyUseCaseKey),
  )
  const rollbackMutation = useRollbackPromptVersion()
  const releaseTimelineQuery = useReleaseSnapshotsTimeline(activeTab === "release")
  const releaseTimeline = releaseTimelineQuery.data ?? []
  const releaseSnapshots = Array.from(
    new Map(releaseTimeline.map((item) => [item.snapshot_id, item])).values(),
  )
  const releaseDiffQuery = useReleaseSnapshotDiff(
    fromSnapshotId,
    toSnapshotId,
    activeTab === "release",
  )
  const selectedLegacyHistory = legacyHistoryQuery.data ?? []
  const exportCsvMutation = useDownloadAdminConsumptionCsv()
  const consumptionQuery = useAdminConsumption(
    {
      view: consumptionView,
      granularity: consumptionGranularity,
      fromUtc: consumptionFromUtc,
      toUtc: consumptionToUtc,
      search: consumptionSearch || undefined,
      page: consumptionPage,
      pageSize: 20,
      sortBy: "period_start_utc",
      sortOrder: "desc",
    },
    activeTab === "consumption",
  )
  const selectedConsumptionRow = consumptionQuery.data?.data.find((item) => consumptionRowKey(item) === selectedDrilldownKey)
  const consumptionDrilldownQuery = useAdminConsumptionDrilldown(
    selectedConsumptionRow
      ? {
          view: consumptionView,
          granularity: consumptionGranularity,
          periodStartUtc: selectedConsumptionRow.period_start_utc,
          userId: selectedConsumptionRow.user_id,
          subscriptionPlan: selectedConsumptionRow.subscription_plan,
          feature: selectedConsumptionRow.feature,
          subfeature: selectedConsumptionRow.subfeature,
        }
      : null,
    activeTab === "consumption" && Boolean(selectedConsumptionRow),
  )
  const selectedLegacyUseCase = useCases.find((item) => item.key === legacyUseCaseKey) ?? null
  const apiActiveId = selectedLegacyUseCase?.active_prompt_version_id
  const activeLegacyVersion =
    apiActiveId != null && String(apiActiveId).length > 0
      ? (selectedLegacyHistory.find((item) => item.id === apiActiveId) ?? null)
      : null
  const compareLegacyVersion =
    selectedLegacyHistory.find((item) => item.id === legacyCompareVersionId) ??
    (activeLegacyVersion
      ? selectedLegacyHistory.find((item) => item.id !== activeLegacyVersion.id) ?? null
      : selectedLegacyHistory[0] ?? null)
  const legacyDiffRightVersion: AdminPromptVersion | null = activeLegacyVersion
    ? activeLegacyVersion
    : compareLegacyVersion
      ? selectedLegacyHistory.find((v) => v.id !== compareLegacyVersion.id) ?? null
      : null
  const canShowLegacyDiff = Boolean(
    compareLegacyVersion &&
      legacyDiffRightVersion &&
      compareLegacyVersion.id !== legacyDiffRightVersion.id,
  )
  const legacyDiffRows = canShowLegacyDiff
    ? buildDiffRows(compareLegacyVersion!.developer_prompt, legacyDiffRightVersion!.developer_prompt)
    : []
  const logicGraph = resolvedQuery.data ? buildLogicGraphProjection(resolvedQuery.data) : null

  const isLegacyLoading =
    useCasesQuery.isPending || (activeTab === "legacy" && legacyHistoryQuery.isPending)
  const hasLegacyError = useCasesQuery.isError || legacyHistoryQuery.isError

  useEffect(() => {
    if (selectedLegacyHistory.length === 0) {
      setLegacyCompareVersionId(null)
      return
    }
    const defaultCompareId = activeLegacyVersion
      ? selectedLegacyHistory.find((version) => version.id !== activeLegacyVersion.id)?.id ?? null
      : selectedLegacyHistory[0]?.id ?? null
    if (!selectedLegacyHistory.some((version) => version.id === legacyCompareVersionId)) {
      setLegacyCompareVersionId(defaultCompareId)
    }
  }, [activeLegacyVersion?.id, legacyCompareVersionId, selectedLegacyHistory])

  useEffect(() => {
    if (releaseSnapshots.length < 2) {
      setFromSnapshotId(null)
      setToSnapshotId(null)
      return
    }
    if (!toSnapshotId || !releaseSnapshots.some((item) => item.snapshot_id === toSnapshotId)) {
      setToSnapshotId(releaseSnapshots[0].snapshot_id)
    }
    if (!fromSnapshotId || !releaseSnapshots.some((item) => item.snapshot_id === fromSnapshotId)) {
      setFromSnapshotId(releaseSnapshots[1].snapshot_id)
    }
  }, [fromSnapshotId, releaseSnapshots, toSnapshotId])

  const selectedTimelineById = releaseTimeline.reduce<Record<string, SnapshotTimelineItem>>((acc, item) => {
    acc[item.snapshot_id] = item
    return acc
  }, {})

  const handleLegacyRollback = async () => {
    if (!legacyUseCaseKey || !legacyRollbackCandidate) return
    const restoredShort = legacyRollbackCandidate.id.slice(0, 8)
    await rollbackMutation.mutateAsync({
      useCaseKey: legacyUseCaseKey,
      targetVersionId: legacyRollbackCandidate.id,
    })
    setLegacyRollbackCandidate(null)
    setSuccessMessage(interpolateLegacyTemplate(tLegacy.successRestore, { short: restoredShort }))
    await queryClient.invalidateQueries({ queryKey: ["admin-llm-prompt-history", legacyUseCaseKey] })
    await queryClient.invalidateQueries({ queryKey: ["admin-llm-catalog"] })
  }

  return (
    <div className="admin-prompts-page">
      <header className="admin-page-header">
        <div>
          <h2>{pageHeader.title}</h2>
          <p className="admin-prompts-page__intro">{pageHeader.intro}</p>
        </div>
        <nav className="admin-tabs admin-prompts-subnav" aria-label="Sections prompts">
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/catalog`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.catalog}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/legacy`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.legacy}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/release`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.release}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/consumption`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.consumption}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/personas`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.personas}
          </NavLink>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/sample-payloads`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.sample_payloads}
          </NavLink>
        </nav>
      </header>

      {activeTab === "personas" ? <PersonasAdmin /> : null}

      {activeTab === "samplePayloads" ? (
        <AdminSamplePayloadsAdmin
          seedFeature={samplePayloadsSeed?.feature ?? null}
          seedLocale={samplePayloadsSeed?.locale ?? null}
          catalogFacetsFromParent={{
            facets: samplePayloadsFacetsCatalogQuery.data?.meta?.facets,
            isPending: samplePayloadsFacetsCatalogQuery.isPending,
            isError: samplePayloadsFacetsCatalogQuery.isError,
          }}
        />
      ) : null}

      {activeTab === "catalog" ? (
        <section className="panel admin-prompts-catalog" aria-label="Catalogue canonique">
          <div className="admin-prompts-catalog-master-detail">
            <div className="admin-prompts-catalog__master">
              <div className="admin-prompts-catalog__filters">
                <div className="admin-prompts-catalog__filters-primary">
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-search">Recherche</label>
                    <input
                      id="catalog-search"
                      value={search}
                      onChange={(event) => {
                        setSearch(event.target.value)
                        setPage(1)
                      }}
                      placeholder="Tuple canonique ou manifest_entry_id"
                    />
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-feature">Feature</label>
                    <select
                      id="catalog-feature"
                      value={feature}
                      onChange={(event) => {
                        setFeature(event.target.value)
                        setPage(1)
                      }}
                    >
                      <option value="">Toutes</option>
                      {availableFeatures.map((value) => (
                        <option key={value} value={value}>
                          {value}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-locale">Locale</label>
                    <select
                      id="catalog-locale"
                      value={locale}
                      onChange={(event) => {
                        setLocale(event.target.value)
                        setPage(1)
                      }}
                    >
                      <option value="">Toutes</option>
                      {availableLocales.map((value) => (
                        <option key={value} value={value}>
                          {value}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-provider">Provider</label>
                    <select
                      id="catalog-provider"
                      value={provider}
                      onChange={(event) => {
                        setProvider(event.target.value)
                        setPage(1)
                      }}
                    >
                      <option value="">Tous</option>
                      {availableProviders.map((value) => (
                        <option key={value} value={value}>
                          {value}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-sort">Tri</label>
                    <select
                      id="catalog-sort"
                      aria-label="Tri catalogue"
                      value={sortBy}
                      onChange={(event) => {
                        setSortBy(event.target.value)
                        setPage(1)
                      }}
                    >
                      <option value="feature">Feature</option>
                      <option value="subfeature">Subfeature</option>
                      <option value="plan">Plan</option>
                      <option value="locale">Locale</option>
                      <option value="manifest_entry_id">Manifest entry</option>
                      <option value="provider">Provider</option>
                      <option value="source_of_truth_status">Source of truth</option>
                      <option value="assembly_status">Assembly status</option>
                      <option value="release_health_status">Release health</option>
                      <option value="catalog_visibility_status">Visibility</option>
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-sort-order">Ordre</label>
                    <select
                      id="catalog-sort-order"
                      aria-label="Ordre tri catalogue"
                      value={sortOrder}
                      onChange={(event) => {
                        setSortOrder(event.target.value as "asc" | "desc")
                        setPage(1)
                      }}
                    >
                      <option value="asc">Ascendant</option>
                      <option value="desc">Descendant</option>
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-actions">
                    <button className="text-button" type="button" onClick={resetCatalogFilters}>
                      Réinitialiser les filtres
                    </button>
                  </div>
                </div>
                <div className="admin-prompts-catalog__active-filters" aria-label="Filtres actifs">
                  {catalogHasActiveFilters ? (
                    <ul className="admin-prompts-catalog__active-filters-list">
                      {search.trim() ? <li>Recherche : {search}</li> : null}
                      {feature ? <li>Feature : {feature}</li> : null}
                      {subfeature ? <li>Subfeature : {subfeature}</li> : null}
                      {plan ? <li>Plan : {plan}</li> : null}
                      {locale ? <li>Locale : {locale}</li> : null}
                      {provider ? <li>Provider : {provider}</li> : null}
                      {sourceOfTruthStatus ? <li>Source de vérité : {sourceOfTruthStatus}</li> : null}
                      {assemblyStatus ? <li>Assembly : {assemblyStatus}</li> : null}
                      {releaseHealthStatus ? <li>Release health : {releaseHealthStatus}</li> : null}
                      {catalogVisibilityStatus ? <li>Visibilité : {catalogVisibilityStatus}</li> : null}
                    </ul>
                  ) : (
                    <span className="text-muted">Aucun filtre actif</span>
                  )}
                </div>
                <div className="admin-prompts-catalog__filters-advanced">
                  <button
                    type="button"
                    className="admin-prompts-catalog__filters-advanced-toggle"
                    aria-expanded={catalogAdvancedFiltersOpen}
                    onClick={() => setCatalogAdvancedFiltersOpen((open) => !open)}
                  >
                    Filtres avancés
                  </button>
                  {catalogAdvancedFiltersOpen ? (
                    <div className="admin-prompts-catalog__filters-advanced-panel">
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-subfeature">Subfeature</label>
                        <select
                          id="catalog-subfeature"
                          value={subfeature}
                          onChange={(event) => {
                            setSubfeature(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">Toutes</option>
                          {availableSubfeatures.map((value) => (
                            <option key={value} value={value}>
                              {value}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-plan">Plan</label>
                        <select
                          id="catalog-plan"
                          value={plan}
                          onChange={(event) => {
                            setPlan(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">Tous</option>
                          {availablePlans.map((value) => (
                            <option key={value} value={value}>
                              {value}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-sot">Source de vérité</label>
                        <select
                          id="catalog-sot"
                          value={sourceOfTruthStatus}
                          onChange={(event) => {
                            setSourceOfTruthStatus(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">Toutes</option>
                          {availableSourceStatuses.map((value) => (
                            <option key={value} value={value}>
                              {value}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-assembly">Assembly status</label>
                        <select
                          id="catalog-assembly"
                          value={assemblyStatus}
                          onChange={(event) => {
                            setAssemblyStatus(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">Tous</option>
                          {availableAssemblyStatuses.map((value) => (
                            <option key={value} value={value}>
                              {value}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-rel-health">Release health</label>
                        <select
                          id="catalog-rel-health"
                          value={releaseHealthStatus}
                          onChange={(event) => {
                            setReleaseHealthStatus(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">Tous</option>
                          {availableReleaseHealthStatuses.map((value) => (
                            <option key={value} value={value}>
                              {value}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-vis">Visibilité catalogue</label>
                        <select
                          id="catalog-vis"
                          value={catalogVisibilityStatus}
                          onChange={(event) => {
                            setCatalogVisibilityStatus(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">Toutes</option>
                          {availableVisibilityStatuses.map((value) => (
                            <option key={value} value={value}>
                              {value}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  ) : null}
                </div>
              </div>

          {catalogQuery.isPending ? <div className="loading-placeholder">Chargement du catalogue canonique...</div> : null}
          {catalogQuery.isError ? <p className="chat-error">Impossible de charger le catalogue canonique.</p> : null}

          {!catalogQuery.isPending && !catalogQuery.isError ? (
            <>
              <div className="admin-prompts-catalog__table-wrap">
                <table className="admin-prompts-catalog__table">
                  <thead>
                    <tr>
                      <th>Tuple canonique</th>
                      <th>Snapshot actif</th>
                      <th>Provider / modèle</th>
                      <th>Santé</th>
                      <th className="admin-prompts-catalog__col-action">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {catalogEntries.map((entry) => (
                      <tr
                        key={entry.manifest_entry_id}
                        className={`admin-prompts-catalog__row${entry.manifest_entry_id === selectedManifestEntryId ? " admin-prompts-catalog__row--selected" : ""}`}
                        tabIndex={0}
                        aria-selected={entry.manifest_entry_id === selectedManifestEntryId}
                        onClick={() => setSelectedManifestEntryId(entry.manifest_entry_id)}
                        onKeyDown={(event) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault()
                            setSelectedManifestEntryId(entry.manifest_entry_id)
                          }
                        }}
                      >
                        <td>{entry.feature}/{entry.subfeature ?? "-"}/{entry.plan ?? "-"}/{entry.locale ?? "-"}</td>
                        <td>
                          {entry.active_snapshot_id
                            ? `${entry.active_snapshot_version} (${entry.active_snapshot_id.slice(0, 8)}…)`
                            : "n/a"}
                        </td>
                        <td>
                          {entry.provider ?? "—"} / {entry.model ?? "—"}
                        </td>
                        <td>
                          <span
                            className={`badge ${entry.source_of_truth_status === "active_snapshot" ? "badge--info" : "badge--warning"}`}
                          >
                            {entry.source_of_truth_status}
                          </span>
                          <div className="text-muted">
                            {entry.release_health_status} · signal {entry.runtime_signal_status} · {entry.catalog_visibility_status}
                          </div>
                        </td>
                        <td>
                          <button
                            className="text-button admin-prompts-catalog__inspect"
                            type="button"
                            onClick={(event) => {
                              event.stopPropagation()
                              setSelectedManifestEntryId(entry.manifest_entry_id)
                            }}
                          >
                            Ouvrir le detail
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="admin-prompts-catalog__footer">
                <span>
                  {catalogMeta?.total ?? 0} lignes · fenêtre runtime: {catalogMeta?.freshness_window_minutes ?? "-"} min
                </span>
                <div className="admin-prompts-catalog__pagination">
                  <button className="text-button" type="button" onClick={() => setPage((current) => Math.max(current - 1, 1))} disabled={page <= 1}>
                    Précédent
                  </button>
                  <span>Page {catalogMeta?.page ?? page}</span>
                  <button className="text-button" type="button" onClick={() => setPage((current) => current + 1)} disabled={Boolean(catalogMeta && catalogMeta.page * pageSize >= catalogMeta.total)}>
                    Suivant
                  </button>
                </div>
              </div>
            </>
          ) : null}
            </div>

            <aside className="admin-prompts-catalog__detail-panel" aria-label="Détail catalogue entrée">
              {selectedManifestEntryId ? (
                <>
                  <section className="admin-prompts-catalog-detail-summary" aria-label="Résumé">
                    <h3 className="admin-prompts-catalog-detail-summary__title">Résumé</h3>
                    {selectedCatalogEntry ? (
                      <>
                        <p className="admin-prompts-catalog-detail-summary__tuple">
                          {selectedCatalogEntry.feature}/{selectedCatalogEntry.subfeature ?? "-"}/
                          {selectedCatalogEntry.plan ?? "-"}/{selectedCatalogEntry.locale ?? "-"}
                        </p>
                        <dl className="admin-prompts-catalog-detail-summary__meta">
                          <div>
                            <dt>Manifest entry</dt>
                            <dd>
                              <code>{selectedCatalogEntry.manifest_entry_id}</code>
                            </dd>
                          </div>
                          <div>
                            <dt>Assembly</dt>
                            <dd>
                              {selectedCatalogEntry.assembly_id ?? "—"}{" "}
                              <span className="text-muted">({selectedCatalogEntry.assembly_status})</span>
                            </dd>
                          </div>
                          <div>
                            <dt>Execution profile</dt>
                            <dd>{selectedCatalogEntry.execution_profile_ref ?? "—"}</dd>
                          </div>
                          <div>
                            <dt>Output contract</dt>
                            <dd>{selectedCatalogEntry.output_contract_ref ?? "—"}</dd>
                          </div>
                          <div>
                            <dt>Visibilité catalogue</dt>
                            <dd>{selectedCatalogEntry.catalog_visibility_status}</dd>
                          </div>
                        </dl>
                      </>
                    ) : resolvedQuery.data ? (
                      <>
                        <p className="admin-prompts-catalog-detail-summary__tuple">
                          {resolvedQuery.data.feature}/{resolvedQuery.data.subfeature ?? "-"}/
                          {resolvedQuery.data.plan ?? "-"}/{resolvedQuery.data.locale ?? "-"}
                        </p>
                        <p className="text-muted">
                          Entrée hors page courante du tableau — le résumé ci-dessus provient du détail résolu.
                        </p>
                        <dl className="admin-prompts-catalog-detail-summary__meta">
                          <div>
                            <dt>Manifest entry</dt>
                            <dd>
                              <code>{resolvedQuery.data.manifest_entry_id}</code>
                            </dd>
                          </div>
                          <div>
                            <dt>Assembly</dt>
                            <dd>{resolvedQuery.data.assembly_id ?? "—"}</dd>
                          </div>
                        </dl>
                      </>
                    ) : (
                      <p className="text-muted">
                        Entrée hors page courante — identifiant <code>{selectedManifestEntryId}</code>
                      </p>
                    )}
                  </section>
                <section className="panel admin-prompts-resolved" aria-label="Détail assembly résolue">
                  <div
                    className={`admin-prompts-resolved__surface-banner admin-prompts-resolved__surface-banner--${resolvedInspectionMode}`}
                    role="status"
                    aria-live="polite"
                    aria-label="Mode d'inspection actif pour ce détail"
                  >
                    <span className="admin-prompts-resolved__surface-banner-kicker">Mode d&apos;inspection</span>
                    <span className="admin-prompts-resolved__surface-banner-title">
                      {inspectionModeFullLabel(resolvedInspectionMode)}
                    </span>
                    <span className="admin-prompts-resolved__surface-banner-short">
                      ({inspectionModeShortLabel(resolvedInspectionMode)})
                    </span>
                  </div>
                  <section className="admin-prompts-detail-section" aria-label="Mode d'inspection">
                    <div className="admin-prompts-resolved__header">
                      <h3>Mode d&apos;inspection</h3>
                      <div className="admin-prompts-resolved__header-meta">
                        <code>{selectedManifestEntryId}</code>
                        <span
                          className={`badge ${resolvedQuery.data?.inspection_mode === "assembly_preview" ? "badge--info" : "badge--warning"}`}
                        >
                          Mode: {resolvedQuery.data ? inspectionModeShortLabel(resolvedQuery.data.inspection_mode) : "—"}
                        </span>
                        <label className="admin-prompts-resolved__mode-field">
                          <span className="text-muted">Mode d&apos;inspection</span>
                          <select
                            aria-label="Mode d'inspection du détail"
                            className="admin-prompts-resolved__mode-select"
                            value={resolvedInspectionMode}
                            onChange={(event) => {
                              setResolvedInspectionMode(event.target.value as AdminInspectionMode)
                            }}
                          >
                            {INSPECTION_MODE_OPTIONS.map((opt) => (
                              <option key={opt.value} value={opt.value}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                        </label>
                      </div>
                    </div>
                    <p className="admin-prompts-resolved__render-note">
                      {inspectionModeHelpText(resolvedQuery.data?.inspection_mode ?? resolvedInspectionMode)}
                    </p>
                  </section>
                  <section className="admin-prompts-detail-section" aria-label="État d'exécution">
                    {resolvedInspectionMode === "runtime_preview" && samplePayloadsQuery.isPending ? (
                      <p className="text-muted">Chargement des sample payloads...</p>
                    ) : null}
                    {resolvedQuery.isPending ? <div className="loading-placeholder">Chargement du detail...</div> : null}
                    {resolvedQuery.isError ? <AdminPromptsResolvedAssemblyError error={resolvedQuery.error} /> : null}
                    {resolvedQuery.data ? (
                      <p className="admin-prompts-detail__exec-state text-muted" role="status">
                        État résolu :{" "}
                        <strong>{inspectionModeShortLabel(resolvedQuery.data.inspection_mode)}</strong>
                        {" · "}
                        source {resolvedQuery.data.source_of_truth_status}
                        {resolvedQuery.data.active_snapshot_version
                          ? ` · snapshot ${resolvedQuery.data.active_snapshot_version}`
                          : ""}
                      </p>
                    ) : null}
                  </section>
                  <section className="admin-prompts-detail-section admin-prompts-detail__actions" aria-label="Actions">
                    <div className="admin-prompts-detail__actions-header">
                      <h3 className="admin-prompts-detail__actions-title">Actions</h3>
                      <p className="admin-prompts-detail__actions-risk text-muted">
                        Risque : exécution fournisseur réelle hors trafic nominal — tracée côté serveur, confirmation
                        obligatoire avant envoi.
                      </p>
                    </div>
                    {resolvedInspectionMode === "runtime_preview" ? (
                      <div className="admin-prompts-resolved__manual-exec admin-prompts-resolved__manual-exec--confirmed-surface">
                        <label className="admin-prompts-resolved__mode-field admin-prompts-detail__actions-field">
                          <span className="text-muted">Sample payload (précondition exécution)</span>
                          <select
                            aria-label="Sélecteur sample payload runtime"
                            className="admin-prompts-resolved__mode-select"
                            value={selectedSamplePayloadId ?? ""}
                            onChange={(event) => {
                              setSelectedSamplePayloadId(event.target.value || null)
                            }}
                          >
                            <option value="">Aucun sample payload</option>
                            {(samplePayloadsQuery.data?.items ?? []).map((sample) => (
                              <option key={sample.id} value={sample.id}>
                                {sample.name}
                                {sample.is_default ? " (défaut)" : ""}
                              </option>
                            ))}
                          </select>
                        </label>
                        {catalogFeatureForSamplePayloads && catalogLocaleForSamplePayloads ? (
                          <p className="admin-prompts-resolved__sample-payload-cta">
                            <button
                              type="button"
                              className="text-button"
                              onClick={() => {
                                setSamplePayloadsSeed({
                                  feature: catalogFeatureForSamplePayloads,
                                  locale: catalogLocaleForSamplePayloads,
                                })
                                navigate(`${ADMIN_PROMPTS_BASE}/sample-payloads`)
                              }}
                            >
                              Gérer les sample payloads ({catalogFeatureForSamplePayloads} /{" "}
                              {catalogLocaleForSamplePayloads})
                            </button>
                          </p>
                        ) : null}
                        <button
                          type="button"
                          className="action-button action-button--secondary"
                          disabled={
                            !selectedSamplePayloadId ||
                            !resolvedQuery.data ||
                            !isAdminRuntimePreviewExecutable(resolvedQuery.data) ||
                            manualExecuteMutation.isPending ||
                            resolvedQuery.isPending
                          }
                          onClick={() => setManualExecuteConfirmOpen(true)}
                        >
                          {manualExecuteMutation.isPending ? "Exécution LLM..." : "Exécuter avec le LLM"}
                        </button>
                        {!selectedSamplePayloadId ? (
                          <p className="text-muted admin-prompts-resolved__manual-exec-hint">
                            Sélectionnez un sample payload pour activer l&apos;exécution réelle.
                          </p>
                        ) : null}
                        {selectedSamplePayloadId &&
                        resolvedQuery.data &&
                        !isAdminRuntimePreviewExecutable(resolvedQuery.data) ? (
                          <p
                            className="admin-prompts-resolved__state admin-prompts-resolved__state--warning"
                            role="status"
                          >
                            Prévisualisation runtime incomplète : corrigez les placeholders bloquants ou complétez le
                            sample avant d&apos;exécuter.
                          </p>
                        ) : null}
                        {manualExecuteMutation.isError ? (
                          <div
                            className="admin-prompts-resolved__error admin-prompts-resolved__manual-exec-error"
                            role="alert"
                          >
                            <p className="admin-prompts-resolved__error-primary">
                              {manualExecuteMutation.error instanceof AdminPromptsApiError
                                ? resolvedAssemblyErrorPresentation(manualExecuteMutation.error).primary
                                : "Exécution impossible."}
                            </p>
                            {manualExecuteMutation.error instanceof AdminPromptsApiError &&
                            manualExecutionFailureLead(manualExecuteMutation.error) ? (
                              <p className="admin-prompts-resolved__error-secondary text-muted">
                                {manualExecutionFailureLead(manualExecuteMutation.error)}
                              </p>
                            ) : null}
                          </div>
                        ) : null}
                      </div>
                    ) : (
                      <p className="text-muted admin-prompts-detail__actions-idle">
                        Sélectionnez « Prévisualisation runtime » pour activer les sample payloads et l&apos;exécution LLM
                        depuis cette zone.
                      </p>
                    )}
                  </section>
                  {resolvedQuery.data ? (
                    <>
                      <div className="admin-prompts-resolved__zones">
                        <section className="admin-prompts-resolved__zone" aria-label="Prompts">
                          <h4>Prompts</h4>
                          <p className="text-muted">
                            Source: {resolvedQuery.data.source_of_truth_status} · snapshot:{" "}
                            {resolvedQuery.data.active_snapshot_version ?? "n/a"}
                          </p>
                          <PromptDisclosure summary="assembled prompt">
                            <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.assembled_prompt}</pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary="post injectors prompt">
                            <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.post_injectors_prompt}</pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary="rendered prompt">
                            <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.rendered_prompt}</pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary="system hard policy">
                            <pre className="admin-prompts-code">
                              {String(resolvedQuery.data.resolved_result.provider_messages.system_hard_policy ?? "")}
                            </pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary="developer content">
                            <pre className="admin-prompts-code">
                              {String(resolvedQuery.data.resolved_result.provider_messages.developer_content_rendered ?? "")}
                            </pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary="persona block">
                            <pre className="admin-prompts-code">
                              {String(resolvedQuery.data.resolved_result.provider_messages.persona_block ?? "")}
                            </pre>
                          </PromptDisclosure>
                        </section>
                        <section className="admin-prompts-resolved__zone" aria-label="Placeholders">
                          <h4>Placeholders</h4>
                          <p className="text-muted">
                            Placeholders résolus/partiels pour lecture opérable (sans parser du JSON brut). Les actions
                            sur les sample payloads sont regroupées dans la zone Actions.
                          </p>
                          {resolvedQuery.data.resolved_result.placeholders.length === 0 ? (
                            <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                              Aucun placeholder disponible pour cette cible.
                            </p>
                          ) : (
                            <div className="admin-prompts-resolved__placeholders">
                              {resolvedQuery.data.resolved_result.placeholders.map((item) => (
                                <article key={item.name} className="admin-prompts-resolved__placeholder">
                                  <strong>{item.name}</strong>
                                  <span className={`admin-prompts-resolved__placeholder-status ${placeholderStatusClassName(item.status)}`}>
                                    {placeholderStatusLabel(item.status)}
                                  </span>
                                  <span className="text-muted">{placeholderSourceLabel(item.resolution_source)}</span>
                                  <span className="text-muted">{item.classification ?? "n/a"}</span>
                                  <span className="text-muted">{placeholderRedactionLevelLabel(item)}</span>
                                  <span className="text-muted">{item.reason ?? "n/a"}</span>
                                  <span className="text-muted">{placeholderPreviewValue(item)}</span>
                                </article>
                              ))}
                            </div>
                          )}
                        </section>
                        <section className="admin-prompts-resolved__zone" aria-label="Retour LLM">
                          <h4>Retour LLM</h4>
                          <p className="text-muted">
                            context_quality: {resolvedQuery.data.resolved_result.context_compensation_status}
                          </p>
                          {typeof resolvedQuery.data.resolved_result.provider_messages.render_error === "string" &&
                          resolvedQuery.data.resolved_result.provider_messages.render_error ? (
                            <p
                              role={
                                resolvedQuery.data.resolved_result.provider_messages.render_error_kind ===
                                "static_preview_incomplete"
                                  ? "status"
                                  : "alert"
                              }
                              aria-live={
                                resolvedQuery.data.resolved_result.provider_messages.render_error_kind ===
                                "static_preview_incomplete"
                                  ? "polite"
                                  : "assertive"
                              }
                              className={
                                resolvedQuery.data.resolved_result.provider_messages.render_error_kind ===
                                "static_preview_incomplete"
                                  ? "admin-prompts-resolved__state admin-prompts-resolved__state--warning"
                                  : "admin-prompts-resolved__state admin-prompts-resolved__state--error"
                              }
                            >
                              {renderErrorLeadText(
                                resolvedQuery.data.inspection_mode,
                                resolvedQuery.data.resolved_result.provider_messages.render_error_kind,
                              )}
                              {resolvedQuery.data.resolved_result.provider_messages.render_error}
                            </p>
                          ) : null}
                          <PromptDisclosure summary="Paramètres d'exécution (prévisualisation assembly)">
                            <pre className="admin-prompts-code">
                              {JSON.stringify(resolvedQuery.data.resolved_result.provider_messages.execution_parameters, null, 2)}
                            </pre>
                          </PromptDisclosure>
                          <p className="text-muted">Sortie d&apos;exécution live</p>
                          {resolvedInspectionMode === "runtime_preview" ? (
                            <>
                              {manualExecuteMutation.isPending ? (
                                <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                                  Exécution LLM en cours…
                                </p>
                              ) : null}
                              {manualExecuteMutation.isError ? (
                                <p
                                  className="admin-prompts-resolved__state admin-prompts-resolved__state--error"
                                  role="status"
                                >
                                  L&apos;exécution a échoué — le détail est affiché dans la zone Actions.
                                </p>
                              ) : null}
                              {!manualExecuteMutation.isPending && !manualExecuteMutation.isError ? (
                                manualExecuteMutation.data ? (
                                  <div className="admin-prompts-resolved__llm-return" aria-live="polite">
                                    <dl className="admin-prompts-resolved__llm-meta">
                                      <div>
                                        <dt>Statut validation</dt>
                                        <dd>{manualExecuteMutation.data.validation_status}</dd>
                                      </div>
                                      <div>
                                        <dt>Durée</dt>
                                        <dd>{manualExecuteMutation.data.latency_ms} ms</dd>
                                      </div>
                                      <div>
                                        <dt>Chemin</dt>
                                        <dd>{manualExecuteMutation.data.execution_path}</dd>
                                      </div>
                                      <div>
                                        <dt>Provider / modèle</dt>
                                        <dd>
                                          {manualExecuteMutation.data.provider} · {manualExecuteMutation.data.model}
                                        </dd>
                                      </div>
                                      <div>
                                        <dt>Tokens (in / out)</dt>
                                        <dd>
                                          {manualExecuteMutation.data.usage_input_tokens} /{" "}
                                          {manualExecuteMutation.data.usage_output_tokens}
                                        </dd>
                                      </div>
                                      <div>
                                        <dt>Gateway request</dt>
                                        <dd>
                                          <code>{manualExecuteMutation.data.gateway_request_id}</code>
                                        </dd>
                                      </div>
                                    </dl>
                                    <PromptDisclosure summary="Paramètres runtime résolus (exécution)">
                                      <pre className="admin-prompts-code">
                                        {JSON.stringify(manualExecuteMutation.data.resolved_runtime_parameters, null, 2)}
                                      </pre>
                                    </PromptDisclosure>
                                    <PromptDisclosure summary="Prompt envoyé au fournisseur (anonymisé)">
                                      <pre className="admin-prompts-code">{manualExecuteMutation.data.prompt_sent}</pre>
                                    </PromptDisclosure>
                                    {manualExecuteMutation.data.structured_output_parseable &&
                                    manualExecuteMutation.data.structured_output ? (
                                      <PromptDisclosure summary="Sortie structurée (validée / redaction admin)">
                                        <pre className="admin-prompts-code">
                                          {JSON.stringify(manualExecuteMutation.data.structured_output, null, 2)}
                                        </pre>
                                      </PromptDisclosure>
                                    ) : null}
                                    <PromptDisclosure summary="Réponse brute fournisseur (anonymisée)">
                                      <pre className="admin-prompts-code">{manualExecuteMutation.data.raw_output}</pre>
                                    </PromptDisclosure>
                                    {manualExecuteMutation.data.meta_validation_errors &&
                                    manualExecuteMutation.data.meta_validation_errors.length > 0 ? (
                                      <p
                                        className="admin-prompts-resolved__state admin-prompts-resolved__state--warning"
                                        role="status"
                                      >
                                        Détails validation :{" "}
                                        {manualExecuteMutation.data.meta_validation_errors.join(" · ")}
                                      </p>
                                    ) : null}
                                  </div>
                                ) : manualExecuteMutation.isSuccess ? (
                                  <p
                                    className="admin-prompts-resolved__state admin-prompts-resolved__state--warning"
                                    role="status"
                                    aria-live="polite"
                                  >
                                    Exécution signalée comme réussie mais sans données de retour. Réessayez ou
                                    vérifiez les journaux côté API.
                                  </p>
                                ) : (
                                  <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                                    {selectedSamplePayloadId && resolvedQuery.data &&
                                    isAdminRuntimePreviewExecutable(resolvedQuery.data)
                                      ? "Utilisez la zone Actions (« Exécuter avec le LLM ») pour afficher le retour complet (métadonnées, prompt effectif, sorties)."
                                      : "Sélectionnez un sample payload valide dans la zone Actions puis exécutez pour afficher le retour opérateur."}
                                  </p>
                                )
                              ) : null}
                            </>
                          ) : (
                            <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                              Passez en prévisualisation runtime pour exécuter le fournisseur et afficher ici le retour
                              complet.
                            </p>
                          )}
                        </section>
                        <section className="admin-prompts-resolved__zone" aria-label="Graphe logique">
                          <h4>Graphe logique</h4>
                          <p className="text-muted">
                            Chaîne inspectable : schéma interactif (zoom / déplacement) avec secours texte. Sources de
                            composition, pipeline, messages fournisseur et données runtime.
                          </p>
                          <AdminPromptsLogicGraph projection={logicGraph} />
                          <details className="admin-prompts-detail__disclosure admin-prompts-detail__disclosure--sources">
                            <summary className="admin-prompts-detail__disclosure-summary">
                              Sources de composition (texte intégral)
                            </summary>
                            <div className="admin-prompts-detail__disclosure-body">
                              <pre className="admin-prompts-code">{resolvedQuery.data.composition_sources.feature_template.content}</pre>
                              {resolvedQuery.data.composition_sources.subfeature_template ? (
                                <pre className="admin-prompts-code">{resolvedQuery.data.composition_sources.subfeature_template.content}</pre>
                              ) : null}
                              {resolvedQuery.data.composition_sources.plan_rules?.content ? (
                                <pre className="admin-prompts-code">{resolvedQuery.data.composition_sources.plan_rules.content}</pre>
                              ) : null}
                              {resolvedQuery.data.composition_sources.persona_block?.content ? (
                                <pre className="admin-prompts-code">{resolvedQuery.data.composition_sources.persona_block.content}</pre>
                              ) : null}
                              <pre className="admin-prompts-code">{resolvedQuery.data.composition_sources.hard_policy.content}</pre>
                              <div className="admin-prompts-resolved__meta-grid">
                                <span className="text-muted">Execution profile</span>
                                <span>
                                  {resolvedQuery.data.composition_sources.execution_profile.provider} /{" "}
                                  {resolvedQuery.data.composition_sources.execution_profile.model}
                                </span>
                                <span className="text-muted">Reasoning</span>
                                <span>{resolvedQuery.data.composition_sources.execution_profile.reasoning ?? "n/a"}</span>
                                <span className="text-muted">Verbosity</span>
                                <span>{resolvedQuery.data.composition_sources.execution_profile.verbosity ?? "n/a"}</span>
                              </div>
                            </div>
                          </details>
                        </section>
                      </div>
                    </>
                  ) : null}
                </section>
                </>
              ) : (
                <div className="admin-prompts-catalog__detail-empty">
                  <p className="text-muted">
                    Sélectionnez une ligne du catalogue pour afficher le détail résolu.
                  </p>
                </div>
              )}
            </aside>
          </div>
        </section>
      ) : null}

      {activeTab === "consumption" ? (
        <section className="panel admin-prompts-consumption" aria-label={tConsumption.regionAriaLabel}>
          <div className="admin-prompts-consumption__surface">
            <header className="admin-prompts-consumption__surface-header">
              <p className="admin-prompts-consumption__kicker">{tConsumption.kicker}</p>
              <h3 className="admin-prompts-consumption__surface-title">{tConsumption.surfaceTitle}</h3>
              <p className="admin-prompts-consumption__surface-intro text-muted">{tConsumption.surfaceIntro}</p>
            </header>

            <div className="admin-prompts-consumption__toolbar" role="toolbar" aria-label={tConsumption.toolbarAria}>
              <div className="admin-prompts-consumption__toolbar-group">
                <p className="admin-prompts-consumption__toolbar-group-title">{tConsumption.groupAxis}</p>
                <div className="admin-prompts-consumption__toolbar-fields">
                  <label className="admin-prompts-consumption__field">
                    <span>{tConsumption.viewLabel}</span>
                    <select
                      aria-label={tConsumption.viewAria}
                      value={consumptionView}
                      onChange={(event) => {
                        setConsumptionView(event.target.value as AdminConsumptionView)
                        setConsumptionPage(1)
                      }}
                    >
                      <option value="user">{tConsumption.viewOptionUser}</option>
                      <option value="subscription">{tConsumption.viewOptionSubscription}</option>
                      <option value="feature">{tConsumption.viewOptionFeature}</option>
                    </select>
                  </label>
                  <label className="admin-prompts-consumption__field">
                    <span>{tConsumption.granularityLabel}</span>
                    <select
                      aria-label={tConsumption.granularityAria}
                      value={consumptionGranularity}
                      onChange={(event) => {
                        setConsumptionGranularity(event.target.value as "day" | "month")
                        setConsumptionPage(1)
                      }}
                    >
                      <option value="day">{tConsumption.granularityOptionDay}</option>
                      <option value="month">{tConsumption.granularityOptionMonth}</option>
                    </select>
                  </label>
                </div>
              </div>
              <div className="admin-prompts-consumption__toolbar-group">
                <p className="admin-prompts-consumption__toolbar-group-title">{tConsumption.groupPeriod}</p>
                <div className="admin-prompts-consumption__toolbar-fields admin-prompts-consumption__toolbar-fields--period">
                  <label className="admin-prompts-consumption__field">
                    <span>{tConsumption.periodFromLabel}</span>
                    <input
                      type="datetime-local"
                      value={consumptionFrom}
                      onChange={(event) => {
                        setConsumptionFrom(event.target.value)
                        setConsumptionPage(1)
                      }}
                    />
                  </label>
                  <label className="admin-prompts-consumption__field">
                    <span>{tConsumption.periodToLabel}</span>
                    <input
                      type="datetime-local"
                      value={consumptionTo}
                      onChange={(event) => {
                        setConsumptionTo(event.target.value)
                        setConsumptionPage(1)
                      }}
                    />
                  </label>
                </div>
              </div>
              <div className="admin-prompts-consumption__toolbar-group admin-prompts-consumption__toolbar-group--refine">
                <p className="admin-prompts-consumption__toolbar-group-title">{tConsumption.groupRefine}</p>
                <div className="admin-prompts-consumption__toolbar-fields admin-prompts-consumption__toolbar-fields--refine">
                  <label className="admin-prompts-consumption__field admin-prompts-consumption__field--grow">
                    <span>{tConsumption.searchLabel}</span>
                    <input
                      value={consumptionSearch}
                      onChange={(event) => {
                        setConsumptionSearch(event.target.value)
                        setConsumptionPage(1)
                      }}
                      placeholder={tConsumption.searchPlaceholder}
                    />
                  </label>
                  <button
                    className="action-button action-button--secondary"
                    type="button"
                    onClick={async () => {
                      setConsumptionExportError(null)
                      try {
                        const blob = await exportCsvMutation.mutateAsync({
                          view: consumptionView,
                          granularity: consumptionGranularity,
                          fromUtc: consumptionFromUtc,
                          toUtc: consumptionToUtc,
                          search: consumptionSearch || undefined,
                        })
                        const url = URL.createObjectURL(blob)
                        const link = document.createElement("a")
                        link.href = url
                        link.download = `llm-consumption-${consumptionView}-${consumptionGranularity}.csv`
                        link.click()
                        window.setTimeout(() => {
                          URL.revokeObjectURL(url)
                        }, 30_000)
                      } catch (error: unknown) {
                        setConsumptionExportError(
                          error instanceof AdminPromptsApiError
                            ? error.message
                            : error instanceof Error
                              ? error.message
                              : tConsumption.errorExportCsv,
                        )
                      }
                    }}
                    disabled={exportCsvMutation.isPending}
                  >
                    {exportCsvMutation.isPending ? tConsumption.exportCsvPending : tConsumption.exportCsv}
                  </button>
                </div>
              </div>
            </div>

            {consumptionExportError ? (
              <p className="chat-error" role="alert">
                {consumptionExportError}
              </p>
            ) : null}

            <p className="admin-prompts-consumption__granularity-hint text-muted">
              {tConsumption.granularityHint(consumptionGranularity)}
            </p>

            {consumptionQuery.isPending ? (
              <div className="loading-placeholder" role="status" aria-live="polite">
                {tConsumption.loadingAggregates}
              </div>
            ) : null}
            {consumptionQuery.isError ? <p className="chat-error">{tConsumption.errorAggregates}</p> : null}

            {consumptionQuery.data ? (
              <div className="admin-prompts-consumption__body">
                <section
                  className="admin-prompts-consumption__aggregates"
                  aria-labelledby="consumption-aggregates-heading"
                >
                  <div className="admin-prompts-consumption__section-head">
                    <h4 id="consumption-aggregates-heading" className="admin-prompts-consumption__section-heading">
                      {tConsumption.aggregatesHeading}
                    </h4>
                    <p className="admin-prompts-consumption__section-hint text-muted">{tConsumption.aggregatesHint}</p>
                  </div>

                  {consumptionQuery.data.data.length === 0 ? (
                    <p className="admin-prompts-consumption__empty text-muted" role="status">
                      {tConsumption.emptyAggregates}
                    </p>
                  ) : consumptionNarrowLayout ? (
                    <div className="admin-prompts-consumption__cards-mobile" role="list">
                      {consumptionQuery.data.data.map((row) => {
                        const rowKey = consumptionRowKey(row)
                        const axisLabel = formatConsumptionAxisLabel(consumptionView, row)
                        const periodLabel = new Date(row.period_start_utc).toLocaleString()
                        return (
                          <article key={rowKey} className="admin-prompts-consumption__row-card" role="listitem">
                            <div className="admin-prompts-consumption__row-card-head">
                              <span className="admin-prompts-consumption__row-card-label">{tConsumption.tablePeriod}</span>
                              <span className="admin-prompts-consumption__row-card-value">{periodLabel}</span>
                            </div>
                            <div className="admin-prompts-consumption__row-card-head">
                              <span className="admin-prompts-consumption__row-card-label">{tConsumption.tableAxis}</span>
                              <span className="admin-prompts-consumption__row-card-value">{axisLabel}</span>
                            </div>
                            <dl className="admin-prompts-consumption__row-card-stats">
                              <div>
                                <dt>{tConsumption.tableRequests}</dt>
                                <dd>{row.request_count}</dd>
                              </div>
                              <div>
                                <dt>{tConsumption.tableTokens}</dt>
                                <dd>
                                  {row.input_tokens} / {row.output_tokens} / {row.total_tokens}
                                </dd>
                              </div>
                              <div>
                                <dt>{tConsumption.tableCost}</dt>
                                <dd>{row.estimated_cost.toFixed(4)} $</dd>
                              </div>
                              <div>
                                <dt>{tConsumption.tableLatency}</dt>
                                <dd>{row.avg_latency_ms.toFixed(1)} ms</dd>
                              </div>
                              <div>
                                <dt>{tConsumption.tableErrorRate}</dt>
                                <dd>{(row.error_rate * 100).toFixed(2)}%</dd>
                              </div>
                            </dl>
                            <button className="text-button" type="button" onClick={() => setSelectedDrilldownKey(rowKey)}>
                              {tConsumption.viewLogsButton}
                            </button>
                          </article>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="admin-prompts-consumption__table-desktop">
                      <div className="admin-prompts-consumption__table-wrap">
                        <table className="admin-prompts-consumption__table">
                          <thead>
                            <tr>
                              <th>{tConsumption.tablePeriod}</th>
                              <th>{tConsumption.tableAxis}</th>
                              <th>{tConsumption.tableRequests}</th>
                              <th>{tConsumption.tableTokens}</th>
                              <th>{tConsumption.tableCost}</th>
                              <th>{tConsumption.tableLatency}</th>
                              <th>{tConsumption.tableErrorRate}</th>
                              <th>{tConsumption.tableActions}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {consumptionQuery.data.data.map((row) => {
                              const rowKey = consumptionRowKey(row)
                              const axisLabel = formatConsumptionAxisLabel(consumptionView, row)
                              return (
                                <tr key={rowKey}>
                                  <td>{new Date(row.period_start_utc).toLocaleString()}</td>
                                  <td>{axisLabel}</td>
                                  <td>{row.request_count}</td>
                                  <td>
                                    {row.input_tokens} / {row.output_tokens} / {row.total_tokens}
                                  </td>
                                  <td>{row.estimated_cost.toFixed(4)} $</td>
                                  <td>{row.avg_latency_ms.toFixed(1)} ms</td>
                                  <td>{(row.error_rate * 100).toFixed(2)}%</td>
                                  <td>
                                    <button className="text-button" type="button" onClick={() => setSelectedDrilldownKey(rowKey)}>
                                      {tConsumption.viewLogsButton}
                                    </button>
                                  </td>
                                </tr>
                              )
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  <footer className="admin-prompts-consumption__footer">
                    <span>{tConsumption.rowLines(consumptionQuery.data.meta.count)}</span>
                    <div className="admin-prompts-consumption__pagination">
                      <button
                        className="text-button"
                        type="button"
                        onClick={() => setConsumptionPage((value) => Math.max(1, value - 1))}
                        disabled={consumptionPage <= 1}
                      >
                        {tConsumption.prevPage}
                      </button>
                      <span>{tConsumption.pageLabel(consumptionQuery.data.meta.page)}</span>
                      <button
                        className="text-button"
                        type="button"
                        onClick={() => setConsumptionPage((value) => value + 1)}
                        disabled={
                          consumptionQuery.data.meta.page * consumptionQuery.data.meta.page_size >=
                          consumptionQuery.data.meta.count
                        }
                      >
                        {tConsumption.nextPage}
                      </button>
                    </div>
                  </footer>
                </section>

                {selectedConsumptionRow ? (
                  <aside
                    className="admin-prompts-consumption__investigation"
                    aria-labelledby="consumption-drill-heading"
                  >
                    <div className="admin-prompts-consumption__investigation-head">
                      <h4 id="consumption-drill-heading" className="admin-prompts-consumption__investigation-title">
                        {tConsumption.drilldownHeading}
                      </h4>
                      <p className="admin-prompts-consumption__investigation-lead text-muted">{tConsumption.drilldownLead}</p>
                      <p className="admin-prompts-consumption__investigation-context" role="status">
                        {tConsumption.selectedRowSummary(
                          new Date(selectedConsumptionRow.period_start_utc).toLocaleString(),
                          formatConsumptionAxisLabel(consumptionView, selectedConsumptionRow),
                        )}
                      </p>
                    </div>
                    {consumptionDrilldownQuery.isPending ? (
                      <div className="loading-placeholder" role="status" aria-live="polite">
                        {tConsumption.loadingDrilldown}
                      </div>
                    ) : null}
                    {consumptionDrilldownQuery.isError ? (
                      <p className="chat-error">{tConsumption.errorDrilldown}</p>
                    ) : null}
                    {consumptionDrilldownQuery.data ? (
                      <div className="admin-prompts-consumption__drill-table-wrap">
                        <table className="admin-prompts-consumption__drill-table">
                          <thead>
                            <tr>
                              <th>{tConsumption.drillTableTimestamp}</th>
                              <th>{tConsumption.drillTableRequestId}</th>
                              <th>{tConsumption.drillTableFeature}</th>
                              <th>{tConsumption.drillTableProvider}</th>
                              <th>{tConsumption.drillTableSnapshot}</th>
                              <th>{tConsumption.drillTableValidation}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {consumptionDrilldownQuery.data.data.map((item) => (
                              <tr key={`${item.request_id}-${item.timestamp}`}>
                                <td>{new Date(item.timestamp).toLocaleString()}</td>
                                <td>
                                  <code>{item.request_id}</code>
                                </td>
                                <td>
                                  {item.feature ?? "unknown"} / {item.subfeature ?? "-"}
                                </td>
                                <td>{item.provider ?? "unknown"}</td>
                                <td>{item.active_snapshot_version ?? item.manifest_entry_id ?? "n/a"}</td>
                                <td>{item.validation_status}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : null}
                  </aside>
                ) : null}
              </div>
            ) : null}
          </div>
        </section>
      ) : null}

      {activeTab === "legacy" ? (
        <section className="panel admin-prompts-legacy" aria-label={tLegacy.regionAriaLabel}>
          {successMessage ? (
            <p className="state-line state-success" role="status" aria-live="polite">
              {successMessage}
            </p>
          ) : null}
          {isLegacyLoading ? <div className="loading-placeholder">{tLegacy.loadingHistory}</div> : null}
          {hasLegacyError ? <p className="chat-error">{tLegacy.errorHistory}</p> : null}

          {!isLegacyLoading && !hasLegacyError ? (
            <div className="admin-prompts-legacy__surface">
              <header className="admin-prompts-legacy__surface-header">
                <p className="admin-prompts-legacy__kicker">{tLegacy.kicker}</p>
                <h3 className="admin-prompts-legacy__surface-title">{tLegacy.surfaceTitle}</h3>
                <p className="admin-prompts-legacy__surface-intro text-muted">{tLegacy.surfaceIntro}</p>
              </header>

              <div className="admin-prompts-legacy__toolbar">
                <label className="admin-prompts-compare admin-prompts-legacy__field">
                  <span>{tLegacy.toolbarLabel}</span>
                  <select
                    aria-label={tLegacy.useCaseSelectAria}
                    value={legacyUseCaseKey ?? ""}
                    onChange={(event) => setLegacyUseCaseKey(event.target.value)}
                  >
                    {useCases.map((useCase) => (
                      <option key={useCase.key} value={useCase.key}>
                        {useCase.display_name} · {useCase.key}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              {selectedLegacyHistory.length === 0 ? (
                <p className="admin-prompts-legacy__empty text-muted" role="status">
                  {tLegacy.emptyVersions}
                </p>
              ) : (
                <>
                  <section className="admin-prompts-legacy__versions" aria-labelledby="legacy-versions-heading">
                    <div className="admin-prompts-legacy__section-head">
                      <h4 id="legacy-versions-heading" className="admin-prompts-legacy__section-heading">
                        {tLegacy.versionsHeading}
                      </h4>
                      <p className="admin-prompts-legacy__section-hint text-muted">
                        {activeLegacyVersion ? tLegacy.versionsHintActiveKnown : tLegacy.versionsHintActiveUnknown}
                      </p>
                    </div>
                    <div className="admin-prompts-history admin-prompts-legacy__version-list">
                      {selectedLegacyHistory.map((version) => {
                        const isResolvedActiveRow =
                          activeLegacyVersion !== null && version.id === activeLegacyVersion.id
                        return (
                          <article key={version.id} className="admin-prompts-history__item admin-prompts-legacy__version-row">
                            <div>
                              <div className="admin-prompts-history__topline">
                                <span
                                  className={`badge ${version.status === "published" ? "badge--info" : "badge--warning"}`}
                                >
                                  {legacyPromptStatusLabel(version.status, tLegacy)}
                                </span>
                                {isResolvedActiveRow ? (
                                  <span className="admin-prompts-legacy__pill admin-prompts-legacy__pill--active">
                                    {tLegacy.badgeInProduction}
                                  </span>
                                ) : null}
                                <span className="text-muted">{version.model}</span>
                              </div>
                              <p className="admin-prompts-history__copy">
                                {tLegacy.authorLine(
                                  version.created_by,
                                  formatLegacyPromptTimestamp(version.created_at, lang),
                                )}
                              </p>
                              <code>{version.id}</code>
                            </div>
                            <div className="admin-prompts-history__actions admin-prompts-legacy__version-actions">
                              {isResolvedActiveRow ? (
                                <span className="admin-prompts-legacy__action-placeholder text-muted">
                                  {tLegacy.alreadyActiveHint}
                                </span>
                              ) : (
                                <button
                                  className="action-button action-button--secondary"
                                  type="button"
                                  onClick={() => setLegacyRollbackCandidate(version)}
                                >
                                  {tLegacy.restoreThisVersion}
                                </button>
                              )}
                            </div>
                          </article>
                        )
                      })}
                    </div>
                  </section>

                  {canShowLegacyDiff && compareLegacyVersion && legacyDiffRightVersion ? (
                    <section
                      className="admin-prompts-legacy__diff panel"
                      aria-labelledby="legacy-diff-heading"
                    >
                      <div className="admin-prompts-legacy__diff-head">
                        <div>
                          <h4 id="legacy-diff-heading" className="admin-prompts-legacy__section-heading">
                            {tLegacy.diffHeading}
                          </h4>
                          <p className="admin-prompts-legacy__diff-lead text-muted">
                            {activeLegacyVersion ? tLegacy.diffLeadActiveKnown : tLegacy.diffLeadActiveUnknown}
                          </p>
                        </div>
                        <label className="admin-prompts-compare admin-prompts-legacy__field admin-prompts-legacy__field--inline">
                          <span>{tLegacy.refVersionLabel}</span>
                          <select
                            aria-label={tLegacy.refSelectAria}
                            value={compareLegacyVersion.id}
                            onChange={(event) => setLegacyCompareVersionId(event.target.value)}
                          >
                            {selectedLegacyHistory
                              .filter((version) =>
                                activeLegacyVersion ? version.id !== activeLegacyVersion.id : true,
                              )
                              .map((version) => (
                                <option key={version.id} value={version.id}>
                                  {version.id.slice(0, 8)}… · {legacyPromptStatusLabel(version.status, tLegacy)}
                                </option>
                              ))}
                          </select>
                        </label>
                      </div>

                      <div
                        className="admin-prompts-diff admin-prompts-legacy__diff-grid"
                        role="group"
                        aria-label={tLegacy.diffGroupAria}
                      >
                        <div className="admin-prompts-diff__column admin-prompts-diff__column--left">
                          <h4 className="admin-prompts-legacy__diff-column-title" id="legacy-diff-left-title">
                            {tLegacy.refColumnTitle}
                          </h4>
                          <LegacyVersionMetaStrip
                            version={compareLegacyVersion}
                            headingId="legacy-diff-left-title"
                            variant="reference"
                            legacy={tLegacy}
                            lang={lang}
                          />
                          <p className="admin-prompts-legacy__diff-caption text-muted">
                            {tLegacy.contentComparedCaption}
                          </p>
                          {legacyDiffRows.map((row, index) => (
                            <code
                              key={`legacy-left-${index}`}
                              className={`admin-prompts-diff__line admin-prompts-diff__line--${row.leftType}`}
                            >
                              {row.leftText || " "}
                            </code>
                          ))}
                        </div>
                        <div className="admin-prompts-diff__column">
                          <h4 className="admin-prompts-legacy__diff-column-title" id="legacy-diff-right-title">
                            {activeLegacyVersion ? tLegacy.rightColumnTitleProduction : tLegacy.rightColumnTitlePeer}
                          </h4>
                          <LegacyVersionMetaStrip
                            version={legacyDiffRightVersion}
                            headingId="legacy-diff-right-title"
                            variant={activeLegacyVersion ? "active" : "peer"}
                            legacy={tLegacy}
                            lang={lang}
                          />
                          <p className="admin-prompts-legacy__diff-caption text-muted">
                            {tLegacy.contentComparedCaption}
                          </p>
                          {legacyDiffRows.map((row, index) => (
                            <code
                              key={`legacy-right-${index}`}
                              className={`admin-prompts-diff__line admin-prompts-diff__line--${row.rightType}`}
                            >
                              {row.rightText || " "}
                            </code>
                          ))}
                        </div>
                      </div>
                    </section>
                  ) : null}
                </>
              )}
            </div>
          ) : null}
        </section>
      ) : null}

      {activeTab === "release" ? (
        <section className="panel admin-prompts-release" aria-label="Investigation release snapshots">
          {releaseTimelineQuery.isPending ? <div className="loading-placeholder">Chargement de la timeline release...</div> : null}
          {releaseTimelineQuery.isError ? <p className="chat-error">Impossible de charger la timeline release.</p> : null}
          {!releaseTimelineQuery.isPending && !releaseTimelineQuery.isError && releaseTimeline.length === 0 ? (
            <div className="state-line">Aucun snapshot disponible.</div>
          ) : null}
          {!releaseTimelineQuery.isPending && !releaseTimelineQuery.isError && releaseTimeline.length > 0 ? (
            <div className="admin-prompts-release__surface">
              <header className="admin-prompts-release__surface-header">
                <p className="admin-prompts-release__kicker">Investigation release</p>
                <h3 className="admin-prompts-release__surface-title">Timeline et comparaison de snapshots</h3>
                <p className="admin-prompts-release__surface-intro text-muted">
                  Lire l&apos;état courant et l&apos;historique, qualifier le snapshot via les preuves, puis comparer deux versions avant
                  d&apos;ouvrir une entrée canonique dans le catalogue.
                </p>
              </header>

              <section className="admin-prompts-release__section" aria-labelledby="release-timeline-heading">
                <div className="admin-prompts-release__section-head">
                  <h4 id="release-timeline-heading" className="admin-prompts-release__section-heading">
                    Chronologie des événements
                  </h4>
                  <p className="admin-prompts-release__section-hint text-muted">
                    Chaque carte regroupe statut release, motif, rollback éventuel et preuves corrélées au snapshot.
                  </p>
                </div>
                <div className="admin-prompts-release__timeline">
                  {releaseTimeline.map((item) => (
                    <article key={`${item.snapshot_id}-${item.occurred_at}`} className="admin-prompts-release__timeline-item">
                      <div className="admin-prompts-release__timeline-top">
                        <strong>{item.snapshot_version}</strong>
                        <span
                          className={`badge ${item.release_health_status === "degraded" || item.release_health_status === "rollback_recommended" ? "badge--warning" : "badge--info"}`}
                        >
                          {item.release_health_status}
                        </span>
                      </div>
                      <p className="text-muted">
                        Événement : {item.event_type} · {new Date(item.occurred_at).toLocaleString()} ·{" "}
                        {item.manifest_entry_count} entrée(s) manifeste
                      </p>
                      <p className="text-muted">
                        État courant : {item.current_status} · transitions enregistrées : {item.status_history.length}
                      </p>
                      {item.from_snapshot_id ? (
                        <p className="text-muted">
                          Rollback : {formatReleaseSnapshotIdShort(item.from_snapshot_id)} →{" "}
                          {item.to_snapshot_id ? formatReleaseSnapshotIdShort(item.to_snapshot_id) : "—"}
                        </p>
                      ) : null}
                      {item.reason ? (
                        <p className="text-muted">
                          <span className="admin-prompts-release__reason-label">Motif : </span>
                          {item.reason}
                        </p>
                      ) : null}
                      <div className="admin-prompts-release__proofs-block">
                        <p className="admin-prompts-release__proofs-lead text-muted">Preuves qualité (corrélation snapshot)</p>
                        <div className="admin-prompts-release__proofs">
                          {item.proof_summaries.map((proof) => (
                            <span
                              key={`${item.snapshot_id}-${proof.proof_type}`}
                              className={`badge ${proof.status === "missing" || proof.verdict === "uncorrelated" ? "badge--warning" : "badge--info"}`}
                            >
                              {proof.proof_type}: {proof.verdict ?? proof.status}
                            </span>
                          ))}
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </section>

              <section className="admin-prompts-release__section" aria-labelledby="release-compare-heading">
                <div className="admin-prompts-release__section-head">
                  <h4 id="release-compare-heading" className="admin-prompts-release__section-heading">
                    Comparer deux snapshots
                  </h4>
                  <p className="admin-prompts-release__section-hint text-muted">
                    Choisissez la référence (source) et la version comparée (cible). Le tableau ci-dessous synthétise les écarts par axe
                    technique.
                  </p>
                </div>
                <div className="admin-prompts-release__diff-controls">
                  <label className="admin-prompts-compare">
                    <span>Snapshot source (référence)</span>
                    <select value={fromSnapshotId ?? ""} onChange={(event) => setFromSnapshotId(event.target.value)}>
                      {releaseSnapshots.map((item) => (
                        <option key={`from-${item.snapshot_id}`} value={item.snapshot_id}>
                          {item.snapshot_version} ({item.snapshot_id.slice(0, 8)})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="admin-prompts-compare">
                    <span>Snapshot cible (comparée)</span>
                    <select value={toSnapshotId ?? ""} onChange={(event) => setToSnapshotId(event.target.value)}>
                      {releaseSnapshots.map((item) => (
                        <option key={`to-${item.snapshot_id}`} value={item.snapshot_id}>
                          {item.snapshot_version} ({item.snapshot_id.slice(0, 8)})
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              </section>

              {releaseDiffQuery.isPending ? <div className="loading-placeholder">Chargement du diff snapshots...</div> : null}
              {releaseDiffQuery.isError ? <p className="chat-error">Impossible de charger le diff snapshots.</p> : null}
              {releaseDiffQuery.data ? (
                <div className="admin-prompts-release__diff panel">
                  <h3 className="admin-prompts-release__diff-title">Synthèse de comparaison</h3>
                  <div className="admin-prompts-release__compare-banner" aria-label="Versions comparées pour ce diff">
                    <div className="admin-prompts-release__compare-card">
                      <span className="admin-prompts-release__compare-role">Référence (source)</span>
                      <strong>
                        {selectedTimelineById[releaseDiffQuery.data.from_snapshot_id]?.snapshot_version ??
                          releaseDiffQuery.data.from_snapshot_id}
                      </strong>
                      <code className="admin-prompts-release__compare-id">
                        {formatReleaseSnapshotIdShort(releaseDiffQuery.data.from_snapshot_id)}
                      </code>
                    </div>
                    <span className="admin-prompts-release__compare-arrow" aria-hidden>
                      →
                    </span>
                    <div className="admin-prompts-release__compare-card">
                      <span className="admin-prompts-release__compare-role">Comparée (cible)</span>
                      <strong>
                        {selectedTimelineById[releaseDiffQuery.data.to_snapshot_id]?.snapshot_version ??
                          releaseDiffQuery.data.to_snapshot_id}
                      </strong>
                      <code className="admin-prompts-release__compare-id">
                        {formatReleaseSnapshotIdShort(releaseDiffQuery.data.to_snapshot_id)}
                      </code>
                    </div>
                  </div>
                  <h4 className="admin-prompts-release__diff-table-heading">Écarts par entrée canonique</h4>
                  <p className="admin-prompts-release__diff-table-lead text-muted">
                    Assembly, profil d&apos;exécution et contrat de sortie : état synthétique avant d&apos;ouvrir le détail catalogue.
                  </p>
                  <div className="admin-prompts-catalog__table-wrap">
                    <table className="admin-prompts-catalog__table">
                      <thead>
                        <tr>
                          <th>Entrée manifeste</th>
                          <th>Portée du changement</th>
                          <th>Assembly</th>
                          <th>Profil d&apos;exécution</th>
                          <th>Contrat de sortie</th>
                          <th>Catalogue</th>
                        </tr>
                      </thead>
                      <tbody>
                        {releaseDiffQuery.data.entries.map((entry) => (
                          <tr key={`diff-${entry.manifest_entry_id}`}>
                            <td>
                              <code>{entry.manifest_entry_id}</code>
                            </td>
                            <td>{releaseDiffCategoryLabel(entry.category)}</td>
                            <td>
                              <span className={releaseDiffAxisBadgeClass(entry.assembly_changed)}>
                                {entry.assembly_changed ? "Modifié" : "Inchangé"}
                              </span>
                            </td>
                            <td>
                              <span className={releaseDiffAxisBadgeClass(entry.execution_profile_changed)}>
                                {entry.execution_profile_changed ? "Modifié" : "Inchangé"}
                              </span>
                            </td>
                            <td>
                              <span className={releaseDiffAxisBadgeClass(entry.output_contract_changed)}>
                                {entry.output_contract_changed ? "Modifié" : "Inchangé"}
                              </span>
                            </td>
                            <td>
                              <button
                                className="text-button admin-prompts-catalog__inspect admin-prompts-release__catalog-link"
                                type="button"
                                aria-label={`Ouvrir l'entrée canonique ${entry.manifest_entry_id} dans le catalogue`}
                                onClick={() => {
                                  navigate(`${ADMIN_PROMPTS_BASE}/catalog`)
                                  setSelectedManifestEntryId(entry.manifest_entry_id)
                                }}
                              >
                                <span className="admin-prompts-release__catalog-link-title">Ouvrir dans le catalogue</span>
                                <span className="admin-prompts-release__catalog-link-hint text-muted">
                                  <code>{formatManifestEntryCatalogHint(entry.manifest_entry_id)}</code>
                                </span>
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}
        </section>
      ) : null}

      {legacyRollbackCandidate && legacyUseCaseKey ? (
        <LegacyRollbackModal
          isPending={rollbackMutation.isPending}
          useCaseKey={legacyUseCaseKey}
          useCaseDisplayName={selectedLegacyUseCase?.display_name ?? legacyUseCaseKey}
          activeVersion={activeLegacyVersion}
          targetVersion={legacyRollbackCandidate}
          legacy={tLegacy}
          onCancel={() => setLegacyRollbackCandidate(null)}
          onConfirm={() => void handleLegacyRollback()}
        />
      ) : null}

      {manualExecuteConfirmOpen &&
      selectedManifestEntryId &&
      selectedSamplePayloadId &&
      activeTab === "catalog" ? (
        <ManualLlmExecuteConfirmModal
          isPending={manualExecuteMutation.isPending}
          manifestEntryId={selectedManifestEntryId}
          samplePayloadId={selectedSamplePayloadId}
          inspectionModeLabel={inspectionModeFullLabel(resolvedInspectionMode)}
          onCancel={() => setManualExecuteConfirmOpen(false)}
          onConfirm={() => {
            manualExecuteMutation.mutate(undefined, {
              onSettled: () => setManualExecuteConfirmOpen(false),
            })
          }}
        />
      ) : null}

      <Outlet />
    </div>
  )
}

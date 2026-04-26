// @ts-nocheck
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
  useCreatePromptDraft,
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
  type AdminInspectionMode,
  type AdminLlmCatalogEntry,
  type AdminPromptDraftCreateInput,
  type AdminPromptVersion,
  type AdminResolvedPlaceholder,
  type SnapshotTimelineItem,
} from "@api"
import { PersonasAdmin } from "./PersonasAdmin"
import { AdminSamplePayloadsAdmin } from "./AdminSamplePayloadsAdmin"
import { AdminPromptEditorPanel } from "./AdminPromptEditorPanel"
import { AdminPromptsLogicGraph } from "./AdminPromptsLogicGraph"
import { AdminPromptCatalogNodeModal } from "./AdminPromptCatalogNodeModal"
import { buildAdminPromptCatalogFlowProjection } from "./adminPromptCatalogFlowProjection"
import { buildLogicGraphProjection } from "./adminPromptsLogicGraphProjection"
import type { AdminPromptsCatalogStrings } from "../../i18n/adminPromptsCatalog"
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

function pickPreferredCatalogEntry(entries: AdminLlmCatalogEntry[]): AdminLlmCatalogEntry | null {
  if (entries.length === 0) {
    return null
  }
  return [...entries].sort((left, right) => {
    const leftScore =
      (left.execution_path_kind === "nominal" ? 4 : 0) +
      (left.source_of_truth_status === "active_snapshot" ? 2 : 0) +
      (left.catalog_visibility_status === "visible" ? 1 : 0)
    const rightScore =
      (right.execution_path_kind === "nominal" ? 4 : 0) +
      (right.source_of_truth_status === "active_snapshot" ? 2 : 0) +
      (right.catalog_visibility_status === "visible" ? 1 : 0)
    if (leftScore !== rightScore) {
      return rightScore - leftScore
    }
    return (left.subfeature ?? "").localeCompare(right.subfeature ?? "")
  })[0] ?? null
}

function formatCatalogFeatureLabel(feature: string): string {
  const normalized = feature.trim().toLowerCase()
  const labels: Record<string, string> = {
    chat: "Chat",
    guidance: "Consultations thematiques",
    natal: "Natal",
    horoscope_daily: "Horoscope quotidien",
  }
  return labels[normalized] ?? feature
}

function releaseDiffAxisBadgeClass(changed: boolean): string {
  return changed ? "badge badge--warning" : "badge badge--info"
}

type ManualLlmExecuteConfirmModalProps = {
  isPending: boolean
  manifestEntryId: string
  samplePayloadId: string
  inspectionModeLabel: string
  catalog: AdminPromptsCatalogStrings
  onCancel: () => void
  onConfirm: () => void
}

function ManualLlmExecuteConfirmModal({
  isPending,
  manifestEntryId,
  samplePayloadId,
  inspectionModeLabel,
  catalog: c,
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
        <h3 id="manual-llm-exec-title">{c.manualLlmModalTitle}</h3>
        <p className="admin-prompts-modal__copy">
          {c.manualLlmModalIntroBeforeSample}
          <code>{samplePayloadId}</code>
          {c.manualLlmModalBetweenSampleAndManifest}
          <code>{manifestEntryId}</code>
          {c.manualLlmModalAfterManifest}
        </p>
        <p className="admin-prompts-modal__copy admin-prompts-modal__copy--emphasis">
          {c.manualLlmModalModePrefix}
          <strong>{inspectionModeLabel}</strong>
          {c.manualLlmModalModeTraced}
        </p>
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            {c.manualLlmModalCancel}
          </button>
          <button
            className="action-button action-button--primary"
            type="button"
            disabled={isPending}
            onClick={onConfirm}
          >
            {isPending ? c.manualLlmModalExecuting : c.manualLlmModalConfirm}
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
        {version.published_at ? (
          <div>
            <dt>{legacy.metaPublished}</dt>
            <dd>{formatLegacyPromptTimestamp(version.published_at, lang)}</dd>
          </div>
        ) : null}
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

function resolvedAssemblyErrorPresentation(
  error: unknown,
  tCat: AdminPromptsCatalogStrings,
): { primary: string; secondary: string | null } {
  if (!(error instanceof AdminPromptsApiError)) {
    return { primary: tCat.resolvedErrorLoadDetailGeneric, secondary: null }
  }
  const mapped = tCat.resolvedAssemblyErrorMessage(error.code)
  const primary = mapped ?? error.message
  const secondary =
    mapped && mapped !== error.message
      ? error.message
      : !mapped
        ? tCat.resolvedErrorSecondaryCodeHttp(error.code, error.status)
        : null
  return { primary, secondary }
}

function AdminPromptsResolvedAssemblyError({
  error,
  catalog,
}: {
  error: unknown
  catalog: AdminPromptsCatalogStrings
}) {
  const { primary, secondary } = resolvedAssemblyErrorPresentation(error, catalog)
  return (
    <div className="admin-prompts-resolved__error" role="alert">
      <p className="admin-prompts-resolved__error-primary">{primary}</p>
      {secondary ? (
        <p className="admin-prompts-resolved__error-secondary text-muted">{secondary}</p>
      ) : null}
    </div>
  )
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

function manualExecutionFailureLead(error: unknown, tCat: AdminPromptsCatalogStrings): string | null {
  if (!(error instanceof AdminPromptsApiError)) {
    return null
  }
  const kind = error.details.failure_kind
  if (typeof kind !== "string") {
    return null
  }
  return tCat.manualExecutionFailureLeadMessage(kind) ?? null
}

function formatPromptSaveError(error: unknown): string {
  if (error instanceof AdminPromptsApiError) {
    const detailLines = Object.entries(error.details)
      .filter(([, value]) => value !== null && value !== undefined && value !== "")
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key}: ${value.join(", ")}`
        }
        if (typeof value === "object") {
          return `${key}: ${JSON.stringify(value)}`
        }
        return `${key}: ${String(value)}`
      })
    return detailLines.length > 0 ? `${error.message} (${detailLines.join(" · ")})` : error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return "Erreur inconnue."
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
  const tEditor = tAdmin.promptsEditor
  const tConsumption = tAdmin.promptsConsumption
  const tCat = tAdmin.promptsCatalog
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

  const [catalogSelectionDraft, setCatalogSelectionDraft] = useState({
    feature: "",
    plan: "",
    locale: "",
  })
  const [catalogSelectionBootstrapped, setCatalogSelectionBootstrapped] = useState(false)
  const [catalogSelection, setCatalogSelection] = useState<{
    feature: string
    plan: string
    locale: string
  } | null>(null)

  const [legacyUseCaseKey, setLegacyUseCaseKey] = useState<string | null>(null)
  const [legacyCompareVersionId, setLegacyCompareVersionId] = useState<string | null>(null)
  const [legacyRollbackCandidate, setLegacyRollbackCandidate] = useState<AdminPromptVersion | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [legacyEditorSuccessMessage, setLegacyEditorSuccessMessage] = useState<string | null>(null)
  const [legacyEditorErrorMessage, setLegacyEditorErrorMessage] = useState<string | null>(null)
  const [catalogEditorSuccessMessage, setCatalogEditorSuccessMessage] = useState<string | null>(null)
  const [catalogEditorErrorMessage, setCatalogEditorErrorMessage] = useState<string | null>(null)
  const [selectedManifestEntryId, setSelectedManifestEntryId] = useState<string | null>(null)
  const [resolvedInspectionMode, setResolvedInspectionMode] = useState<AdminInspectionMode>("assembly_preview")
  const [selectedSamplePayloadId, setSelectedSamplePayloadId] = useState<string | null>(null)
  const [catalogModalNodeId, setCatalogModalNodeId] = useState<string | null>(null)
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

  /** Facettes globales (sans dérouler le catalogue complet) : servent au sélecteur minimal et aux sample payloads. */
  const samplePayloadsFacetsCatalogQuery = useAdminLlmCatalog(
    { page: 1, pageSize: 1, sortBy: "feature", sortOrder: "asc" },
    activeTab === "samplePayloads" || activeTab === "catalog",
  )

  const catalogFacets = samplePayloadsFacetsCatalogQuery.data?.meta?.facets
  const catalogContextQuery = useAdminLlmCatalog(
    catalogSelection
      ? {
          page: 1,
          pageSize: 50,
          feature: catalogSelection.feature,
          plan: catalogSelection.plan,
          locale: catalogSelection.locale,
          sortBy: "subfeature",
          sortOrder: "asc",
        }
      : { page: 1, pageSize: 1, sortBy: "feature", sortOrder: "asc" },
    activeTab === "catalog" && Boolean(catalogSelection),
  )

  const catalogEntries = catalogContextQuery.data?.data ?? []
  const catalogTableEntries = catalogQuery.data?.data ?? []
  const catalogMeta = catalogQuery.data?.meta
  const selectedCatalogEntry =
    catalogTableEntries.find((entry) => entry.manifest_entry_id === selectedManifestEntryId) ??
    catalogEntries.find((entry) => entry.manifest_entry_id === selectedManifestEntryId) ??
    null
  const resolvedQuery = useAdminResolvedAssembly(
    selectedManifestEntryId,
    resolvedInspectionMode,
    effectiveSamplePayloadId,
    activeTab === "catalog" && Boolean(selectedManifestEntryId),
  )
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
        resolvedInspectionMode === "runtime_preview" &&
        Boolean(catalogFeatureForSamplePayloads) &&
        Boolean(catalogLocaleForSamplePayloads),
    },
  )

  useEffect(() => {
    if (activeTab !== "samplePayloads") {
      setSamplePayloadsSeed(null)
    }
  }, [activeTab])

  useEffect(() => {
    if (activeTab !== "catalog") {
      setCatalogModalNodeId(null)
    }
  }, [activeTab])

  useEffect(() => {
    setCatalogModalNodeId(null)
    setCatalogEditorSuccessMessage(null)
    setCatalogEditorErrorMessage(null)
    createPromptDraftMutation.reset()
  }, [selectedManifestEntryId])

  useEffect(() => {
    if (!catalogSelection || catalogEntries.length === 0) {
      return
    }
    if (selectedManifestEntryId && catalogEntries.some((entry) => entry.manifest_entry_id === selectedManifestEntryId)) {
      return
    }
    const preferredEntry = pickPreferredCatalogEntry(catalogEntries)
    if (preferredEntry) {
      setSelectedManifestEntryId(preferredEntry.manifest_entry_id)
    }
  }, [catalogEntries, catalogSelection, selectedManifestEntryId])

  useEffect(() => {
    if (!resolvedQuery.data) {
      return
    }
    setCatalogSelection((current) => {
      if (
        current?.feature === resolvedQuery.data.feature &&
        current?.plan === (resolvedQuery.data.plan ?? "") &&
        current?.locale === (resolvedQuery.data.locale ?? "")
      ) {
        return current
      }
      return {
        feature: resolvedQuery.data.feature,
        plan: resolvedQuery.data.plan ?? "",
        locale: resolvedQuery.data.locale ?? "",
      }
    })
    setCatalogSelectionDraft((current) => {
      const next = {
        feature: current.feature || resolvedQuery.data.feature,
        plan: current.plan || (resolvedQuery.data.plan ?? ""),
        locale: current.locale || (resolvedQuery.data.locale ?? ""),
      }
      if (
        current.feature === next.feature &&
        current.plan === next.plan &&
        current.locale === next.locale
      ) {
        return current
      }
      return next
    })
  }, [resolvedQuery.data])

  useEffect(() => {
    setResolvedInspectionMode("assembly_preview")
    setSelectedSamplePayloadId(null)
  }, [selectedManifestEntryId])

  useEffect(() => {
    if (resolvedInspectionMode !== "runtime_preview") {
      setSelectedSamplePayloadId(null)
    }
  }, [resolvedInspectionMode])

  useEffect(() => {
    setManualExecuteConfirmOpen(false)
  }, [resolvedInspectionMode, selectedManifestEntryId, selectedSamplePayloadId])

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
  const availableSubfeatures = facets?.subfeature ?? []
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
  const catalogHasActiveFilters = Boolean(
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
  )

  const availableFeatures = catalogFacets?.feature ?? []
  const availablePlans = catalogFacets?.plan ?? []
  const availableLocales = catalogFacets?.locale ?? []

  useEffect(() => {
    if (activeTab !== "catalog" || catalogSelectionBootstrapped) {
      return
    }
    const preferredEntry = pickPreferredCatalogEntry(catalogTableEntries)
    const featureSeed = preferredEntry?.feature ?? availableFeatures[0] ?? ""
    const planSeed = preferredEntry?.plan ?? availablePlans[0] ?? ""
    const localeSeed = preferredEntry?.locale ?? availableLocales[0] ?? ""
    if (!featureSeed || !planSeed || !localeSeed) {
      return
    }
    setCatalogSelectionDraft({
      feature: featureSeed,
      plan: planSeed,
      locale: localeSeed,
    })
    setCatalogSelection({
      feature: featureSeed,
      plan: planSeed,
      locale: localeSeed,
    })
    setCatalogSelectionBootstrapped(true)
  }, [
    activeTab,
    availableFeatures,
    availableLocales,
    availablePlans,
    catalogSelectionBootstrapped,
    catalogTableEntries,
  ])

  const useCasesQuery = useAdminLlmUseCases({
    enabled: activeTab === "legacy" || activeTab === "catalog",
  })
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
  const createPromptDraftMutation = useCreatePromptDraft()
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
  const catalogModalEnabled =
    activeTab === "catalog" &&
    Boolean(catalogModalNodeId) &&
    Boolean(resolvedQuery.data?.use_case_key)
  const catalogHistoryQuery = useAdminPromptHistory(
    resolvedQuery.data?.use_case_key ?? "",
    catalogModalEnabled,
  )
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
  const selectedCatalogUseCase =
    useCases.find((item) => item.key === (resolvedQuery.data?.use_case_key ?? "")) ?? null
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
  const catalogHistory = catalogHistoryQuery.data ?? []
  const activeCatalogVersion =
    selectedCatalogUseCase?.active_prompt_version_id != null
      ? (catalogHistory.find((item) => item.id === selectedCatalogUseCase.active_prompt_version_id) ?? null)
      : null
  const logicGraph =
    resolvedQuery.data &&
    resolvedQuery.data.activation &&
    Array.isArray(resolvedQuery.data.selected_components) &&
    Array.isArray(resolvedQuery.data.runtime_artifacts)
      ? buildAdminPromptCatalogFlowProjection(resolvedQuery.data)
      : null
  const resolvedLogicGraph = resolvedQuery.data ? buildLogicGraphProjection(resolvedQuery.data) : null
  const hasStructuredCatalogView = Boolean(logicGraph && resolvedQuery.data?.activation)
  const selectedCatalogFlowNode =
    logicGraph?.flowNodes.find((node) => node.id === catalogModalNodeId) ?? null
  const canApplyCatalogSelection = Boolean(
    catalogSelectionDraft.feature && catalogSelectionDraft.plan && catalogSelectionDraft.locale,
  )
  const catalogContextLabel = resolvedQuery.data
    ? `${resolvedQuery.data.feature}/${resolvedQuery.data.subfeature ?? "-"}/${resolvedQuery.data.plan ?? "-"}/${resolvedQuery.data.locale ?? "-"}`
    : null

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
    setSuccessMessage(null)
    setLegacyEditorSuccessMessage(null)
    setLegacyEditorErrorMessage(null)
    createPromptDraftMutation.reset()
  }, [legacyUseCaseKey])

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
  }

  const createDraftForUseCase = async (
    useCaseKey: string,
    payload: AdminPromptDraftCreateInput,
    onSuccess: (createdVersion: AdminPromptVersion) => void,
    onError: (message: string) => void,
  ) => {
    try {
      const createdVersion = await createPromptDraftMutation.mutateAsync({
        useCaseKey,
        payload,
      })
      onSuccess(createdVersion)
    } catch (error) {
      onError(formatPromptSaveError(error))
      throw error
    }
  }

  const handleLegacyCreateDraft = async (payload: AdminPromptDraftCreateInput) => {
    if (!legacyUseCaseKey) return
    setSuccessMessage(null)
    setLegacyEditorSuccessMessage(null)
    setLegacyEditorErrorMessage(null)

    await createDraftForUseCase(
      legacyUseCaseKey,
      payload,
      (createdVersion) => {
        setLegacyEditorSuccessMessage(tEditor.success(createdVersion.id.slice(0, 8)))
        setLegacyCompareVersionId(createdVersion.id)
      },
      setLegacyEditorErrorMessage,
    )
  }

  const handleCatalogCreateDraft = async (payload: AdminPromptDraftCreateInput) => {
    if (!resolvedQuery.data?.use_case_key) return
    setCatalogEditorSuccessMessage(null)
    setCatalogEditorErrorMessage(null)

    await createDraftForUseCase(
      resolvedQuery.data.use_case_key,
      payload,
      (createdVersion) => {
        setCatalogEditorSuccessMessage(tEditor.success(createdVersion.id.slice(0, 8)))
      },
      setCatalogEditorErrorMessage,
    )
  }

  return (
    <div className="admin-prompts-page">
      <header className="admin-page-header">
        <div>
          <h2>{pageHeader.title}</h2>
          <p className="admin-prompts-page__intro">{pageHeader.intro}</p>
        </div>
        <nav className="admin-tabs admin-prompts-subnav" aria-label={tCat.subNavAriaLabel}>
          <NavLink
            to={`${ADMIN_PROMPTS_BASE}/catalog`}
            className={({ isActive }) => `tab-button ${isActive ? "tab-button--active" : ""}`}
            end
          >
            {sub.catalog}
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
        <section className="panel admin-prompts-catalog" aria-label={tCat.catalogRegionAria}>
          <div className="admin-prompts-catalog__flow-shell">
            <header className="admin-prompts-catalog__flow-header">
              <p className="admin-prompts-catalog__flow-kicker">Catalogue actif</p>
              <h3 className="admin-prompts-catalog__flow-title">Sélectionner un contexte catalogue</h3>
              <p className="admin-prompts-catalog__flow-intro">
                Commencez par choisir une feature, un abonnement et une locale. Le schéma affiche ensuite
                l&apos;activation canonique, les composants retenus et les artefacts runtime réellement préparés.
                Cliquez sur un nœud pour ouvrir sa modale d&apos;édition ou de lecture.
              </p>
            </header>

            <section className="admin-prompts-catalog__selector" aria-label="Sélection du contexte catalogue">
              <div className="admin-prompts-catalog__selector-grid">
                <label className="admin-prompts-catalog__filter-field" htmlFor="catalog-feature-minimal">
                  <span>{tCat.filterFeatureLabel}</span>
                  <select
                    id="catalog-feature-minimal"
                    value={catalogSelectionDraft.feature}
                    onChange={(event) =>
                      setCatalogSelectionDraft((current) => ({ ...current, feature: event.target.value }))
                    }
                  >
                    <option value="">{tCat.filterAllFeminine}</option>
                    {availableFeatures.map((value) => (
                      <option key={value} value={value}>
                        {formatCatalogFeatureLabel(value)}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="admin-prompts-catalog__filter-field" htmlFor="catalog-plan-minimal">
                  <span>{tCat.filterPlanLabel}</span>
                  <select
                    id="catalog-plan-minimal"
                    value={catalogSelectionDraft.plan}
                    onChange={(event) =>
                      setCatalogSelectionDraft((current) => ({ ...current, plan: event.target.value }))
                    }
                  >
                    <option value="">{tCat.filterAllMasculine}</option>
                    {availablePlans.map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="admin-prompts-catalog__filter-field" htmlFor="catalog-locale-minimal">
                  <span>{tCat.filterLocaleLabel}</span>
                  <select
                    id="catalog-locale-minimal"
                    value={catalogSelectionDraft.locale}
                    onChange={(event) =>
                      setCatalogSelectionDraft((current) => ({ ...current, locale: event.target.value }))
                    }
                  >
                    <option value="">{tCat.filterAllFeminine}</option>
                    {availableLocales.map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="admin-prompts-catalog__selector-actions">
                <button
                  className="action-button action-button--primary"
                  type="button"
                  disabled={!canApplyCatalogSelection}
                  onClick={() =>
                    setCatalogSelection({
                      feature: catalogSelectionDraft.feature,
                      plan: catalogSelectionDraft.plan,
                      locale: catalogSelectionDraft.locale,
                    })
                  }
                >
                  Afficher le schéma
                </button>
                <button
                  className="text-button"
                  type="button"
                  onClick={() => {
                    setCatalogSelection(null)
                    setCatalogSelectionDraft({ feature: "", plan: "", locale: "" })
                    setSelectedManifestEntryId(null)
                    setCatalogModalNodeId(null)
                    setCatalogEditorSuccessMessage(null)
                    setCatalogEditorErrorMessage(null)
                  }}
                >
                  Réinitialiser
                </button>
              </div>
            </section>

            {!catalogSelection ? (
              <div className="admin-prompts-catalog__detail-empty">
                <p className="text-muted">
                  Sélectionnez un triplet feature / abonnement / locale pour charger le graphe du catalogue actif.
                </p>
              </div>
            ) : null}

            {catalogSelection && catalogContextQuery.isPending ? (
              <div className="loading-placeholder">{tCat.catalogLoading}</div>
            ) : null}
            {catalogSelection && catalogContextQuery.isError ? (
              <p className="chat-error">{tCat.catalogError}</p>
            ) : null}
            {catalogSelection &&
            !catalogContextQuery.isPending &&
            !catalogContextQuery.isError &&
            catalogEntries.length === 0 ? (
              <div className="state-line">
                Aucun prompt catalogue actif ne correspond à cette combinaison feature / abonnement / locale.
              </div>
            ) : null}

            {catalogSelection && selectedManifestEntryId && hasStructuredCatalogView ? (
              <>
                <section
                  className="admin-prompts-catalog-detail-summary"
                  aria-label="Résumé du contexte catalogue"
                >
                  <h3 className="admin-prompts-catalog-detail-summary__title">
                    Résumé du contexte catalogue
                  </h3>
                  {catalogContextLabel ? (
                    <p className="admin-prompts-catalog-detail-summary__tuple">{catalogContextLabel}</p>
                  ) : null}
                  <dl className="admin-prompts-catalog-detail-summary__meta">
                    <div>
                      <dt>{tCat.detailManifestEntryDt}</dt>
                      <dd>
                        <code>{selectedManifestEntryId}</code>
                      </dd>
                    </div>
                    <div>
                      <dt>{tCat.detailAssemblyDt}</dt>
                      <dd>{resolvedQuery.data?.assembly_id ?? selectedCatalogEntry?.assembly_id ?? "—"}</dd>
                    </div>
                    <div>
                      <dt>{tCat.detailExecutionProfileDt}</dt>
                      <dd>
                        {selectedCatalogEntry?.execution_profile_ref ??
                          resolvedQuery.data?.composition_sources.execution_profile.name ??
                          "—"}
                      </dd>
                    </div>
                    <div>
                      <dt>{tCat.detailOutputContractDt}</dt>
                      <dd>{selectedCatalogEntry?.output_contract_ref ?? "—"}</dd>
                    </div>
                    <div>
                      <dt>{tCat.detailCatalogVisibilityDt}</dt>
                      <dd>
                        {selectedCatalogEntry
                          ? tCat.labelCatalogVisibilityStatus(selectedCatalogEntry.catalog_visibility_status)
                          : "—"}
                      </dd>
                    </div>
                  </dl>
                  {hasStructuredCatalogView ? (
                    <div className="admin-prompts-catalog-layers">
                      <section className="admin-prompts-catalog-layer-card" aria-label="Activation">
                        <h4>Activation</h4>
                        <dl className="admin-prompts-catalog-layer-card__meta">
                          <div>
                            <dt>Manifest</dt>
                            <dd>
                              <code>{resolvedQuery.data.activation.manifest_entry_id}</code>
                            </dd>
                          </div>
                          <div>
                            <dt>Provider</dt>
                            <dd>{resolvedQuery.data.activation.provider_target}</dd>
                          </div>
                          <div>
                            <dt>Policy family</dt>
                            <dd>{resolvedQuery.data.activation.policy_family}</dd>
                          </div>
                          <div>
                            <dt>Output schema</dt>
                            <dd>{resolvedQuery.data.activation.output_schema ?? "—"}</dd>
                          </div>
                          <div>
                            <dt>Injecteurs</dt>
                            <dd>{resolvedQuery.data.activation.injector_set.join(", ") || "—"}</dd>
                          </div>
                          <div>
                            <dt>Persona policy</dt>
                            <dd>{resolvedQuery.data.activation.persona_policy ?? "—"}</dd>
                          </div>
                        </dl>
                      </section>

                      <section className="admin-prompts-catalog-layer-card" aria-label="Composants sélectionnés">
                        <h4>Composants sélectionnés</h4>
                        <ul className="admin-prompts-catalog-layer-card__list">
                          {resolvedQuery.data.selected_components.map((component) => (
                            <li key={component.key}>
                              <strong>{component.title}</strong>
                              <span>{component.summary}</span>
                            </li>
                          ))}
                        </ul>
                      </section>

                      <section className="admin-prompts-catalog-layer-card" aria-label="Artefacts runtime">
                        <h4>Artefacts runtime</h4>
                        <ul className="admin-prompts-catalog-layer-card__list">
                          {resolvedQuery.data.runtime_artifacts.map((artifact) => (
                            <li key={artifact.key}>
                              <strong>{artifact.title}</strong>
                              <span>{artifact.delta_note ?? artifact.summary}</span>
                            </li>
                          ))}
                        </ul>
                      </section>
                    </div>
                  ) : null}
                </section>

                <section className="admin-prompts-catalog__graph-surface" aria-label={tCat.graphZoneAria}>
                  <div className="admin-prompts-catalog__graph-head">
                    <div>
                      <h3 className="admin-prompts-catalog__graph-title">{tCat.graphZoneTitle}</h3>
                      <p className="admin-prompts-catalog__graph-intro text-muted">{tCat.graphIntro}</p>
                    </div>
                    {hasStructuredCatalogView ? (
                      <span className="badge badge--info">{resolvedQuery.data.activation.provider_target}</span>
                    ) : null}
                  </div>

                  {resolvedQuery.isPending ? <div className="loading-placeholder">{tCat.resolvedLoading}</div> : null}
                  {resolvedQuery.isError ? (
                    <AdminPromptsResolvedAssemblyError error={resolvedQuery.error} catalog={tCat} />
                  ) : null}

                  {hasStructuredCatalogView ? (
                    <>
                      <AdminPromptsLogicGraph
                        projection={logicGraph}
                        onNodeSelect={(nodeId) => setCatalogModalNodeId(nodeId)}
                      />
                      <p className="admin-prompts-catalog__graph-help text-muted">
                        Le graphe sépare l&apos;activation canonique, les composants réellement sélectionnés et les
                        artefacts runtime envoyés au provider. Cliquez sur un nœud pour inspecter son contenu.
                      </p>
                      <section className="admin-prompts-catalog__final-prompt">
                        <h4>Final provider payload</h4>
                        <pre className="admin-prompts-code">
                          {resolvedQuery.data.runtime_artifacts.find(
                            (artifact) => artifact.key === "final_provider_payload",
                          )?.content ?? "Payload final indisponible."}
                        </pre>
                      </section>
                    </>
                  ) : null}
                </section>
              </>
            ) : null}
          </div>
        </section>
      ) : null}

      {activeTab === "catalog" ? (
        <section className="panel admin-prompts-catalog" aria-label={tCat.catalogRegionAria}>
          <div className="admin-prompts-catalog-master-detail">
            <div className="admin-prompts-catalog__master">
              <div className="admin-prompts-catalog__filters">
                <div className="admin-prompts-catalog__filters-primary">
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-search">{tCat.filterSearchLabel}</label>
                    <input
                      id="catalog-search"
                      value={search}
                      onChange={(event) => {
                        setSearch(event.target.value)
                        setPage(1)
                      }}
                      placeholder={tCat.filterSearchPlaceholder}
                    />
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-feature">{tCat.filterFeatureLabel}</label>
                    <select
                      id="catalog-feature"
                      value={feature}
                      onChange={(event) => {
                        setFeature(event.target.value)
                        setPage(1)
                      }}
                    >
                      <option value="">{tCat.filterAllFeminine}</option>
                      {availableFeatures.map((value) => (
                        <option key={value} value={value}>
                          {formatCatalogFeatureLabel(value)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-locale">{tCat.filterLocaleLabel}</label>
                    <select
                      id="catalog-locale"
                      value={locale}
                      onChange={(event) => {
                        setLocale(event.target.value)
                        setPage(1)
                      }}
                    >
                      <option value="">{tCat.filterAllFeminine}</option>
                      {availableLocales.map((value) => (
                        <option key={value} value={value}>
                          {value}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-provider">{tCat.filterProviderLabel}</label>
                    <select
                      id="catalog-provider"
                      value={provider}
                      onChange={(event) => {
                        setProvider(event.target.value)
                        setPage(1)
                      }}
                    >
                      <option value="">{tCat.filterAllMasculine}</option>
                      {availableProviders.map((value) => (
                        <option key={value} value={value}>
                          {value}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-sort">{tCat.filterSortLabel}</label>
                    <select
                      id="catalog-sort"
                      aria-label={tCat.sortAriaCatalog}
                      value={sortBy}
                      onChange={(event) => {
                        setSortBy(event.target.value)
                        setPage(1)
                      }}
                    >
                      <option value="feature">{tCat.sortOptionFeature}</option>
                      <option value="subfeature">{tCat.sortOptionSubfeature}</option>
                      <option value="plan">{tCat.sortOptionPlan}</option>
                      <option value="locale">{tCat.sortOptionLocale}</option>
                      <option value="manifest_entry_id">{tCat.sortOptionManifestEntry}</option>
                      <option value="provider">{tCat.sortOptionProvider}</option>
                      <option value="source_of_truth_status">{tCat.sortOptionSourceOfTruth}</option>
                      <option value="assembly_status">{tCat.sortOptionAssemblyStatus}</option>
                      <option value="release_health_status">{tCat.sortOptionReleaseHealth}</option>
                      <option value="catalog_visibility_status">{tCat.sortOptionCatalogVisibility}</option>
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-field">
                    <label htmlFor="catalog-sort-order">{tCat.filterSortOrderLabel}</label>
                    <select
                      id="catalog-sort-order"
                      aria-label={tCat.sortOrderAriaCatalog}
                      value={sortOrder}
                      onChange={(event) => {
                        setSortOrder(event.target.value as "asc" | "desc")
                        setPage(1)
                      }}
                    >
                      <option value="asc">{tCat.sortOrderAsc}</option>
                      <option value="desc">{tCat.sortOrderDesc}</option>
                    </select>
                  </div>
                  <div className="admin-prompts-catalog__filter-actions">
                    <button className="text-button" type="button" onClick={resetCatalogFilters}>
                      {tCat.resetCatalogFilters}
                    </button>
                  </div>
                </div>
                <div className="admin-prompts-catalog__active-filters" aria-label={tCat.activeFiltersAria}>
                  {catalogHasActiveFilters ? (
                    <ul className="admin-prompts-catalog__active-filters-list">
                      {search.trim() ? <li>{tCat.activeFilterSearch(search.trim())}</li> : null}
                      {feature ? <li>{tCat.activeFilterFeature(feature)}</li> : null}
                      {subfeature ? <li>{tCat.activeFilterSubfeature(subfeature)}</li> : null}
                      {plan ? <li>{tCat.activeFilterPlan(plan)}</li> : null}
                      {locale ? <li>{tCat.activeFilterLocale(locale)}</li> : null}
                      {provider ? <li>{tCat.activeFilterProvider(provider)}</li> : null}
                      {sourceOfTruthStatus ? (
                        <li>
                          {tCat.activeFilterSourceOfTruth(tCat.labelSourceOfTruthStatus(sourceOfTruthStatus))}
                        </li>
                      ) : null}
                      {assemblyStatus ? (
                        <li>{tCat.activeFilterAssembly(tCat.labelAssemblyStatus(assemblyStatus))}</li>
                      ) : null}
                      {releaseHealthStatus ? (
                        <li>
                          {tCat.activeFilterReleaseHealth(tCat.labelReleaseHealthStatus(releaseHealthStatus))}
                        </li>
                      ) : null}
                      {catalogVisibilityStatus ? (
                        <li>
                          {tCat.activeFilterVisibility(tCat.labelCatalogVisibilityStatus(catalogVisibilityStatus))}
                        </li>
                      ) : null}
                    </ul>
                  ) : (
                    <span className="text-muted">{tCat.noActiveFilters}</span>
                  )}
                </div>
                <div className="admin-prompts-catalog__filters-advanced">
                  <button
                    type="button"
                    className="admin-prompts-catalog__filters-advanced-toggle"
                    aria-expanded={catalogAdvancedFiltersOpen}
                    onClick={() => setCatalogAdvancedFiltersOpen((open) => !open)}
                  >
                    {tCat.advancedFiltersToggle}
                  </button>
                  {catalogAdvancedFiltersOpen ? (
                    <div className="admin-prompts-catalog__filters-advanced-panel">
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-subfeature">{tCat.filterSubfeatureLabel}</label>
                        <select
                          id="catalog-subfeature"
                          value={subfeature}
                          onChange={(event) => {
                            setSubfeature(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">{tCat.filterAllFeminine}</option>
                          {availableSubfeatures.map((value) => (
                            <option key={value} value={value}>
                              {value}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-plan">{tCat.filterPlanLabel}</label>
                        <select
                          id="catalog-plan"
                          value={plan}
                          onChange={(event) => {
                            setPlan(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">{tCat.filterAllMasculine}</option>
                          {availablePlans.map((value) => (
                            <option key={value} value={value}>
                              {value}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-sot">{tCat.filterSourceOfTruth}</label>
                        <select
                          id="catalog-sot"
                          value={sourceOfTruthStatus}
                          onChange={(event) => {
                            setSourceOfTruthStatus(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">{tCat.filterAllFeminine}</option>
                          {availableSourceStatuses.map((value) => (
                            <option key={value} value={value}>
                              {tCat.labelSourceOfTruthStatus(value)}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-assembly">{tCat.filterAssemblyStatus}</label>
                        <select
                          id="catalog-assembly"
                          value={assemblyStatus}
                          onChange={(event) => {
                            setAssemblyStatus(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">{tCat.filterAllMasculine}</option>
                          {availableAssemblyStatuses.map((value) => (
                            <option key={value} value={value}>
                              {tCat.labelAssemblyStatus(value)}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-rel-health">{tCat.filterReleaseHealth}</label>
                        <select
                          id="catalog-rel-health"
                          value={releaseHealthStatus}
                          onChange={(event) => {
                            setReleaseHealthStatus(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">{tCat.filterAllMasculine}</option>
                          {availableReleaseHealthStatuses.map((value) => (
                            <option key={value} value={value}>
                              {tCat.labelReleaseHealthStatus(value)}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="admin-prompts-catalog__filter-field">
                        <label htmlFor="catalog-vis">{tCat.filterCatalogVisibility}</label>
                        <select
                          id="catalog-vis"
                          value={catalogVisibilityStatus}
                          onChange={(event) => {
                            setCatalogVisibilityStatus(event.target.value)
                            setPage(1)
                          }}
                        >
                          <option value="">{tCat.filterAllFeminine}</option>
                          {availableVisibilityStatuses.map((value) => (
                            <option key={value} value={value}>
                              {tCat.labelCatalogVisibilityStatus(value)}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  ) : null}
                </div>
              </div>

          {catalogQuery.isPending ? <div className="loading-placeholder">{tCat.catalogLoading}</div> : null}
          {catalogQuery.isError ? <p className="chat-error">{tCat.catalogError}</p> : null}

          {!catalogQuery.isPending && !catalogQuery.isError ? (
            <>
              <div className="admin-prompts-catalog__table-wrap">
                <table className="admin-prompts-catalog__table">
                  <thead>
                    <tr>
                      <th>{tCat.tableColTuple}</th>
                      <th>{tCat.tableColSnapshot}</th>
                      <th>{tCat.tableColProviderModel}</th>
                      <th>{tCat.tableColHealth}</th>
                      <th className="admin-prompts-catalog__col-action">{tCat.tableColAction}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {catalogTableEntries.map((entry) => (
                      <tr
                        key={entry.manifest_entry_id}
                        className={`admin-prompts-catalog__row${entry.manifest_entry_id === selectedManifestEntryId ? " admin-prompts-catalog__row--selected" : ""}`}
                        tabIndex={0}
                        aria-label={tCat.catalogRowAria(
                          `${entry.feature}/${entry.subfeature ?? "-"}/${entry.plan ?? "-"}/${entry.locale ?? "-"}`,
                          entry.manifest_entry_id === selectedManifestEntryId,
                        )}
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
                            : tCat.notAvailable}
                        </td>
                        <td>
                          {entry.provider ?? "—"} / {entry.model ?? "—"}
                        </td>
                        <td className="admin-prompts-catalog__health-cell">
                          <span
                            className={`badge ${entry.source_of_truth_status === "active_snapshot" ? "badge--info" : "badge--warning"}`}
                          >
                            {tCat.labelSourceOfTruthStatus(entry.source_of_truth_status)}
                          </span>
                          <div className="text-muted">
                            {tCat.healthLine(
                              tCat.labelReleaseHealthStatus(entry.release_health_status),
                              tCat.labelRuntimeSignalStatus(entry.runtime_signal_status),
                              tCat.labelCatalogVisibilityStatus(entry.catalog_visibility_status),
                            )}
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
                            {tCat.openDetail}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="admin-prompts-catalog__footer">
                <span>
                  {tCat.catalogFooterLines(
                    catalogMeta?.total ?? 0,
                    String(catalogMeta?.freshness_window_minutes ?? "-"),
                  )}
                </span>
                <div className="admin-prompts-catalog__pagination">
                  <button className="text-button" type="button" onClick={() => setPage((current) => Math.max(current - 1, 1))} disabled={page <= 1}>
                    {tCat.catalogPrev}
                  </button>
                  <span>{tCat.catalogPage(catalogMeta?.page ?? page)}</span>
                  <button className="text-button" type="button" onClick={() => setPage((current) => current + 1)} disabled={Boolean(catalogMeta && catalogMeta.page * pageSize >= catalogMeta.total)}>
                    {tCat.catalogNext}
                  </button>
                </div>
              </div>
            </>
          ) : null}
            </div>

            <aside className="admin-prompts-catalog__detail-panel" aria-label={tCat.detailPanelAria}>
              {selectedManifestEntryId ? (
                <>
                  <section className="admin-prompts-catalog-detail-summary" aria-label={tCat.detailSummaryTitle}>
                    <h3 className="admin-prompts-catalog-detail-summary__title">{tCat.detailSummaryTitle}</h3>
                    {selectedCatalogEntry ? (
                      <>
                        <p className="admin-prompts-catalog-detail-summary__tuple">
                          {selectedCatalogEntry.feature}/{selectedCatalogEntry.subfeature ?? "-"}/
                          {selectedCatalogEntry.plan ?? "-"}/{selectedCatalogEntry.locale ?? "-"}
                        </p>
                        <dl className="admin-prompts-catalog-detail-summary__meta">
                          <div>
                            <dt>{tCat.detailManifestEntryDt}</dt>
                            <dd>
                              <code>{selectedCatalogEntry.manifest_entry_id}</code>
                            </dd>
                          </div>
                          <div>
                            <dt>{tCat.detailAssemblyDt}</dt>
                            <dd>
                              {selectedCatalogEntry.assembly_id ?? "—"}{" "}
                              <span className="text-muted">
                                ({tCat.labelAssemblyStatus(selectedCatalogEntry.assembly_status)})
                              </span>
                            </dd>
                          </div>
                          <div>
                            <dt>{tCat.detailExecutionProfileDt}</dt>
                            <dd>{selectedCatalogEntry.execution_profile_ref ?? "—"}</dd>
                          </div>
                          <div>
                            <dt>{tCat.detailOutputContractDt}</dt>
                            <dd>{selectedCatalogEntry.output_contract_ref ?? "—"}</dd>
                          </div>
                          <div>
                            <dt>{tCat.detailCatalogVisibilityDt}</dt>
                            <dd>{tCat.labelCatalogVisibilityStatus(selectedCatalogEntry.catalog_visibility_status)}</dd>
                          </div>
                        </dl>
                      </>
                    ) : resolvedQuery.data ? (
                      <>
                        <p className="admin-prompts-catalog-detail-summary__tuple">
                          {resolvedQuery.data.feature}/{resolvedQuery.data.subfeature ?? "-"}/
                          {resolvedQuery.data.plan ?? "-"}/{resolvedQuery.data.locale ?? "-"}
                        </p>
                        <p className="text-muted">{tCat.detailOffPageFromResolved}</p>
                        <dl className="admin-prompts-catalog-detail-summary__meta">
                          <div>
                            <dt>{tCat.detailManifestEntryDt}</dt>
                            <dd>
                              <code>{resolvedQuery.data.manifest_entry_id}</code>
                            </dd>
                          </div>
                          <div>
                            <dt>{tCat.detailAssemblyDt}</dt>
                            <dd>{resolvedQuery.data.assembly_id ?? "—"}</dd>
                          </div>
                        </dl>
                      </>
                    ) : (
                      <p className="text-muted">
                        {tCat.detailOffPageIdOnly} <code>{selectedManifestEntryId}</code>
                      </p>
                    )}
                  </section>
                <section className="panel admin-prompts-resolved" aria-label={tCat.resolvedPanelAria}>
                  <div
                    className={`admin-prompts-resolved__surface-banner admin-prompts-resolved__surface-banner--${resolvedInspectionMode}`}
                    role="status"
                    aria-live="polite"
                    aria-label={tCat.inspectionBannerAria}
                  >
                    <span className="admin-prompts-resolved__surface-banner-kicker">{tCat.inspectionBannerKicker}</span>
                    <span className="admin-prompts-resolved__surface-banner-title">
                      {tCat.inspectionModeFullLabel(resolvedInspectionMode)}
                    </span>
                    <span className="admin-prompts-resolved__surface-banner-short">
                      ({tCat.inspectionModeShortLabel(resolvedInspectionMode)})
                    </span>
                  </div>
                  <section className="admin-prompts-detail-section" aria-label={tCat.inspectionSectionAria}>
                    <div className="admin-prompts-resolved__header">
                      <h3>{tCat.inspectionHeading}</h3>
                      <div className="admin-prompts-resolved__header-meta">
                        <code>{selectedManifestEntryId}</code>
                        <span
                          className={`badge ${resolvedQuery.data?.inspection_mode === "assembly_preview" ? "badge--info" : "badge--warning"}`}
                        >
                          {resolvedQuery.data
                            ? tCat.modeBadge(tCat.inspectionModeShortLabel(resolvedQuery.data.inspection_mode))
                            : "—"}
                        </span>
                        <label className="admin-prompts-resolved__mode-field">
                          <span className="text-muted">{tCat.inspectionModeFieldCaption}</span>
                          <select
                            aria-label={tCat.inspectionModeSelectAria}
                            className="admin-prompts-resolved__mode-select"
                            value={resolvedInspectionMode}
                            onChange={(event) => {
                              setResolvedInspectionMode(event.target.value as AdminInspectionMode)
                            }}
                          >
                            {tCat.inspectionModeOptions.map((opt) => (
                              <option key={opt.value} value={opt.value}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                        </label>
                      </div>
                    </div>
                    <p className="admin-prompts-resolved__render-note">
                      {tCat.inspectionModeHelpText(resolvedQuery.data?.inspection_mode ?? resolvedInspectionMode)}
                    </p>
                  </section>
                  <section className="admin-prompts-detail-section" aria-label={tCat.executionStateSectionAria}>
                    {resolvedInspectionMode === "runtime_preview" && samplePayloadsQuery.isPending ? (
                      <p className="text-muted">{tCat.resolvedLoadingSamples}</p>
                    ) : null}
                    {resolvedQuery.isPending ? <div className="loading-placeholder">{tCat.resolvedLoading}</div> : null}
                    {resolvedQuery.isError ? (
                      <AdminPromptsResolvedAssemblyError error={resolvedQuery.error} catalog={tCat} />
                    ) : null}
                    {resolvedQuery.data ? (
                      <p className="admin-prompts-detail__exec-state text-muted" role="status">
                        {tCat.resolvedStateLead(
                          tCat.inspectionModeShortLabel(resolvedQuery.data.inspection_mode),
                          tCat.labelSourceOfTruthStatus(resolvedQuery.data.source_of_truth_status),
                          resolvedQuery.data.active_snapshot_version ?? "",
                        )}
                      </p>
                    ) : null}
                  </section>
                  <section className="admin-prompts-detail-section admin-prompts-detail__actions" aria-label={tCat.actionsSectionAria}>
                    <div className="admin-prompts-detail__actions-header">
                      <h3 className="admin-prompts-detail__actions-title">{tCat.actionsTitle}</h3>
                      <p className="admin-prompts-detail__actions-risk text-muted">{tCat.actionsRiskNote}</p>
                    </div>
                    {resolvedInspectionMode === "runtime_preview" ? (
                      <div className="admin-prompts-resolved__manual-exec admin-prompts-resolved__manual-exec--confirmed-surface">
                        <label className="admin-prompts-resolved__mode-field admin-prompts-detail__actions-field">
                          <span className="text-muted">{tCat.samplePayloadFieldCaption}</span>
                          <select
                            aria-label={tCat.samplePayloadSelectAria}
                            className="admin-prompts-resolved__mode-select"
                            value={selectedSamplePayloadId ?? ""}
                            onChange={(event) => {
                              setSelectedSamplePayloadId(event.target.value || null)
                            }}
                          >
                            <option value="">{tCat.noSamplePayloadOption}</option>
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
                          {manualExecuteMutation.isPending ? tCat.executeWithLlmPending : tCat.executeWithLlm}
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
                            {tCat.manualExecIncomplete}
                          </p>
                        ) : null}
                        {manualExecuteMutation.isError ? (
                          <div
                            className="admin-prompts-resolved__error admin-prompts-resolved__manual-exec-error"
                            role="alert"
                          >
                            <p className="admin-prompts-resolved__error-primary">
                              {manualExecuteMutation.error instanceof AdminPromptsApiError
                                ? resolvedAssemblyErrorPresentation(manualExecuteMutation.error, tCat).primary
                                : tCat.manualExecErrorGeneric}
                            </p>
                            {manualExecuteMutation.error instanceof AdminPromptsApiError &&
                            manualExecutionFailureLead(manualExecuteMutation.error, tCat) ? (
                              <p className="admin-prompts-resolved__error-secondary text-muted">
                                {manualExecutionFailureLead(manualExecuteMutation.error, tCat)}
                              </p>
                            ) : null}
                          </div>
                        ) : null}
                      </div>
                    ) : (
                      <p className="text-muted admin-prompts-detail__actions-idle">{tCat.runtimePreviewIdle}</p>
                    )}
                  </section>
                  {resolvedQuery.data ? (
                    <>
                      <div className="admin-prompts-resolved__zones">
                        <section className="admin-prompts-resolved__zone" aria-label={tCat.promptsZoneAria}>
                          <h4>{tCat.promptsZoneTitle}</h4>
                          <p className="text-muted">
                            {tCat.promptsSourceLine(
                              tCat.labelSourceOfTruthStatus(resolvedQuery.data.source_of_truth_status),
                              resolvedQuery.data.active_snapshot_version ?? tCat.notAvailable,
                            )}
                          </p>
                          <PromptDisclosure summary={tCat.disclosureAssembled}>
                            <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.assembled_prompt}</pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary={tCat.disclosurePostInjectors}>
                            <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.post_injectors_prompt}</pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary={tCat.disclosureRendered}>
                            <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.rendered_prompt}</pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary={tCat.disclosureSystemPolicy}>
                            <pre className="admin-prompts-code">
                              {String(resolvedQuery.data.resolved_result.provider_messages.system_hard_policy ?? "")}
                            </pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary={tCat.disclosureDeveloper}>
                            <pre className="admin-prompts-code">
                              {String(resolvedQuery.data.resolved_result.provider_messages.developer_content_rendered ?? "")}
                            </pre>
                          </PromptDisclosure>
                          <PromptDisclosure summary={tCat.disclosurePersona}>
                            <pre className="admin-prompts-code">
                              {String(resolvedQuery.data.resolved_result.provider_messages.persona_block ?? "")}
                            </pre>
                          </PromptDisclosure>
                        </section>
                        <section className="admin-prompts-resolved__zone" aria-label={tCat.placeholdersZoneAria}>
                          <h4>{tCat.placeholdersZoneTitle}</h4>
                          <p className="text-muted">{tCat.placeholdersIntro}</p>
                          {resolvedQuery.data.resolved_result.placeholders.length === 0 ? (
                            <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                              {tCat.placeholdersEmpty}
                            </p>
                          ) : (
                            <div className="admin-prompts-resolved__placeholders">
                              {resolvedQuery.data.resolved_result.placeholders.map((item) => (
                                <article key={item.name} className="admin-prompts-resolved__placeholder">
                                  <strong>{item.name}</strong>
                                  <span className={`admin-prompts-resolved__placeholder-status ${placeholderStatusClassName(item.status)}`}>
                                    {tCat.placeholderStatusLabel(item.status)}
                                  </span>
                                  <span className="text-muted">{tCat.placeholderSourceLabel(item.resolution_source)}</span>
                                  <span className="text-muted">{item.classification ?? tCat.placeholderUnknownClassification}</span>
                                  <span className="text-muted">{tCat.placeholderRedactionLevelLabel(item)}</span>
                                  <span className="text-muted">{item.reason ?? tCat.placeholderUnknownReason}</span>
                                  <span className="text-muted">{tCat.placeholderPreviewValue(item)}</span>
                                </article>
                              ))}
                            </div>
                          )}
                        </section>
                        <section className="admin-prompts-resolved__zone" aria-label={tCat.llmReturnZoneAria}>
                          <h4>{tCat.llmReturnZoneTitle}</h4>
                          <p className="text-muted">
                            {tCat.contextQualityLine(
                              tCat.labelContextCompensation(resolvedQuery.data.resolved_result.context_compensation_status),
                            )}
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
                              {tCat.renderErrorLeadLine(
                                resolvedQuery.data.inspection_mode,
                                resolvedQuery.data.resolved_result.provider_messages.render_error_kind,
                              )}
                              {resolvedQuery.data.resolved_result.provider_messages.render_error}
                            </p>
                          ) : null}
                          <PromptDisclosure summary={tCat.disclosureExecParamsPreview}>
                            <pre className="admin-prompts-code">
                              {JSON.stringify(resolvedQuery.data.resolved_result.provider_messages.execution_parameters, null, 2)}
                            </pre>
                          </PromptDisclosure>
                          <p className="text-muted">{tCat.llmOutputLead}</p>
                          {resolvedInspectionMode === "runtime_preview" ? (
                            <>
                              {manualExecuteMutation.isPending ? (
                                <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                                  {tCat.executeWithLlmPending}
                                </p>
                              ) : null}
                              {manualExecuteMutation.isError ? (
                                <p
                                  className="admin-prompts-resolved__state admin-prompts-resolved__state--error"
                                  role="status"
                                >
                                  {tCat.manualExecFailed}
                                </p>
                              ) : null}
                              {!manualExecuteMutation.isPending && !manualExecuteMutation.isError ? (
                                manualExecuteMutation.data ? (
                                  <div className="admin-prompts-resolved__llm-return" aria-live="polite">
                                    <dl className="admin-prompts-resolved__llm-meta">
                                      <div>
                                        <dt>{tCat.validationStatusDt}</dt>
                                        <dd>{manualExecuteMutation.data.validation_status}</dd>
                                      </div>
                                      <div>
                                        <dt>{tCat.durationDt}</dt>
                                        <dd>{manualExecuteMutation.data.latency_ms} ms</dd>
                                      </div>
                                      <div>
                                        <dt>{tCat.pathDt}</dt>
                                        <dd>{manualExecuteMutation.data.execution_path}</dd>
                                      </div>
                                      <div>
                                        <dt>{tCat.providerModelDt}</dt>
                                        <dd>
                                          {manualExecuteMutation.data.provider} · {manualExecuteMutation.data.model}
                                        </dd>
                                      </div>
                                      <div>
                                        <dt>{tCat.tokensDt}</dt>
                                        <dd>
                                          {manualExecuteMutation.data.usage_input_tokens} /{" "}
                                          {manualExecuteMutation.data.usage_output_tokens}
                                        </dd>
                                      </div>
                                      <div>
                                        <dt>{tCat.gatewayRequestDt}</dt>
                                        <dd>
                                          <code>{manualExecuteMutation.data.gateway_request_id}</code>
                                        </dd>
                                      </div>
                                    </dl>
                                    <PromptDisclosure summary={tCat.disclosureRuntimeResolved}>
                                      <pre className="admin-prompts-code">
                                        {JSON.stringify(manualExecuteMutation.data.resolved_runtime_parameters, null, 2)}
                                      </pre>
                                    </PromptDisclosure>
                                    <PromptDisclosure summary={tCat.disclosurePromptSent}>
                                      <pre className="admin-prompts-code">{manualExecuteMutation.data.prompt_sent}</pre>
                                    </PromptDisclosure>
                                    {manualExecuteMutation.data.structured_output_parseable &&
                                    manualExecuteMutation.data.structured_output ? (
                                      <PromptDisclosure summary={tCat.disclosureStructuredOut}>
                                        <pre className="admin-prompts-code">
                                          {JSON.stringify(manualExecuteMutation.data.structured_output, null, 2)}
                                        </pre>
                                      </PromptDisclosure>
                                    ) : null}
                                    <PromptDisclosure summary={tCat.disclosureRawOut}>
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
                                    {tCat.manualExecSuccessNoData}
                                  </p>
                                ) : (
                                  <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                                    {selectedSamplePayloadId && resolvedQuery.data &&
                                    isAdminRuntimePreviewExecutable(resolvedQuery.data)
                                      ? tCat.manualExecHintReady
                                      : tCat.manualExecHintNeedSample}
                                  </p>
                                )
                              ) : null}
                            </>
                          ) : (
                            <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                              {tCat.manualExecPassToRuntime}
                            </p>
                          )}
                        </section>
                        <section className="admin-prompts-resolved__zone" aria-label={tCat.graphZoneAria}>
                          <h4>{tCat.graphZoneTitle}</h4>
                          <p className="text-muted">{tCat.graphIntro}</p>
                          {resolvedLogicGraph ? (
                            <AdminPromptsLogicGraph projection={resolvedLogicGraph} />
                          ) : (
                            <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                              {tCat.graphUnavailable ?? tCat.notAvailable}
                            </p>
                          )}
                          <details className="admin-prompts-detail__disclosure admin-prompts-detail__disclosure--sources">
                            <summary className="admin-prompts-detail__disclosure-summary">
                              {tCat.compositionSourcesSummary}
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
                                <span className="text-muted">{tCat.execProfileGridLabel}</span>
                                <span>
                                  {resolvedQuery.data.composition_sources.execution_profile.provider} /{" "}
                                  {resolvedQuery.data.composition_sources.execution_profile.model}
                                </span>
                                <span className="text-muted">{tCat.reasoningGridLabel}</span>
                                <span>
                                  {resolvedQuery.data.composition_sources.execution_profile.reasoning ?? tCat.notAvailable}
                                </span>
                                <span className="text-muted">{tCat.verbosityGridLabel}</span>
                                <span>
                                  {resolvedQuery.data.composition_sources.execution_profile.verbosity ?? tCat.notAvailable}
                                </span>
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
                  <p className="text-muted">{tCat.detailEmptySelectRow}</p>
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
                        const axisLabel = tCat.formatConsumptionAxisLabel(consumptionView, row)
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
                              const axisLabel = tCat.formatConsumptionAxisLabel(consumptionView, row)
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
                          tCat.formatConsumptionAxisLabel(consumptionView, selectedConsumptionRow),
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
                                  {tCat.consumptionUnknownFeatureCell(item.feature ?? null, item.subfeature ?? null)}
                                </td>
                                <td>{item.provider ?? tCat.consumptionUnknownProvider}</td>
                                <td>{item.active_snapshot_version ?? item.manifest_entry_id ?? tCat.notAvailable}</td>
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

              {legacyUseCaseKey ? (
                <AdminPromptEditorPanel
                  useCaseKey={legacyUseCaseKey}
                  useCaseDisplayName={selectedLegacyUseCase?.display_name ?? legacyUseCaseKey}
                  versions={selectedLegacyHistory}
                  activeVersion={activeLegacyVersion}
                  useCases={useCases}
                  strings={tEditor}
                  saveError={legacyEditorErrorMessage}
                  saveSuccess={legacyEditorSuccessMessage}
                  isPending={createPromptDraftMutation.isPending}
                  onSubmit={handleLegacyCreateDraft}
                />
              ) : null}

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
                              {version.published_at ? (
                                <p className="admin-prompts-history__copy text-muted">
                                  {tLegacy.publishedLine(
                                    formatLegacyPromptTimestamp(version.published_at, lang),
                                  )}
                                </p>
                              ) : null}
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
        <section className="panel admin-prompts-release" aria-label={tCat.releaseRegionAria}>
          {releaseTimelineQuery.isPending ? <div className="loading-placeholder">{tCat.releaseLoadingTimeline}</div> : null}
          {releaseTimelineQuery.isError ? <p className="chat-error">{tCat.releaseErrorTimeline}</p> : null}
          {!releaseTimelineQuery.isPending && !releaseTimelineQuery.isError && releaseTimeline.length === 0 ? (
            <div className="state-line">{tCat.releaseEmptySnapshots}</div>
          ) : null}
          {!releaseTimelineQuery.isPending && !releaseTimelineQuery.isError && releaseTimeline.length > 0 ? (
            <div className="admin-prompts-release__surface">
              <header className="admin-prompts-release__surface-header">
                <p className="admin-prompts-release__kicker">{tCat.releaseKicker}</p>
                <h3 className="admin-prompts-release__surface-title">{tCat.releaseSurfaceTitle}</h3>
                <p className="admin-prompts-release__surface-intro text-muted">{tCat.releaseSurfaceIntro}</p>
              </header>

              <section className="admin-prompts-release__section" aria-labelledby="release-timeline-heading">
                <div className="admin-prompts-release__section-head">
                  <h4 id="release-timeline-heading" className="admin-prompts-release__section-heading">
                    {tCat.releaseTimelineHeading}
                  </h4>
                  <p className="admin-prompts-release__section-hint text-muted">{tCat.releaseTimelineHint}</p>
                </div>
                <div className="admin-prompts-release__timeline">
                  {releaseTimeline.map((item) => (
                    <article key={`${item.snapshot_id}-${item.occurred_at}`} className="admin-prompts-release__timeline-item">
                      <div className="admin-prompts-release__timeline-top">
                        <strong>{item.snapshot_version}</strong>
                        <span
                          className={`badge ${item.release_health_status === "degraded" || item.release_health_status === "rollback_recommended" ? "badge--warning" : "badge--info"}`}
                        >
                          {tCat.labelReleaseHealthStatus(item.release_health_status)}
                        </span>
                      </div>
                      <p className="text-muted">
                        {tCat.releaseEventLine(
                          tCat.labelReleaseEventType(item.event_type),
                          new Date(item.occurred_at).toLocaleString(),
                          tCat.manifestEntriesCount(item.manifest_entry_count),
                        )}
                      </p>
                      <p className="text-muted">
                        {tCat.releaseCurrentLine(tCat.labelReleaseCurrentStatus(item.current_status), item.status_history.length)}
                      </p>
                      {item.from_snapshot_id ? (
                        <p className="text-muted">
                          {tCat.releaseRollbackLine(
                            formatReleaseSnapshotIdShort(item.from_snapshot_id),
                            item.to_snapshot_id ? formatReleaseSnapshotIdShort(item.to_snapshot_id) : "—",
                          )}
                        </p>
                      ) : null}
                      {item.reason ? (
                        <p className="text-muted">
                          <span className="admin-prompts-release__reason-label">{tCat.releaseReasonPrefix}</span>
                          {item.reason}
                        </p>
                      ) : null}
                      <div className="admin-prompts-release__proofs-block">
                        <p className="admin-prompts-release__proofs-lead text-muted">{tCat.releaseProofsLead}</p>
                        <div className="admin-prompts-release__proofs">
                          {item.proof_summaries.map((proof) => (
                            <span
                              key={`${item.snapshot_id}-${proof.proof_type}`}
                              className={`badge ${proof.status === "missing" || proof.verdict === "uncorrelated" ? "badge--warning" : "badge--info"}`}
                            >
                              {tCat.labelReleaseProofType(proof.proof_type)}:{" "}
                              {tCat.labelReleaseProofOutcome(proof.verdict, proof.status)}
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
                    {tCat.releaseCompareHeading}
                  </h4>
                  <p className="admin-prompts-release__section-hint text-muted">{tCat.releaseCompareHint}</p>
                </div>
                <div className="admin-prompts-release__diff-controls">
                  <label className="admin-prompts-compare">
                    <span>{tCat.releaseSnapshotSourceLabel}</span>
                    <select value={fromSnapshotId ?? ""} onChange={(event) => setFromSnapshotId(event.target.value)}>
                      {releaseSnapshots.map((item) => (
                        <option key={`from-${item.snapshot_id}`} value={item.snapshot_id}>
                          {item.snapshot_version} ({item.snapshot_id.slice(0, 8)})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="admin-prompts-compare">
                    <span>{tCat.releaseSnapshotTargetLabel}</span>
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

              {releaseDiffQuery.isPending ? <div className="loading-placeholder">{tCat.releaseDiffLoading}</div> : null}
              {releaseDiffQuery.isError ? <p className="chat-error">{tCat.releaseDiffError}</p> : null}
              {releaseDiffQuery.data ? (
                <div className="admin-prompts-release__diff panel">
                  <h3 className="admin-prompts-release__diff-title">{tCat.releaseDiffTitle}</h3>
                  <div className="admin-prompts-release__compare-banner" aria-label={tCat.releaseCompareBannerAria}>
                    <div className="admin-prompts-release__compare-card">
                      <span className="admin-prompts-release__compare-role">{tCat.releaseCompareRoleSource}</span>
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
                      <span className="admin-prompts-release__compare-role">{tCat.releaseCompareRoleTarget}</span>
                      <strong>
                        {selectedTimelineById[releaseDiffQuery.data.to_snapshot_id]?.snapshot_version ??
                          releaseDiffQuery.data.to_snapshot_id}
                      </strong>
                      <code className="admin-prompts-release__compare-id">
                        {formatReleaseSnapshotIdShort(releaseDiffQuery.data.to_snapshot_id)}
                      </code>
                    </div>
                  </div>
                  <h4 className="admin-prompts-release__diff-table-heading">{tCat.releaseDiffTableHeading}</h4>
                  <p className="admin-prompts-release__diff-table-lead text-muted">{tCat.releaseDiffTableLead}</p>
                  <div className="admin-prompts-catalog__table-wrap">
                    <table className="admin-prompts-catalog__table">
                      <thead>
                        <tr>
                          <th>{tCat.releaseDiffColManifest}</th>
                          <th>{tCat.releaseDiffColScope}</th>
                          <th>{tCat.releaseDiffColAssembly}</th>
                          <th>{tCat.releaseDiffColExec}</th>
                          <th>{tCat.releaseDiffColContract}</th>
                          <th>{tCat.releaseDiffColCatalog}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {releaseDiffQuery.data.entries.map((entry) => (
                          <tr key={`diff-${entry.manifest_entry_id}`}>
                            <td>
                              <code>{entry.manifest_entry_id}</code>
                            </td>
                            <td>{tCat.releaseDiffCategoryLabel(entry.category)}</td>
                            <td>
                              <span className={releaseDiffAxisBadgeClass(entry.assembly_changed)}>
                                {entry.assembly_changed ? tCat.releaseDiffChanged : tCat.releaseDiffUnchanged}
                              </span>
                            </td>
                            <td>
                              <span className={releaseDiffAxisBadgeClass(entry.execution_profile_changed)}>
                                {entry.execution_profile_changed ? tCat.releaseDiffChanged : tCat.releaseDiffUnchanged}
                              </span>
                            </td>
                            <td>
                              <span className={releaseDiffAxisBadgeClass(entry.output_contract_changed)}>
                                {entry.output_contract_changed ? tCat.releaseDiffChanged : tCat.releaseDiffUnchanged}
                              </span>
                            </td>
                            <td>
                              <button
                                className="text-button admin-prompts-catalog__inspect admin-prompts-release__catalog-link"
                                type="button"
                                aria-label={tCat.releaseOpenCatalogAria(entry.manifest_entry_id)}
                                onClick={() => {
                                  navigate(`${ADMIN_PROMPTS_BASE}/catalog`)
                                  setSelectedManifestEntryId(entry.manifest_entry_id)
                                }}
                              >
                                <span className="admin-prompts-release__catalog-link-title">{tCat.releaseOpenCatalogTitle}</span>
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

      {activeTab === "catalog" && selectedCatalogFlowNode ? (
        <AdminPromptCatalogNodeModal
          node={selectedCatalogFlowNode}
          useCases={useCases}
          versions={catalogHistory}
          activeVersion={activeCatalogVersion}
          useCaseDisplayName={selectedCatalogUseCase?.display_name ?? null}
          editorStrings={tEditor}
          saveError={catalogEditorErrorMessage}
          saveSuccess={catalogEditorSuccessMessage}
          isPending={createPromptDraftMutation.isPending}
          onClose={() => {
            setCatalogModalNodeId(null)
            setCatalogEditorSuccessMessage(null)
            setCatalogEditorErrorMessage(null)
          }}
          onSubmit={handleCatalogCreateDraft}
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
          inspectionModeLabel={tCat.inspectionModeFullLabel(resolvedInspectionMode)}
          catalog={tCat}
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

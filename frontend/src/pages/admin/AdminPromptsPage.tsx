import { useEffect, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"

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
  type AdminConsumptionView,
  type AdminPromptVersion,
  type AdminInspectionMode,
  type AdminResolvedPlaceholder,
  type AdminResolvedAssemblyView,
  type SnapshotTimelineItem,
} from "@api"
import { PersonasAdmin } from "./PersonasAdmin"
import "./AdminPromptsPage.css"

type PromptPageTab = "catalog" | "legacy" | "release" | "consumption" | "personas"

type LegacyRollbackModalProps = {
  isPending: boolean
  useCaseKey: string
  version: AdminPromptVersion
  onCancel: () => void
  onConfirm: () => void
}

function LegacyRollbackModal({
  isPending,
  useCaseKey,
  version,
  onCancel,
  onConfirm,
}: LegacyRollbackModalProps) {
  return (
    <div className="modal-overlay" role="presentation">
      <div className="modal-content admin-prompts-modal" aria-labelledby="legacy-rollback-title" role="dialog" aria-modal="true">
        <h3 id="legacy-rollback-title">Confirmer le rollback legacy</h3>
        <p className="admin-prompts-modal__copy">
          Le use case <strong>{useCaseKey}</strong> sera republié sur la version <code>{version.id}</code>.
        </p>
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            Annuler
          </button>
          <button className="action-button action-button--primary" type="button" disabled={isPending} onClick={onConfirm}>
            {isPending ? "Rollback en cours..." : "Rollback"}
          </button>
        </div>
      </div>
    </div>
  )
}

type DiffRow = {
  leftText: string
  rightText: string
  leftType: "unchanged" | "removed"
  rightType: "unchanged" | "added"
}

type LogicGraphNodeTone = "neutral" | "layer" | "system" | "fallback" | "sample"

type LogicGraphNode = {
  id: string
  title: string
  detail: string
  tone: LogicGraphNodeTone
}

type LogicGraphEdge = {
  from: string
  to: string
  label: string
}

type LogicGraphProjection = {
  nodes: LogicGraphNode[]
  edges: LogicGraphEdge[]
  dense: boolean
  fallbackSummary: string[]
}

function classifyPlaceholderSource(item: AdminResolvedPlaceholder): LogicGraphNodeTone | "runtime" {
  const source = (item.resolution_source ?? "").toLowerCase()
  if (source.includes("sample")) return "sample"
  if (source.includes("fallback")) return "fallback"
  if (
    source.includes("runtime") ||
    source === "static_preview_gap" ||
    source === "missing_required" ||
    item.status === "expected_missing_in_preview" ||
    item.status === "blocking_missing"
  ) {
    return "runtime"
  }
  return "neutral"
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

function inspectionModeHelpText(mode: AdminInspectionMode): string {
  switch (mode) {
    case "assembly_preview":
      return "Prévisualisation statique: les placeholders attendus uniquement au runtime restent signalés comme absents mais non bloquants."
    case "runtime_preview":
      return "Prévisualisation runtime: les placeholders requis manquants sont traités comme bloquants selon la sémantique nominale."
    case "live_execution":
      return "Inspection live: même sémantique placeholder que runtime_preview pour l’instant. Cette vue n’exécute pas encore le provider."
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

function buildLogicGraphProjection(resolvedView: AdminResolvedAssemblyView): LogicGraphProjection {
  const placeholderStats = resolvedView.resolved_result.placeholders.reduce(
    (acc, item) => {
      const category = classifyPlaceholderSource(item)
      if (category === "fallback") {
        acc.fallback += 1
      } else if (category === "sample") {
        acc.sample += 1
      } else if (category === "runtime") {
        acc.runtime += 1
      }
      return acc
    },
    { runtime: 0, fallback: 0, sample: 0 },
  )
  const hasSubfeatureTemplate = Boolean(resolvedView.composition_sources.subfeature_template)
  const hasPlanRules = Boolean(resolvedView.composition_sources.plan_rules?.content)
  const hasPersonaBlock = Boolean(resolvedView.composition_sources.persona_block?.content)
  const dense = resolvedView.resolved_result.placeholders.length >= 16

  const nodes: LogicGraphNode[] = [
    { id: "manifest", title: "manifest_entry_id", detail: resolvedView.manifest_entry_id, tone: "neutral" },
    {
      id: "composition",
      title: "composition_sources",
      detail: `${resolvedView.feature}/${resolvedView.subfeature ?? "-"} · plan ${resolvedView.plan ?? "-"}`,
      tone: "neutral",
    },
    { id: "feature", title: "feature template", detail: resolvedView.composition_sources.feature_template.id, tone: "layer" },
    {
      id: "subfeature",
      title: "subfeature template",
      detail: hasSubfeatureTemplate ? (resolvedView.composition_sources.subfeature_template?.id ?? "actif") : "absent",
      tone: "layer",
    },
    {
      id: "planRules",
      title: "plan rules",
      detail: hasPlanRules ? (resolvedView.composition_sources.plan_rules?.ref ?? "actif") : "absent",
      tone: "layer",
    },
    {
      id: "persona",
      title: "persona block",
      detail: hasPersonaBlock ? (resolvedView.composition_sources.persona_block?.name ?? "actif") : "absent",
      tone: "layer",
    },
    {
      id: "hardPolicy",
      title: "hard policy",
      detail: resolvedView.composition_sources.hard_policy.safety_profile,
      tone: "system",
    },
    {
      id: "executionProfile",
      title: "execution profile",
      detail: `${resolvedView.composition_sources.execution_profile.provider}/${resolvedView.composition_sources.execution_profile.model}`,
      tone: "system",
    },
    { id: "pipeline", title: "transformation_pipeline", detail: "assembled -> injectors -> rendered", tone: "neutral" },
    {
      id: "providerMessages",
      title: "provider_messages",
      detail: `context_quality: ${resolvedView.resolved_result.context_compensation_status}`,
      tone: "system",
    },
    {
      id: "runtimeInputs",
      title: "runtime inputs",
      detail: `runtime:${placeholderStats.runtime} · fallback:${placeholderStats.fallback} · sample:${placeholderStats.sample}`,
      tone: "neutral",
    },
    {
      id: "fallbackRegistry",
      title: "fallbacks registre",
      detail: `${placeholderStats.fallback} placeholder(s)`,
      tone: "fallback",
    },
    {
      id: "samplePayloads",
      title: "sample payloads",
      detail: `${placeholderStats.sample} placeholder(s)`,
      tone: "sample",
    },
  ]

  const edges: LogicGraphEdge[] = [
    { from: "manifest", to: "composition", label: "résout la cible canonique" },
    { from: "composition", to: "feature", label: "couche" },
    { from: "composition", to: "subfeature", label: hasSubfeatureTemplate ? "couche" : "optionnel" },
    { from: "composition", to: "planRules", label: hasPlanRules ? "couche" : "optionnel" },
    { from: "composition", to: "persona", label: hasPersonaBlock ? "couche" : "optionnel" },
    { from: "composition", to: "hardPolicy", label: "politique système" },
    { from: "composition", to: "executionProfile", label: "paramètres provider" },
    { from: "composition", to: "pipeline", label: "assemblage prompt" },
    { from: "hardPolicy", to: "providerMessages", label: "message system" },
    { from: "persona", to: "providerMessages", label: hasPersonaBlock ? "message persona" : "optionnel" },
    { from: "executionProfile", to: "providerMessages", label: "paramètres d'exécution" },
    { from: "pipeline", to: "providerMessages", label: "messages finaux" },
    { from: "runtimeInputs", to: "pipeline", label: "substitutions variables" },
    { from: "fallbackRegistry", to: "runtimeInputs", label: "fallbacks appliqués" },
    { from: "samplePayloads", to: "runtimeInputs", label: "données de test" },
  ]

  return {
    nodes,
    edges,
    dense,
    fallbackSummary: [
      `manifest_entry_id: ${resolvedView.manifest_entry_id}`,
      `composition_sources -> transformation_pipeline -> provider_messages`,
      `runtime inputs: runtime=${placeholderStats.runtime}, fallback=${placeholderStats.fallback}, sample=${placeholderStats.sample}`,
      `couches: feature template, subfeature template, plan rules, persona block, hard policy, execution profile`,
    ],
  }
}

export function AdminPromptsPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<PromptPageTab>("catalog")

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
  const [selectedDrilldownKey, setSelectedDrilldownKey] = useState<string | null>(null)
  const consumptionFromUtc = consumptionFrom ? toUtcIsoFromDateTimeInput(consumptionFrom) : undefined
  const consumptionToUtc = consumptionTo ? toUtcIsoFromDateTimeInput(consumptionTo) : undefined
  const effectiveSamplePayloadId =
    resolvedInspectionMode === "runtime_preview" ? selectedSamplePayloadId : null

  const catalogQuery = useAdminLlmCatalog({
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
  }, activeTab === "catalog")

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
  const samplePayloadsQuery = useAdminLlmSamplePayloads(
    selectedCatalogEntry?.feature ?? null,
    selectedCatalogEntry?.locale ?? null,
    activeTab === "catalog" &&
      Boolean(selectedManifestEntryId) &&
      resolvedInspectionMode === "runtime_preview",
  )

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
    if (resolvedInspectionMode !== "runtime_preview") return
    const recommendedId = samplePayloadsQuery.data?.recommended_default_id ?? null
    if (!recommendedId) {
      setSelectedSamplePayloadId(null)
      return
    }
    setSelectedSamplePayloadId((current) => current ?? recommendedId)
  }, [resolvedInspectionMode, samplePayloadsQuery.data?.recommended_default_id])

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

  const useCasesQuery = useAdminLlmUseCases()
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
  const selectedConsumptionRow = consumptionQuery.data?.data.find((item) => {
    const key = `${item.period_start_utc}::${item.user_id ?? "none"}::${item.subscription_plan ?? "none"}::${item.feature ?? "none"}::${item.subfeature ?? "none"}`
    return key === selectedDrilldownKey
  })
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
  const activeLegacyVersion =
    selectedLegacyHistory.find((item) => item.id === selectedLegacyUseCase?.active_prompt_version_id) ??
    selectedLegacyHistory[0] ??
    null
  const compareLegacyVersion =
    selectedLegacyHistory.find((item) => item.id === legacyCompareVersionId) ??
    selectedLegacyHistory.find((item) => item.id !== activeLegacyVersion?.id) ??
    null
  const legacyDiffRows =
    activeLegacyVersion && compareLegacyVersion
      ? buildDiffRows(compareLegacyVersion.developer_prompt, activeLegacyVersion.developer_prompt)
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
    const defaultCompareId =
      selectedLegacyHistory.find((version) => version.id !== activeLegacyVersion?.id)?.id ?? null
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
    await rollbackMutation.mutateAsync({
      useCaseKey: legacyUseCaseKey,
      targetVersionId: legacyRollbackCandidate.id,
    })
    setLegacyRollbackCandidate(null)
    setSuccessMessage(`Rollback effectue vers ${legacyRollbackCandidate.id.slice(0, 8)}.`)
    await queryClient.invalidateQueries({ queryKey: ["admin-llm-prompt-history", legacyUseCaseKey] })
    await queryClient.invalidateQueries({ queryKey: ["admin-llm-catalog"] })
  }

  return (
    <div className="admin-prompts-page">
      <header className="admin-page-header">
        <div>
          <h2>Catalogue prompts LLM</h2>
          <p className="admin-prompts-page__intro">
            Vue canonique feature/subfeature/plan/locale gouvernée par snapshot actif, avec historique legacy séparé.
          </p>
        </div>
        <div className="admin-tabs" role="tablist" aria-label="Sections prompts">
          <button className={`tab-button ${activeTab === "catalog" ? "tab-button--active" : ""}`} type="button" role="tab" aria-selected={activeTab === "catalog"} onClick={() => setActiveTab("catalog")}>
            Catalogue canonique
          </button>
          <button className={`tab-button ${activeTab === "legacy" ? "tab-button--active" : ""}`} type="button" role="tab" aria-selected={activeTab === "legacy"} onClick={() => setActiveTab("legacy")}>
            Historique legacy
          </button>
          <button className={`tab-button ${activeTab === "release" ? "tab-button--active" : ""}`} type="button" role="tab" aria-selected={activeTab === "release"} onClick={() => setActiveTab("release")}>
            Historique release
          </button>
          <button className={`tab-button ${activeTab === "consumption" ? "tab-button--active" : ""}`} type="button" role="tab" aria-selected={activeTab === "consumption"} onClick={() => setActiveTab("consumption")}>
            Consommation
          </button>
          <button className={`tab-button ${activeTab === "personas" ? "tab-button--active" : ""}`} type="button" role="tab" aria-selected={activeTab === "personas"} onClick={() => setActiveTab("personas")}>
            Personas
          </button>
        </div>
      </header>

      {activeTab === "personas" ? <PersonasAdmin /> : null}

      {activeTab === "catalog" ? (
        <section className="panel admin-prompts-catalog" aria-label="Catalogue canonique">
          <div className="admin-prompts-catalog__filters">
            <input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1) }} placeholder="Recherche tuple canonique / manifest_entry_id" />
            <select value={feature} onChange={(event) => { setFeature(event.target.value); setPage(1) }}>
              <option value="">Feature</option>
              {availableFeatures.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select value={subfeature} onChange={(event) => { setSubfeature(event.target.value); setPage(1) }}>
              <option value="">Subfeature</option>
              {availableSubfeatures.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select value={plan} onChange={(event) => { setPlan(event.target.value); setPage(1) }}>
              <option value="">Plan</option>
              {availablePlans.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select value={locale} onChange={(event) => { setLocale(event.target.value); setPage(1) }}>
              <option value="">Locale</option>
              {availableLocales.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select value={provider} onChange={(event) => { setProvider(event.target.value); setPage(1) }}>
              <option value="">Provider</option>
              {availableProviders.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select value={sourceOfTruthStatus} onChange={(event) => { setSourceOfTruthStatus(event.target.value); setPage(1) }}>
              <option value="">Source of truth</option>
              {availableSourceStatuses.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select value={assemblyStatus} onChange={(event) => { setAssemblyStatus(event.target.value); setPage(1) }}>
              <option value="">Assembly status</option>
              {availableAssemblyStatuses.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select value={releaseHealthStatus} onChange={(event) => { setReleaseHealthStatus(event.target.value); setPage(1) }}>
              <option value="">Release health</option>
              {availableReleaseHealthStatuses.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select value={catalogVisibilityStatus} onChange={(event) => { setCatalogVisibilityStatus(event.target.value); setPage(1) }}>
              <option value="">Visibility</option>
              {availableVisibilityStatuses.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
            <select
              aria-label="Tri catalogue"
              value={sortBy}
              onChange={(event) => { setSortBy(event.target.value); setPage(1) }}
            >
              <option value="feature">Tri: Feature</option>
              <option value="subfeature">Tri: Subfeature</option>
              <option value="plan">Tri: Plan</option>
              <option value="locale">Tri: Locale</option>
              <option value="manifest_entry_id">Tri: Manifest entry</option>
              <option value="provider">Tri: Provider</option>
              <option value="source_of_truth_status">Tri: Source of truth</option>
              <option value="assembly_status">Tri: Assembly status</option>
              <option value="release_health_status">Tri: Release health</option>
              <option value="catalog_visibility_status">Tri: Visibility</option>
            </select>
            <select
              aria-label="Ordre tri catalogue"
              value={sortOrder}
              onChange={(event) => { setSortOrder(event.target.value as "asc" | "desc"); setPage(1) }}
            >
              <option value="asc">Ordre: Ascendant</option>
              <option value="desc">Ordre: Descendant</option>
            </select>
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
                      <th>Assembly</th>
                      <th>Execution profile</th>
                      <th>Output contract</th>
                      <th>Source de verite</th>
                      <th>Snapshot actif</th>
                      <th>Manifest entry</th>
                      <th>Provider / model</th>
                      <th>Signals runtime</th>
                    </tr>
                  </thead>
                  <tbody>
                    {catalogEntries.map((entry) => (
                      <tr key={entry.manifest_entry_id}>
                        <td>{entry.feature}/{entry.subfeature ?? "-"}/{entry.plan ?? "-"}/{entry.locale ?? "-"}</td>
                        <td>{entry.assembly_id ?? "-"} <span className="text-muted">({entry.assembly_status})</span></td>
                        <td>{entry.execution_profile_ref ?? "-"}</td>
                        <td>{entry.output_contract_ref ?? "-"}</td>
                        <td>
                          <span className={`badge ${entry.source_of_truth_status === "active_snapshot" ? "badge--info" : "badge--warning"}`}>
                            {entry.source_of_truth_status}
                          </span>
                          <div className="text-muted">
                            health: {entry.release_health_status} · visibility: {entry.catalog_visibility_status}
                          </div>
                        </td>
                        <td>{entry.active_snapshot_id ? `${entry.active_snapshot_version} (${entry.active_snapshot_id.slice(0, 8)}...)` : "n/a"}</td>
                        <td><code>{entry.manifest_entry_id}</code></td>
                        <td>{entry.provider ?? "-"} / {entry.model ?? "-"}</td>
                        <td>
                          <div>{entry.runtime_signal_status}</div>
                          <div className="text-muted">{entry.execution_path_kind ?? "n/a"} · {entry.context_compensation_status ?? "n/a"} · {entry.max_output_tokens_source ?? "n/a"}</div>
                          <button
                            className="text-button admin-prompts-catalog__inspect"
                            type="button"
                            onClick={() => setSelectedManifestEntryId(entry.manifest_entry_id)}
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

              {selectedManifestEntryId ? (
                <section className="panel admin-prompts-resolved" aria-label="Détail assembly résolue">
                  <div className="admin-prompts-resolved__header">
                    <h3>Assembly prompt résolue</h3>
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
                      {resolvedInspectionMode === "runtime_preview" ? (
                        <label className="admin-prompts-resolved__mode-field">
                          <span className="text-muted">Sample payload</span>
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
                      ) : null}
                    </div>
                  </div>
                  <p className="admin-prompts-resolved__render-note">
                    {inspectionModeHelpText(resolvedQuery.data?.inspection_mode ?? resolvedInspectionMode)}
                  </p>
                  {resolvedInspectionMode === "runtime_preview" && samplePayloadsQuery.isPending ? (
                    <p className="text-muted">Chargement des sample payloads...</p>
                  ) : null}
                  {resolvedQuery.isPending ? <div className="loading-placeholder">Chargement du detail...</div> : null}
                  {resolvedQuery.isError ? <AdminPromptsResolvedAssemblyError error={resolvedQuery.error} /> : null}
                  {resolvedQuery.data ? (
                    <>
                      <section className="admin-prompts-logic-graph" aria-label="Construction logique">
                        <h4>Construction logique</h4>
                        <p className="text-muted">
                          Graphe inspectable de la chaîne canonique: sources de composition, pipeline de transformation et données runtime.
                        </p>
                        <div className="admin-prompts-logic-graph__legend" aria-label="Légende du graphe">
                          <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--system">Données système</span>
                          <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--fallback">Fallback registre</span>
                          <span className="admin-prompts-logic-graph__legend-chip admin-prompts-logic-graph__legend-chip--sample">Sample payload</span>
                        </div>
                        {!logicGraph?.dense ? (
                          <>
                            <div className="admin-prompts-logic-graph__nodes">
                              {logicGraph?.nodes.map((node) => (
                                <article key={node.id} className={`admin-prompts-logic-graph__node admin-prompts-logic-graph__node--${node.tone}`}>
                                  <strong>{node.title}</strong>
                                  <span className="text-muted">{node.detail}</span>
                                </article>
                              ))}
                            </div>
                            <ul className="admin-prompts-logic-graph__edges" aria-label="Connexions du graphe">
                              {logicGraph?.edges.map((edge) => (
                                <li key={`${edge.from}-${edge.to}`}>
                                  <code>{edge.from}</code> → <code>{edge.to}</code> · {edge.label}
                                </li>
                              ))}
                            </ul>
                          </>
                        ) : (
                          <div className="admin-prompts-logic-graph__fallback" aria-live="polite">
                            <p className="text-muted">
                              Graphe simplifié en vue texte car la densité dépasse le seuil de lisibilité.
                            </p>
                            <ul>
                              {logicGraph?.fallbackSummary.map((line) => (
                                <li key={line}>{line}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </section>
                      <div className="admin-prompts-resolved__zones">
                        <section className="admin-prompts-resolved__zone" aria-label="Prompts">
                          <h4>Prompts</h4>
                          <p className="text-muted">
                            Source: {resolvedQuery.data.source_of_truth_status} · snapshot: {resolvedQuery.data.active_snapshot_version ?? "n/a"}
                          </p>
                          <p className="text-muted">assembled prompt</p>
                          <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.assembled_prompt}</pre>
                          <p className="text-muted">post injectors prompt</p>
                          <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.post_injectors_prompt}</pre>
                          <p className="text-muted">rendered prompt</p>
                          <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.rendered_prompt}</pre>
                          <p className="text-muted">system hard policy</p>
                          <pre className="admin-prompts-code">{String(resolvedQuery.data.resolved_result.provider_messages.system_hard_policy ?? "")}</pre>
                          <p className="text-muted">developer content</p>
                          <pre className="admin-prompts-code">{String(resolvedQuery.data.resolved_result.provider_messages.developer_content_rendered ?? "")}</pre>
                          <p className="text-muted">persona block</p>
                          <pre className="admin-prompts-code">{String(resolvedQuery.data.resolved_result.provider_messages.persona_block ?? "")}</pre>
                        </section>
                        <section className="admin-prompts-resolved__zone" aria-label="Données d'exemple">
                          <h4>Données d&apos;exemple</h4>
                          <p className="text-muted">
                            Placeholders résolus/partiels pour lecture opérable (sans parser du JSON brut).
                          </p>
                          {resolvedQuery.data.resolved_result.placeholders.length === 0 ? (
                            <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                              Aucune donnée d&apos;exemple disponible pour cette cible.
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
                          <p className="text-muted">Paramètres d&apos;exécution</p>
                          <pre className="admin-prompts-code">{JSON.stringify(resolvedQuery.data.resolved_result.provider_messages.execution_parameters, null, 2)}</pre>
                          <p className="text-muted">Sortie d&apos;exécution live</p>
                          <p className="admin-prompts-resolved__state" role="status" aria-live="polite">
                            Vide pour l&apos;instant: cette zone accueillera le retour provider des stories 69.x.
                          </p>
                        </section>
                        <section className="admin-prompts-resolved__zone" aria-label="Construction logique (sources)">
                          <h4>Construction logique (sources)</h4>
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
                              {resolvedQuery.data.composition_sources.execution_profile.provider} / {resolvedQuery.data.composition_sources.execution_profile.model}
                            </span>
                            <span className="text-muted">Reasoning</span>
                            <span>{resolvedQuery.data.composition_sources.execution_profile.reasoning ?? "n/a"}</span>
                            <span className="text-muted">Verbosity</span>
                            <span>{resolvedQuery.data.composition_sources.execution_profile.verbosity ?? "n/a"}</span>
                          </div>
                        </section>
                      </div>
                    </>
                  ) : null}
                </section>
              ) : null}
            </>
          ) : null}
        </section>
      ) : null}

      {activeTab === "consumption" ? (
        <section className="panel admin-prompts-catalog" aria-label="Dashboard consommation LLM">
          <div className="admin-prompts-catalog__filters">
            <select value={consumptionView} onChange={(event) => { setConsumptionView(event.target.value as AdminConsumptionView); setConsumptionPage(1); setSelectedDrilldownKey(null) }}>
              <option value="user">Vue par utilisateur</option>
              <option value="subscription">Vue par abonnement</option>
              <option value="feature">Vue par feature/subfeature</option>
            </select>
            <select value={consumptionGranularity} onChange={(event) => { setConsumptionGranularity(event.target.value as "day" | "month"); setConsumptionPage(1) }}>
              <option value="day">Granularité journalière</option>
              <option value="month">Granularité mensuelle</option>
            </select>
            <input type="datetime-local" value={consumptionFrom} onChange={(event) => { setConsumptionFrom(event.target.value); setConsumptionPage(1) }} />
            <input type="datetime-local" value={consumptionTo} onChange={(event) => { setConsumptionTo(event.target.value); setConsumptionPage(1) }} />
            <input value={consumptionSearch} onChange={(event) => { setConsumptionSearch(event.target.value); setConsumptionPage(1) }} placeholder="Recherche utilisateur / abonnement / feature" />
            <button
              className="text-button"
              type="button"
              onClick={async () => {
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
                URL.revokeObjectURL(url)
              }}
              disabled={exportCsvMutation.isPending}
            >
              {exportCsvMutation.isPending ? "Export en cours..." : "Export CSV"}
            </button>
          </div>
          <p className="text-muted">Granularité par défaut: agrégé par période sélectionnée ({consumptionGranularity}).</p>
          {consumptionQuery.isPending ? <div className="loading-placeholder">Chargement consommation...</div> : null}
          {consumptionQuery.isError ? <p className="chat-error">Impossible de charger la consommation.</p> : null}
          {consumptionQuery.data ? (
            <>
              <div className="admin-prompts-catalog__table-wrap">
                <table className="admin-prompts-catalog__table">
                  <thead>
                    <tr>
                      <th>Période</th>
                      <th>Axe</th>
                      <th>Requêtes</th>
                      <th>Tokens in/out/total</th>
                      <th>Coût estimé</th>
                      <th>Latence moyenne</th>
                      <th>Taux erreur</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {consumptionQuery.data.data.map((row) => {
                      const rowKey = `${row.period_start_utc}::${row.user_id ?? "none"}::${row.subscription_plan ?? "none"}::${row.feature ?? "none"}::${row.subfeature ?? "none"}`
                      return (
                        <tr key={rowKey}>
                          <td>{new Date(row.period_start_utc).toLocaleString()}</td>
                          <td>
                            {consumptionView === "user" ? (row.user_email ?? `user:${row.user_id ?? "n/a"}`) : null}
                            {consumptionView === "subscription" ? (row.subscription_plan ?? "unknown") : null}
                            {consumptionView === "feature" ? `${row.feature ?? "unknown"} / ${row.subfeature ?? "-"}` : null}
                          </td>
                          <td>{row.request_count}</td>
                          <td>{row.input_tokens} / {row.output_tokens} / {row.total_tokens}</td>
                          <td>{row.estimated_cost.toFixed(4)} $</td>
                          <td>{row.avg_latency_ms.toFixed(1)} ms</td>
                          <td>{(row.error_rate * 100).toFixed(2)}%</td>
                          <td>
                            <button className="text-button" type="button" onClick={() => setSelectedDrilldownKey(rowKey)}>
                              Voir logs récents
                            </button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              <div className="admin-prompts-catalog__footer">
                <span>{consumptionQuery.data.meta.count} lignes</span>
                <div className="admin-prompts-catalog__pagination">
                  <button className="text-button" type="button" onClick={() => setConsumptionPage((value) => Math.max(1, value - 1))} disabled={consumptionPage <= 1}>
                    Précédent
                  </button>
                  <span>Page {consumptionQuery.data.meta.page}</span>
                  <button className="text-button" type="button" onClick={() => setConsumptionPage((value) => value + 1)} disabled={consumptionQuery.data.meta.page * consumptionQuery.data.meta.page_size >= consumptionQuery.data.meta.count}>
                    Suivant
                  </button>
                </div>
              </div>
              {selectedConsumptionRow ? (
                <section className="panel" aria-label="Drill-down appels LLM récents">
                  <h3>Drill-down appels récents (50 max)</h3>
                  {consumptionDrilldownQuery.isPending ? <div className="loading-placeholder">Chargement drill-down...</div> : null}
                  {consumptionDrilldownQuery.isError ? <p className="chat-error">Impossible de charger les logs corrélés.</p> : null}
                  {consumptionDrilldownQuery.data ? (
                    <div className="admin-prompts-catalog__table-wrap">
                      <table className="admin-prompts-catalog__table">
                        <thead>
                          <tr>
                            <th>timestamp</th>
                            <th>request_id</th>
                            <th>feature/subfeature</th>
                            <th>provider</th>
                            <th>snapshot/manifest</th>
                            <th>validation_status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {consumptionDrilldownQuery.data.data.map((item) => (
                            <tr key={`${item.request_id}-${item.timestamp}`}>
                              <td>{new Date(item.timestamp).toLocaleString()}</td>
                              <td><code>{item.request_id}</code></td>
                              <td>{item.feature ?? "unknown"} / {item.subfeature ?? "-"}</td>
                              <td>{item.provider ?? "unknown"}</td>
                              <td>{item.active_snapshot_version ?? item.manifest_entry_id ?? "n/a"}</td>
                              <td>{item.validation_status}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : null}
                </section>
              ) : null}
            </>
          ) : null}
        </section>
      ) : null}

      {activeTab === "legacy" ? (
        <section className="panel" aria-label="Historique legacy prompt/persona">
          {successMessage ? <p className="state-line state-success">{successMessage}</p> : null}
          {isLegacyLoading ? <div className="loading-placeholder">Chargement de l'historique legacy...</div> : null}
          {hasLegacyError ? <p className="chat-error">Impossible de charger l'historique legacy.</p> : null}

          {!isLegacyLoading && !hasLegacyError ? (
            <div className="admin-prompts-history-legacy">
              <label className="admin-prompts-compare">
                <span>Use case legacy</span>
                <select value={legacyUseCaseKey ?? ""} onChange={(event) => setLegacyUseCaseKey(event.target.value)}>
                  {useCases.map((useCase) => (
                    <option key={useCase.key} value={useCase.key}>
                      {useCase.display_name} ({useCase.key})
                    </option>
                  ))}
                </select>
              </label>
              <div className="admin-prompts-history">
                {selectedLegacyHistory.map((version) => (
                  <article key={version.id} className="admin-prompts-history__item">
                    <div>
                      <div className="admin-prompts-history__topline">
                        <strong>{version.status}</strong>
                        <span className="text-muted">{version.model}</span>
                      </div>
                      <p className="admin-prompts-history__copy">
                        Auteur {version.created_by} · {version.created_at}
                      </p>
                      <code>{version.id}</code>
                    </div>
                    <div className="admin-prompts-history__actions">
                      <button className="action-button action-button--secondary" type="button" onClick={() => setLegacyRollbackCandidate(version)}>
                        Rollback
                      </button>
                    </div>
                  </article>
                ))}
              </div>
              {activeLegacyVersion && compareLegacyVersion ? (
                <div className="panel">
                  <div className="admin-prompts-history__header">
                    <h3>Comparaison legacy</h3>
                    <label className="admin-prompts-compare">
                      <span>Comparer avec</span>
                      <select
                        aria-label="Comparer version legacy"
                        value={compareLegacyVersion.id}
                        onChange={(event) => setLegacyCompareVersionId(event.target.value)}
                      >
                        {selectedLegacyHistory
                          .filter((version) => version.id !== activeLegacyVersion.id)
                          .map((version) => (
                            <option key={version.id} value={version.id}>
                              {version.id} · {version.status}
                            </option>
                          ))}
                      </select>
                    </label>
                  </div>
                  <div className="admin-prompts-diff" role="table" aria-label="Diff prompt legacy">
                    <div className="admin-prompts-diff__column admin-prompts-diff__column--left">
                      <h4>Version comparée</h4>
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
                      <h4>Version active</h4>
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
                </div>
              ) : null}
            </div>
          ) : null}
        </section>
      ) : null}

      {activeTab === "release" ? (
        <section className="panel admin-prompts-release" aria-label="Historique release snapshots">
          {releaseTimelineQuery.isPending ? <div className="loading-placeholder">Chargement de la timeline release...</div> : null}
          {releaseTimelineQuery.isError ? <p className="chat-error">Impossible de charger la timeline release.</p> : null}
          {!releaseTimelineQuery.isPending && !releaseTimelineQuery.isError && releaseTimeline.length === 0 ? (
            <div className="state-line">Aucun snapshot disponible.</div>
          ) : null}
          {!releaseTimelineQuery.isPending && !releaseTimelineQuery.isError && releaseTimeline.length > 0 ? (
            <>
              <div className="admin-prompts-release__header">
                <h3>Timeline snapshots</h3>
                <p className="text-muted">Unité de lecture: release snapshot, avec statut courant, historique et preuves corrélées.</p>
              </div>
              <div className="admin-prompts-release__timeline">
                {releaseTimeline.map((item) => (
                  <article key={`${item.snapshot_id}-${item.occurred_at}`} className="admin-prompts-release__timeline-item">
                    <div className="admin-prompts-release__timeline-top">
                      <strong>{item.snapshot_version}</strong>
                      <span className={`badge ${item.release_health_status === "degraded" || item.release_health_status === "rollback_recommended" ? "badge--warning" : "badge--info"}`}>
                        {item.release_health_status}
                      </span>
                    </div>
                    <p className="text-muted">
                      {item.event_type} · {new Date(item.occurred_at).toLocaleString()} · entries: {item.manifest_entry_count}
                    </p>
                    <p className="text-muted">
                      current_status: {item.current_status} · status_history: {item.status_history.length}
                    </p>
                    {item.from_snapshot_id ? (
                      <p className="text-muted">rollback: {item.from_snapshot_id.slice(0, 8)}... → {item.to_snapshot_id?.slice(0, 8)}...</p>
                    ) : null}
                    {item.reason ? <p className="text-muted">{item.reason}</p> : null}
                    <div className="admin-prompts-release__proofs">
                      {item.proof_summaries.map((proof) => (
                        <span key={`${item.snapshot_id}-${proof.proof_type}`} className={`badge ${proof.status === "missing" || proof.verdict === "uncorrelated" ? "badge--warning" : "badge--info"}`}>
                          {proof.proof_type}: {proof.verdict ?? proof.status}
                        </span>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
              <div className="admin-prompts-release__diff-controls">
                <label className="admin-prompts-compare">
                  <span>Snapshot source</span>
                  <select value={fromSnapshotId ?? ""} onChange={(event) => setFromSnapshotId(event.target.value)}>
                    {releaseSnapshots.map((item) => (
                      <option key={`from-${item.snapshot_id}`} value={item.snapshot_id}>
                        {item.snapshot_version} ({item.snapshot_id.slice(0, 8)})
                      </option>
                    ))}
                  </select>
                </label>
                <label className="admin-prompts-compare">
                  <span>Snapshot cible</span>
                  <select value={toSnapshotId ?? ""} onChange={(event) => setToSnapshotId(event.target.value)}>
                    {releaseSnapshots.map((item) => (
                      <option key={`to-${item.snapshot_id}`} value={item.snapshot_id}>
                        {item.snapshot_version} ({item.snapshot_id.slice(0, 8)})
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              {releaseDiffQuery.isPending ? <div className="loading-placeholder">Chargement du diff snapshots...</div> : null}
              {releaseDiffQuery.isError ? <p className="chat-error">Impossible de charger le diff snapshots.</p> : null}
              {releaseDiffQuery.data ? (
                <div className="admin-prompts-release__diff panel">
                  <h3>Diff snapshot</h3>
                  <p className="text-muted">
                    from: {selectedTimelineById[releaseDiffQuery.data.from_snapshot_id]?.snapshot_version ?? releaseDiffQuery.data.from_snapshot_id} ·
                    to: {selectedTimelineById[releaseDiffQuery.data.to_snapshot_id]?.snapshot_version ?? releaseDiffQuery.data.to_snapshot_id}
                  </p>
                  <div className="admin-prompts-catalog__table-wrap">
                    <table className="admin-prompts-catalog__table">
                      <thead>
                        <tr>
                          <th>manifest_entry_id</th>
                          <th>catégorie</th>
                          <th>assembly</th>
                          <th>execution profile</th>
                          <th>output contract</th>
                          <th>navigation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {releaseDiffQuery.data.entries.map((entry) => (
                          <tr key={`diff-${entry.manifest_entry_id}`}>
                            <td><code>{entry.manifest_entry_id}</code></td>
                            <td>{entry.category}</td>
                            <td>{entry.assembly_changed ? "changed" : "stable"}</td>
                            <td>{entry.execution_profile_changed ? "changed" : "stable"}</td>
                            <td>{entry.output_contract_changed ? "changed" : "stable"}</td>
                            <td>
                              <button
                                className="text-button admin-prompts-catalog__inspect"
                                type="button"
                                onClick={() => {
                                  setActiveTab("catalog")
                                  setSelectedManifestEntryId(entry.manifest_entry_id)
                                }}
                              >
                                Ouvrir 66.46
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : null}
            </>
          ) : null}
        </section>
      ) : null}

      {legacyRollbackCandidate && legacyUseCaseKey ? (
        <LegacyRollbackModal
          isPending={rollbackMutation.isPending}
          useCaseKey={legacyUseCaseKey}
          version={legacyRollbackCandidate}
          onCancel={() => setLegacyRollbackCandidate(null)}
          onConfirm={() => void handleLegacyRollback()}
        />
      ) : null}
    </div>
  )
}

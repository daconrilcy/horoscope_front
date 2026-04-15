import { useEffect, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"

import {
  useAdminLlmCatalog,
  useAdminLlmUseCases,
  useAdminPromptHistory,
  useRollbackPromptVersion,
  useAdminResolvedAssembly,
  type AdminPromptVersion,
} from "@api"
import { PersonasAdmin } from "./PersonasAdmin"
import "./AdminPromptsPage.css"

type PromptPageTab = "catalog" | "legacy" | "personas"

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
  const resolvedQuery = useAdminResolvedAssembly(
    selectedManifestEntryId,
    activeTab === "catalog" && Boolean(selectedManifestEntryId),
  )

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
  const selectedLegacyHistory = legacyHistoryQuery.data ?? []
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
                <section className="panel admin-prompts-resolved" aria-label="Detail resolved prompt assembly">
                  <div className="admin-prompts-resolved__header">
                    <h3>Resolved Prompt Assembly</h3>
                    <code>{selectedManifestEntryId}</code>
                  </div>
                  {resolvedQuery.isPending ? <div className="loading-placeholder">Chargement du detail...</div> : null}
                  {resolvedQuery.isError ? <p className="chat-error">Impossible de charger le detail d'assembly.</p> : null}
                  {resolvedQuery.data ? (
                    <div className="admin-prompts-resolved__zones">
                      <section>
                        <h4>Sources de composition</h4>
                        <p className="text-muted">
                          Source: {resolvedQuery.data.source_of_truth_status} · snapshot: {resolvedQuery.data.active_snapshot_version ?? "n/a"}
                        </p>
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
                      <section>
                        <h4>Pipeline de transformation</h4>
                        <p className="text-muted">Assembled</p>
                        <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.assembled_prompt}</pre>
                        <p className="text-muted">Post injecteurs</p>
                        <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.post_injectors_prompt}</pre>
                        <p className="text-muted">Rendered</p>
                        <pre className="admin-prompts-code">{resolvedQuery.data.transformation_pipeline.rendered_prompt}</pre>
                      </section>
                      <section>
                        <h4>Resultat resolu</h4>
                        <p className="text-muted">
                          context_quality: {resolvedQuery.data.resolved_result.context_compensation_status}
                        </p>
                        <p className="text-muted">System / hard policy</p>
                        <pre className="admin-prompts-code">{String(resolvedQuery.data.resolved_result.provider_messages.system_hard_policy ?? "")}</pre>
                        <p className="text-muted">Developer content rendu</p>
                        <pre className="admin-prompts-code">{String(resolvedQuery.data.resolved_result.provider_messages.developer_content_rendered ?? "")}</pre>
                        <p className="text-muted">Persona block</p>
                        <pre className="admin-prompts-code">{String(resolvedQuery.data.resolved_result.provider_messages.persona_block ?? "")}</pre>
                        <p className="text-muted">Execution parameters</p>
                        <pre className="admin-prompts-code">{JSON.stringify(resolvedQuery.data.resolved_result.provider_messages.execution_parameters, null, 2)}</pre>
                        <div className="admin-prompts-resolved__placeholders">
                          {resolvedQuery.data.resolved_result.placeholders.map((item) => (
                            <article key={item.name} className="admin-prompts-resolved__placeholder">
                              <strong>{item.name}</strong>
                              <span className="text-muted">{item.status}</span>
                              <span className="text-muted">{item.classification ?? "n/a"}</span>
                              <span className="text-muted">{item.resolution_source ?? "n/a"}</span>
                              <span className="text-muted">{item.reason ?? "n/a"}</span>
                              <span className="text-muted">{item.safe_to_display ? "safe_to_display" : "redacted"}</span>
                              <span className="text-muted">
                                {item.safe_to_display && item.value_preview ? item.value_preview : "redacted"}
                              </span>
                            </article>
                          ))}
                        </div>
                      </section>
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

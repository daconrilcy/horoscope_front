import { useEffect, useState } from "react"
import { useQueries, useQueryClient } from "@tanstack/react-query"

import {
  useAdminLlmPersonas,
  useAdminLlmUseCases,
  useRollbackPromptVersion,
  listPromptHistory,
  type AdminLlmPersona,
  type AdminLlmUseCase,
  type AdminPromptVersion,
} from "@api"
import { detectLang } from "@i18n/astrology"
import { PersonasAdmin } from "./PersonasAdmin"
import "./AdminPromptsPage.css"

type PromptPageTab = "prompts" | "personas"

type DiffRow = {
  leftText: string
  rightText: string
  leftType: "unchanged" | "removed"
  rightType: "unchanged" | "added"
}

type RollbackModalProps = {
  isPending: boolean
  useCaseLabel: string
  version: AdminPromptVersion
  onCancel: () => void
  onConfirm: () => void
}

function RollbackModal({ isPending, useCaseLabel, version, onCancel, onConfirm }: RollbackModalProps) {
  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content admin-prompts-modal"
        aria-labelledby="admin-prompts-rollback-title"
        aria-modal="true"
        role="dialog"
      >
        <h3 id="admin-prompts-rollback-title">Confirmer le rollback</h3>
        <p className="admin-prompts-modal__copy">
          Le prompt <strong>{useCaseLabel}</strong> sera republié sur la version du{" "}
          <strong>{formatDate(version.published_at ?? version.created_at)}</strong>.
        </p>
        <div className="admin-prompts-modal__meta">
          <span>{toDisplayStatus(version.status)}</span>
          <code>{version.id}</code>
        </div>
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
            {isPending ? "Rollback en cours..." : "Rollback vers cette version"}
          </button>
        </div>
      </div>
    </div>
  )
}

function formatDate(value: string | null): string {
  if (!value) {
    return "Non publie"
  }
  const lang = detectLang()
  const locale = lang === "en" ? "en-GB" : lang === "es" ? "es-ES" : "fr-FR"
  return new Date(value).toLocaleString(locale)
}

function toDisplayStatus(status: AdminPromptVersion["status"]): string {
  if (status === "published") {
    return "active"
  }
  if (status === "archived") {
    return "deprecated"
  }
  return "draft"
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

function resolvePersonaLabel(useCase: AdminLlmUseCase, personas: AdminLlmPersona[]): string {
  const personaId = useCase.allowed_persona_ids[0]
  if (!personaId) {
    return "Aucune persona"
  }
  return personas.find((persona) => persona.id === personaId)?.name ?? personaId
}

function resolveActiveVersion(
  useCase: AdminLlmUseCase,
  versions: AdminPromptVersion[],
): AdminPromptVersion | null {
  if (useCase.active_prompt_version_id) {
    return versions.find((version) => version.id === useCase.active_prompt_version_id) ?? null
  }
  return versions[0] ?? null
}

export function AdminPromptsPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<PromptPageTab>("prompts")
  const [selectedUseCaseKey, setSelectedUseCaseKey] = useState<string | null>(null)
  const [compareVersionId, setCompareVersionId] = useState<string | null>(null)
  const [rollbackCandidate, setRollbackCandidate] = useState<AdminPromptVersion | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const useCasesQuery = useAdminLlmUseCases()
  const personasQuery = useAdminLlmPersonas()
  const useCases = useCasesQuery.data ?? []
  const personas = personasQuery.data ?? []

  useEffect(() => {
    if (!selectedUseCaseKey && useCases.length > 0) {
      setSelectedUseCaseKey(useCases[0].key)
    }
  }, [selectedUseCaseKey, useCases])

  const historyQueries = useQueries({
    queries: useCases.map((useCase) => ({
      queryKey: ["admin-llm-prompt-history", useCase.key],
      queryFn: () => listPromptHistory(useCase.key),
      enabled: activeTab === "prompts",
    })),
  })

  const historyByUseCase = new Map<string, AdminPromptVersion[]>()
  useCases.forEach((useCase, index) => {
    historyByUseCase.set(useCase.key, historyQueries[index]?.data ?? [])
  })

  const selectedUseCase = useCases.find((useCase) => useCase.key === selectedUseCaseKey) ?? null
  const selectedHistory = selectedUseCase ? historyByUseCase.get(selectedUseCase.key) ?? [] : []
  const activeVersion = selectedUseCase ? resolveActiveVersion(selectedUseCase, selectedHistory) : null
  const compareVersion =
    selectedHistory.find((version) => version.id === compareVersionId) ??
    selectedHistory.find((version) => version.id !== activeVersion?.id) ??
    null
  const diffRows =
    activeVersion && compareVersion
      ? buildDiffRows(compareVersion.developer_prompt, activeVersion.developer_prompt)
      : []

  useEffect(() => {
    if (selectedHistory.length === 0) {
      setCompareVersionId(null)
      return
    }

    const nextCompareVersion =
      selectedHistory.find((version) => version.id !== activeVersion?.id)?.id ?? null

    if (!selectedHistory.some((version) => version.id === compareVersionId)) {
      setCompareVersionId(nextCompareVersion)
    }
  }, [activeVersion?.id, compareVersionId, selectedHistory, selectedUseCaseKey])

  const rollbackMutation = useRollbackPromptVersion()

  const isLoading =
    useCasesQuery.isPending || personasQuery.isPending || historyQueries.some((query) => query.isPending)
  const hasError = useCasesQuery.isError || personasQuery.isError || historyQueries.some((query) => query.isError)

  const handleRollback = async () => {
    if (!selectedUseCase || !rollbackCandidate) {
      return
    }
    const rolledBack = await rollbackMutation.mutateAsync({
      useCaseKey: selectedUseCase.key,
      targetVersionId: rollbackCandidate.id,
    })
    setRollbackCandidate(null)
    setSuccessMessage(`Rollback effectue vers ${rolledBack.id.slice(0, 8)}.`)
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["admin-llm-use-cases"] }),
      queryClient.invalidateQueries({ queryKey: ["admin-llm-prompt-history", selectedUseCase.key] }),
    ])
  }

  return (
    <div className="admin-prompts-page">
      <header className="admin-page-header">
        <div>
          <h2>Prompts & Personas</h2>
          <p className="admin-prompts-page__intro">
            Suivi des prompts actifs, diff rapide avec historique et rollback cible sans redeploiement.
          </p>
        </div>
        <div className="admin-tabs" role="tablist" aria-label="Sections prompts">
          <button
            className={`tab-button ${activeTab === "prompts" ? "tab-button--active" : ""}`}
            type="button"
            role="tab"
            aria-selected={activeTab === "prompts"}
            onClick={() => setActiveTab("prompts")}
          >
            Prompts
          </button>
          <button
            className={`tab-button ${activeTab === "personas" ? "tab-button--active" : ""}`}
            type="button"
            role="tab"
            aria-selected={activeTab === "personas"}
            onClick={() => setActiveTab("personas")}
          >
            Personas
          </button>
        </div>
      </header>

      {activeTab === "personas" ? (
        <PersonasAdmin />
      ) : (
        <>
          {successMessage ? <p className="state-line state-success">{successMessage}</p> : null}
          {isLoading ? <div className="loading-placeholder">Chargement des prompts...</div> : null}
          {hasError ? (
            <p className="chat-error">
              Impossible de charger la configuration LLM admin. Rafraichissez puis reessayez.
            </p>
          ) : null}

          {!isLoading && !hasError && selectedUseCase ? (
            <div className="admin-prompts-layout">
              <aside className="admin-prompts-sidebar" aria-label="Use cases LLM">
                {useCases.map((useCase) => {
                  const versions = historyByUseCase.get(useCase.key) ?? []
                  const currentVersion = resolveActiveVersion(useCase, versions)
                  return (
                    <button
                      key={useCase.key}
                      className={`admin-prompts-card ${
                        selectedUseCase.key === useCase.key ? "admin-prompts-card--active" : ""
                      }`}
                      type="button"
                      onClick={() => {
                        setSelectedUseCaseKey(useCase.key)
                        setSuccessMessage(null)
                      }}
                    >
                      <span className="admin-prompts-card__title">{useCase.display_name}</span>
                      <span className="admin-prompts-card__key">{useCase.key}</span>
                      <span className="admin-prompts-card__meta">
                        Persona: {resolvePersonaLabel(useCase, personas)}
                      </span>
                      <span className="admin-prompts-card__meta">
                        Active: {formatDate(currentVersion?.published_at ?? currentVersion?.created_at ?? null)}
                      </span>
                      <span className={`badge badge--status-${toDisplayStatus(currentVersion?.status ?? "draft")}`}>
                        {toDisplayStatus(currentVersion?.status ?? "draft")}
                      </span>
                    </button>
                  )
                })}
              </aside>

              <section className="admin-prompts-detail" aria-label="Detail prompt">
                <div className="panel admin-prompts-active">
                  <div className="admin-prompts-active__header">
                    <div>
                      <h3>{selectedUseCase.display_name}</h3>
                      <p>{selectedUseCase.description}</p>
                    </div>
                    <div className="admin-prompts-active__chips">
                      <span className="badge badge--info">{selectedUseCase.persona_strategy}</span>
                      <span className="badge badge--info">{resolvePersonaLabel(selectedUseCase, personas)}</span>
                    </div>
                  </div>

                  {activeVersion ? (
                    <>
                      <dl className="admin-prompts-active__meta">
                        <div>
                          <dt>Version active</dt>
                          <dd>
                            <code>{activeVersion.id}</code>
                          </dd>
                        </div>
                        <div>
                          <dt>Active depuis</dt>
                          <dd>{formatDate(activeVersion.published_at)}</dd>
                        </div>
                        <div>
                          <dt>Auteur</dt>
                          <dd>{activeVersion.created_by}</dd>
                        </div>
                        <div>
                          <dt>Modele</dt>
                          <dd>{activeVersion.model}</dd>
                        </div>
                      </dl>
                      <pre className="admin-prompts-code">{activeVersion.developer_prompt}</pre>
                    </>
                  ) : (
                    <p className="empty-table-state">Aucun prompt configure pour ce use case.</p>
                  )}
                </div>

                <div className="panel">
                  <div className="admin-prompts-history__header">
                    <h3>Historique des versions</h3>
                    {compareVersion ? (
                      <label className="admin-prompts-compare">
                        <span>Comparer avec</span>
                        <select
                          aria-label="Comparer avec une version"
                          value={compareVersion.id}
                          onChange={(event) => setCompareVersionId(event.target.value)}
                        >
                          {selectedHistory
                            .filter((version) => version.id !== activeVersion?.id)
                            .map((version) => (
                              <option key={version.id} value={version.id}>
                                {formatDate(version.published_at ?? version.created_at)} · {toDisplayStatus(version.status)}
                              </option>
                            ))}
                        </select>
                      </label>
                    ) : null}
                  </div>

                  <div className="admin-prompts-history">
                    {selectedHistory.map((version) => {
                      const isActive = version.id === activeVersion?.id
                      return (
                        <article key={version.id} className="admin-prompts-history__item">
                          <div>
                            <div className="admin-prompts-history__topline">
                              <strong>{formatDate(version.published_at ?? version.created_at)}</strong>
                              <span className={`badge badge--status-${toDisplayStatus(version.status)}`}>
                                {toDisplayStatus(version.status)}
                              </span>
                            </div>
                            <p className="admin-prompts-history__copy">
                              Auteur {version.created_by} · {version.model} · temp {version.temperature}
                            </p>
                            <code>{version.id}</code>
                          </div>
                          <div className="admin-prompts-history__actions">
                            {!isActive ? (
                              <>
                                <button
                                  className="text-button"
                                  type="button"
                                  onClick={() => setCompareVersionId(version.id)}
                                >
                                  Comparer
                                </button>
                                <button
                                  className="action-button action-button--secondary"
                                  type="button"
                                  onClick={() => setRollbackCandidate(version)}
                                >
                                  Rollback
                                </button>
                              </>
                            ) : (
                              <span className="text-muted">Version active</span>
                            )}
                          </div>
                        </article>
                      )
                    })}
                  </div>
                </div>

                {activeVersion && compareVersion ? (
                  <div className="panel">
                    <div className="admin-prompts-diff__header">
                      <h3>Diff cote a cote</h3>
                      <p>
                        Historique {formatDate(compareVersion.published_at ?? compareVersion.created_at)} vers actif{" "}
                        {formatDate(activeVersion.published_at ?? activeVersion.created_at)}
                      </p>
                    </div>
                    <div className="admin-prompts-diff" role="table" aria-label="Diff prompt">
                      <div className="admin-prompts-diff__column admin-prompts-diff__column--left">
                        <h4>Version comparee</h4>
                        {diffRows.map((row, index) => (
                          <code
                            key={`left-${index}`}
                            className={`admin-prompts-diff__line admin-prompts-diff__line--${row.leftType}`}
                          >
                            {row.leftText || " "}
                          </code>
                        ))}
                      </div>
                      <div className="admin-prompts-diff__column">
                        <h4>Version active</h4>
                        {diffRows.map((row, index) => (
                          <code
                            key={`right-${index}`}
                            className={`admin-prompts-diff__line admin-prompts-diff__line--${row.rightType}`}
                          >
                            {row.rightText || " "}
                          </code>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : null}
              </section>
            </div>
          ) : null}
        </>
      )}

      {rollbackCandidate && selectedUseCase ? (
        <RollbackModal
          isPending={rollbackMutation.isPending}
          useCaseLabel={selectedUseCase.display_name}
          version={rollbackCandidate}
          onCancel={() => setRollbackCandidate(null)}
          onConfirm={() => void handleRollback()}
        />
      ) : null}
    </div>
  )
}

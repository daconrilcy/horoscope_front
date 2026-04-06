import { useEffect, useMemo, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"

import {
  useAdminContentTexts,
  useAdminContentFeatureFlags,
  useUpdateAdminContentText,
  useUpdateAdminContentFeatureFlag,
  useEditorialTemplates,
  useEditorialTemplate,
  useCreateEditorialTemplateVersion,
  useRollbackEditorialTemplate,
  useCalibrationRules,
  useUpdateCalibrationRule,
  type AdminContentFeatureFlag,
  type CalibrationRule,
} from "@api"
import "./AdminContentPage.css"

type ContentTab = "paywall" | "transactional" | "flags" | "rules"

type FeatureFlagModalState = {
  enabled: boolean
  flag: AdminContentFeatureFlag
} | null

type CalibrationModalState = {
  nextValue: string
  rule: CalibrationRule
} | null

function formatDate(value: string | null): string {
  if (!value) {
    return "Non publié"
  }
  return new Date(value).toLocaleString("fr-FR")
}

function FeatureFlagModal({
  isPending,
  state,
  onCancel,
  onConfirm,
}: {
  isPending: boolean
  state: FeatureFlagModalState
  onCancel: () => void
  onConfirm: () => void
}) {
  if (!state) {
    return null
  }

  return (
    <div className="modal-overlay" role="presentation">
      <div className="modal-content admin-content-modal" role="dialog" aria-modal="true" aria-labelledby="feature-flag-modal-title">
        <h3 id="feature-flag-modal-title">Confirmer le changement du feature flag</h3>
        <p className="admin-content-modal__copy">
          Le flag <strong>{state.flag.key}</strong> sera {state.enabled ? "activé" : "désactivé"}.
        </p>
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            Annuler
          </button>
          <button className="action-button action-button--primary" type="button" onClick={onConfirm} disabled={isPending}>
            {isPending ? "Sauvegarde..." : "Confirmer"}
          </button>
        </div>
      </div>
    </div>
  )
}

function CalibrationModal({
  isPending,
  state,
  onCancel,
  onConfirm,
}: {
  isPending: boolean
  state: CalibrationModalState
  onCancel: () => void
  onConfirm: () => void
}) {
  if (!state) {
    return null
  }

  return (
    <div className="modal-overlay" role="presentation">
      <div className="modal-content admin-content-modal" role="dialog" aria-modal="true" aria-labelledby="calibration-modal-title">
        <h3 id="calibration-modal-title">Confirmer la mise à jour de la règle</h3>
        <p className="admin-content-modal__copy">
          La règle <strong>{state.rule.rule_code}</strong> sera mise à jour avec la valeur <strong>{state.nextValue}</strong>.
        </p>
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            Annuler
          </button>
          <button className="action-button action-button--primary" type="button" onClick={onConfirm} disabled={isPending}>
            {isPending ? "Sauvegarde..." : "Confirmer"}
          </button>
        </div>
      </div>
    </div>
  )
}

export function AdminContentPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<ContentTab>("paywall")
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [featureFlagModal, setFeatureFlagModal] = useState<FeatureFlagModalState>(null)
  const [calibrationModal, setCalibrationModal] = useState<CalibrationModalState>(null)
  const [draftTexts, setDraftTexts] = useState<Record<string, string>>({})
  const [selectedTemplateCode, setSelectedTemplateCode] = useState<string | null>(null)
  const [templateDraft, setTemplateDraft] = useState({
    title: "",
    content: "",
    expectedTags: "",
    exampleRender: "",
  })
  const [calibrationDrafts, setCalibrationDrafts] = useState<Record<string, string>>({})

  const paywallTextsQuery = useAdminContentTexts("paywall")
  const transactionalTextsQuery = useAdminContentTexts("transactional")
  const marketingTextsQuery = useAdminContentTexts("marketing")
  const featureFlagsQuery = useAdminContentFeatureFlags()
  const templatesQuery = useEditorialTemplates()
  const calibrationRulesQuery = useCalibrationRules()

  const updateTextMutation = useUpdateAdminContentText()
  const updateFlagMutation = useUpdateAdminContentFeatureFlag()
  const templateDetailQuery = useEditorialTemplate(selectedTemplateCode, Boolean(selectedTemplateCode))
  const createTemplateVersionMutation = useCreateEditorialTemplateVersion()
  const rollbackTemplateMutation = useRollbackEditorialTemplate()
  const updateCalibrationMutation = useUpdateCalibrationRule()

  const templates = templatesQuery.data ?? []
  const templateDetail = templateDetailQuery.data
  const calibrationRules = calibrationRulesQuery.data ?? []

  useEffect(() => {
    if (!selectedTemplateCode && templates.length > 0) {
      setSelectedTemplateCode(templates[0].template_code)
    }
  }, [selectedTemplateCode, templates])

  useEffect(() => {
    if (!templateDetail) {
      return
    }
    const activeVersion =
      templateDetail.versions.find((version) => version.id === templateDetail.active_version_id) ??
      templateDetail.versions[0]
    if (!activeVersion) {
      return
    }
    setTemplateDraft({
      title: activeVersion.title,
      content: activeVersion.content,
      expectedTags: activeVersion.expected_tags.join(", "),
      exampleRender: activeVersion.example_render ?? "",
    })
  }, [templateDetail])

  useEffect(() => {
    if (!successMessage) {
      return
    }
    const timeoutId = window.setTimeout(() => {
      setSuccessMessage(null)
    }, 3500)

    return () => window.clearTimeout(timeoutId)
  }, [successMessage])

  const hasError =
    paywallTextsQuery.isError ||
    transactionalTextsQuery.isError ||
    marketingTextsQuery.isError ||
    featureFlagsQuery.isError ||
    templatesQuery.isError ||
    templateDetailQuery.isError ||
    calibrationRulesQuery.isError

  const activeTemplate =
    templateDetail?.versions.find((version) => version.id === templateDetail.active_version_id) ??
    templateDetail?.versions[0] ??
    null

  const transactionalEntries = useMemo(
    () => [...(transactionalTextsQuery.data ?? []), ...(marketingTextsQuery.data ?? [])],
    [marketingTextsQuery.data, transactionalTextsQuery.data],
  )

  const handleSaveText = async (key: string) => {
    const nextValue = draftTexts[key]
    if (nextValue === undefined) {
      return
    }
    await updateTextMutation.mutateAsync({ key, value: nextValue })
    setSuccessMessage(`Texte ${key} mis à jour.`)
    await queryClient.invalidateQueries({ queryKey: ["admin-content-texts"] })
  }

  const handleToggleFeatureFlag = async () => {
    if (!featureFlagModal) {
      return
    }
    const { flag, enabled } = featureFlagModal
    await updateFlagMutation.mutateAsync({
      key: flag.key,
      enabled,
      targetRoles: flag.target_roles,
      targetUserIds: flag.target_user_ids,
    })
    setFeatureFlagModal(null)
    setSuccessMessage(`Feature flag ${flag.key} mis à jour.`)
    await queryClient.invalidateQueries({ queryKey: ["admin-content-feature-flags"] })
  }

  const handleSaveTemplate = async () => {
    if (!selectedTemplateCode) {
      return
    }
    await createTemplateVersionMutation.mutateAsync({
      templateCode: selectedTemplateCode,
      title: templateDraft.title,
      content: templateDraft.content,
      expected_tags: templateDraft.expectedTags
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      example_render: templateDraft.exampleRender,
    })
    setSuccessMessage(`Nouvelle version publiée pour ${selectedTemplateCode}.`)
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["admin-editorial-templates"] }),
      queryClient.invalidateQueries({ queryKey: ["admin-editorial-template", selectedTemplateCode] }),
    ])
  }

  const handleRollbackTemplate = async (versionId: string) => {
    if (!selectedTemplateCode) {
      return
    }
    await rollbackTemplateMutation.mutateAsync({ templateCode: selectedTemplateCode, versionId })
    setSuccessMessage(`Rollback effectué sur ${selectedTemplateCode}.`)
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["admin-editorial-templates"] }),
      queryClient.invalidateQueries({ queryKey: ["admin-editorial-template", selectedTemplateCode] }),
    ])
  }

  const handleUpdateCalibrationRule = async () => {
    if (!calibrationModal) {
      return
    }
    await updateCalibrationMutation.mutateAsync({
      ruleCode: calibrationModal.rule.rule_code,
      value: calibrationModal.nextValue,
    })
    setCalibrationModal(null)
    setSuccessMessage(`Règle ${calibrationModal.rule.rule_code} mise à jour.`)
    await queryClient.invalidateQueries({ queryKey: ["admin-calibration-rules"] })
  }

  const renderTextSection = (title: string, entries: Array<{ key: string; value: string; updated_at: string }>) => (
    <section className="admin-content-section panel" aria-label={title}>
      <div className="admin-content-section__header">
        <h3>{title}</h3>
      </div>
      <div className="admin-content-text-list">
        {entries.map((entry) => {
          const currentValue = draftTexts[entry.key] ?? entry.value
          return (
            <article key={entry.key} className="admin-content-text-card">
              <div className="admin-content-text-card__header">
                <div>
                  <strong>{entry.key}</strong>
                  <span className="admin-content-text-card__meta">
                    Dernière modification: {formatDate(entry.updated_at)}
                  </span>
                </div>
                <button
                  className="action-button action-button--primary"
                  type="button"
                  disabled={updateTextMutation.isPending || currentValue === entry.value}
                  onClick={() => void handleSaveText(entry.key)}
                >
                  Sauvegarder
                </button>
              </div>
              <textarea
                aria-label={`Texte ${entry.key}`}
                value={currentValue}
                onChange={(event) =>
                  setDraftTexts((currentDrafts) => ({ ...currentDrafts, [entry.key]: event.target.value }))
                }
              />
            </article>
          )
        })}
      </div>
    </section>
  )

  return (
    <div className="admin-content-page">
      <header className="admin-page-header">
        <div>
          <h2>Contenus & Paywalls</h2>
          <p className="admin-content-page__intro">
            Modifiez les textes exposés dans le produit, pilotez les feature flags et ajustez les règles métier sans déploiement.
          </p>
        </div>
        <div className="admin-tabs" role="tablist" aria-label="Sections contenu admin">
          <button
            className={`tab-button ${activeTab === "paywall" ? "tab-button--active" : ""}`}
            type="button"
            role="tab"
            aria-selected={activeTab === "paywall"}
            onClick={() => setActiveTab("paywall")}
          >
            Textes paywalls
          </button>
          <button
            className={`tab-button ${activeTab === "transactional" ? "tab-button--active" : ""}`}
            type="button"
            role="tab"
            aria-selected={activeTab === "transactional"}
            onClick={() => setActiveTab("transactional")}
          >
            Messages transactionnels
          </button>
          <button
            className={`tab-button ${activeTab === "flags" ? "tab-button--active" : ""}`}
            type="button"
            role="tab"
            aria-selected={activeTab === "flags"}
            onClick={() => setActiveTab("flags")}
          >
            Feature flags
          </button>
          <button
            className={`tab-button ${activeTab === "rules" ? "tab-button--active" : ""}`}
            type="button"
            role="tab"
            aria-selected={activeTab === "rules"}
            onClick={() => setActiveTab("rules")}
          >
            Règles métier
          </button>
        </div>
      </header>

      {successMessage ? <p className="state-line state-success">{successMessage}</p> : null}
      {hasError ? <p className="chat-error">Impossible de charger la configuration de contenu admin.</p> : null}

      {activeTab === "paywall" ? renderTextSection("Textes paywalls", paywallTextsQuery.data ?? []) : null}

      {activeTab === "transactional" ? (
        <div className="admin-content-stack">
          {renderTextSection("Messages transactionnels", transactionalEntries)}
        </div>
      ) : null}

      {activeTab === "flags" ? (
        <section className="panel" aria-label="Feature flags">
          <div className="admin-content-section__header">
            <h3>Feature flags</h3>
          </div>
          <div className="table-container">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Description</th>
                  <th>État</th>
                  <th>Scope</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {(featureFlagsQuery.data ?? []).map((flag) => (
                  <tr key={flag.key}>
                    <td>
                      <code>{flag.key}</code>
                    </td>
                    <td>{flag.description}</td>
                    <td>
                      <span className={`badge ${flag.enabled ? "badge--status-active" : "badge--status-deprecated"}`}>
                        {flag.enabled ? "activé" : "désactivé"}
                      </span>
                    </td>
                    <td>{flag.target_roles.length > 0 ? flag.target_roles.join(", ") : flag.scope}</td>
                    <td>
                      <button
                        className="text-button"
                        type="button"
                        onClick={() => setFeatureFlagModal({ flag, enabled: !flag.enabled })}
                      >
                        {flag.enabled ? "Désactiver" : "Activer"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {activeTab === "rules" ? (
        <div className="admin-content-stack">
          <section className="panel" aria-label="Templates éditoriaux">
            <div className="admin-content-section__header">
              <h3>Templates éditoriaux</h3>
            </div>
            <div className="admin-content-rules-layout">
              <aside className="admin-content-template-list">
                {templates.map((template) => (
                  <button
                    key={template.template_code}
                    type="button"
                    className={`admin-content-template-card ${
                      selectedTemplateCode === template.template_code ? "admin-content-template-card--active" : ""
                    }`}
                    onClick={() => {
                      setSelectedTemplateCode(template.template_code)
                      setSuccessMessage(null)
                    }}
                  >
                    <strong>{template.title}</strong>
                    <span>{template.template_code}</span>
                    <span>
                      Version active: {template.active_version_number ?? "-"} · {formatDate(template.published_at)}
                    </span>
                  </button>
                ))}
              </aside>

              <div className="admin-content-template-detail">
                {activeTemplate ? (
                  <>
                    <div className="admin-content-template-summary">
                      <div>
                        <h4>{activeTemplate.title}</h4>
                        <p>
                          Version active {activeTemplate.version_number} · {formatDate(activeTemplate.published_at)}
                        </p>
                      </div>
                      <span className="badge badge--info">{activeTemplate.status}</span>
                    </div>

                    <dl className="admin-content-template-meta">
                      <div>
                        <dt>Balises attendues</dt>
                        <dd>{activeTemplate.expected_tags.join(", ") || "Aucune"}</dd>
                      </div>
                      <div>
                        <dt>Exemple de rendu</dt>
                        <dd>{activeTemplate.example_render || "Aucun exemple"}</dd>
                      </div>
                    </dl>

                    <div className="admin-content-editor">
                      <label>
                        <span>Titre</span>
                        <input
                          value={templateDraft.title}
                          onChange={(event) =>
                            setTemplateDraft((draft) => ({ ...draft, title: event.target.value }))
                          }
                        />
                      </label>
                      <label>
                        <span>Balises attendues</span>
                        <input
                          value={templateDraft.expectedTags}
                          onChange={(event) =>
                            setTemplateDraft((draft) => ({ ...draft, expectedTags: event.target.value }))
                          }
                        />
                      </label>
                      <label>
                        <span>Exemple de rendu</span>
                        <textarea
                          value={templateDraft.exampleRender}
                          onChange={(event) =>
                            setTemplateDraft((draft) => ({ ...draft, exampleRender: event.target.value }))
                          }
                        />
                      </label>
                      <label>
                        <span>Contenu du template</span>
                        <textarea
                          className="admin-content-editor__code"
                          value={templateDraft.content}
                          onChange={(event) =>
                            setTemplateDraft((draft) => ({ ...draft, content: event.target.value }))
                          }
                        />
                      </label>
                      <button
                        className="action-button action-button--primary"
                        type="button"
                        onClick={() => void handleSaveTemplate()}
                        disabled={createTemplateVersionMutation.isPending}
                      >
                        {createTemplateVersionMutation.isPending ? "Publication..." : "Publier une nouvelle version"}
                      </button>
                    </div>

                    <div className="admin-content-version-list">
                      <h4>Historique des versions</h4>
                      {templateDetail?.versions.map((version) => {
                        const isActive = version.id === templateDetail.active_version_id
                        return (
                          <article key={version.id} className="admin-content-version-card">
                            <div>
                              <strong>Version {version.version_number}</strong>
                              <p>
                                {formatDate(version.published_at ?? version.created_at)} · {version.status}
                              </p>
                            </div>
                            {isActive ? (
                              <span className="text-muted">Version active</span>
                            ) : (
                              <button
                                className="text-button"
                                type="button"
                                onClick={() => void handleRollbackTemplate(version.id)}
                              >
                                Rollback
                              </button>
                            )}
                          </article>
                        )
                      })}
                    </div>
                  </>
                ) : (
                  <div className="loading-placeholder">Sélectionnez un template éditorial.</div>
                )}
              </div>
            </div>
          </section>

          <section className="panel" aria-label="Règles de calibration">
            <div className="admin-content-section__header">
              <h3>Règles de calibration</h3>
            </div>
            <div className="table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Valeur</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Version ruleset</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {calibrationRules.map((rule) => {
                    const draftValue = calibrationDrafts[rule.rule_code] ?? rule.value
                    return (
                      <tr key={rule.rule_code}>
                        <td>
                          <code>{rule.rule_code}</code>
                        </td>
                        <td>
                          <input
                            aria-label={`Valeur ${rule.rule_code}`}
                            value={draftValue}
                            onChange={(event) =>
                              setCalibrationDrafts((currentDrafts) => ({
                                ...currentDrafts,
                                [rule.rule_code]: event.target.value,
                              }))
                            }
                          />
                        </td>
                        <td>{rule.data_type}</td>
                        <td>{rule.description}</td>
                        <td>{rule.ruleset_version}</td>
                        <td>
                          <button
                            className="text-button"
                            type="button"
                            disabled={draftValue === rule.value}
                            onClick={() => setCalibrationModal({ rule, nextValue: draftValue })}
                          >
                            Sauvegarder
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      ) : null}

      <FeatureFlagModal
        isPending={updateFlagMutation.isPending}
        state={featureFlagModal}
        onCancel={() => setFeatureFlagModal(null)}
        onConfirm={() => void handleToggleFeatureFlag()}
      />

      <CalibrationModal
        isPending={updateCalibrationMutation.isPending}
        state={calibrationModal}
        onCancel={() => setCalibrationModal(null)}
        onConfirm={() => void handleUpdateCalibrationRule()}
      />
    </div>
  )
}

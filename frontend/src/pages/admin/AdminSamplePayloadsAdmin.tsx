import { useEffect, useMemo, useRef, useState } from "react"

import {
  useAdminLlmCatalog,
  useAdminLlmSamplePayloads,
  useCreateAdminLlmSamplePayload,
  useDeleteAdminLlmSamplePayload,
  useUpdateAdminLlmSamplePayload,
  getAdminLlmSamplePayload,
  AdminPromptsApiError,
  type AdminLlmSamplePayload,
  type AdminLlmSamplePayloadSummary,
} from "@api"
import "./AdminSamplePayloadsAdmin.css"

const FALLBACK_FEATURES = ["chat", "guidance", "horoscope_daily", "natal"] as const

const DEFAULT_NATAL_CHART = `{
  "sun": "aries",
  "moon": "leo"
}`

const DEFAULT_GENERIC_PAYLOAD = `{
  "sample": true
}`

const SAMPLE_PAYLOAD_ERROR_MESSAGES_FR: Readonly<Record<string, string>> = {
  invalid_sample_payload: "Payload invalide (JSON, clés sensibles ou contraintes métier).",
  sample_payload_name_conflict: "Ce nom existe déjà pour cette feature et cette locale.",
  sample_payload_default_conflict: "Un autre payload est déjà défini par défaut pour cette locale.",
  sample_payload_conflict: "Conflit de données lors de l’enregistrement.",
  invalid_query: "Paramètres de liste invalides.",
}

function formatSamplePayloadApiError(error: unknown): string {
  if (error instanceof AdminPromptsApiError) {
    const mapped = SAMPLE_PAYLOAD_ERROR_MESSAGES_FR[error.code]
    return mapped ? `${mapped} ${error.message}` : error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return "Erreur inconnue."
}

function parseJsonObject(text: string, label: string): Record<string, unknown> {
  const trimmed = text.trim()
  if (!trimmed) {
    throw new Error(`${label} : JSON vide.`)
  }
  let parsed: unknown
  try {
    parsed = JSON.parse(trimmed) as unknown
  } catch {
    throw new Error(`${label} : JSON invalide.`)
  }
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error(`${label} : un objet JSON est attendu (pas un tableau ni une valeur primitive).`)
  }
  return parsed as Record<string, unknown>
}

function buildNatalPayload(chartJsonText: string, extrasText: string): Record<string, unknown> {
  const chart = parseJsonObject(chartJsonText, "chart_json")
  const out: Record<string, unknown> = { chart_json: chart }
  const extrasTrim = extrasText.trim()
  if (!extrasTrim) {
    return out
  }
  const extras = parseJsonObject(extrasTrim, "Champs additionnels")
  for (const [key, value] of Object.entries(extras)) {
    if (key === "chart_json") {
      continue
    }
    out[key] = value
  }
  return out
}

function isNatalFeature(feature: string): boolean {
  return feature.trim().toLowerCase() === "natal"
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString("fr-FR")
}

type AdminSamplePayloadsAdminProps = {
  seedFeature: string | null
  seedLocale: string | null
}

type EditorMode = "create" | "edit"

type EditorState = {
  mode: EditorMode
  id?: string
  name: string
  description: string
  isDefault: boolean
  isActive: boolean
  /** Natal: deux champs guidés si chart_json est un objet; sinon édition JSON du payload complet (ex. données masquées par l’API). */
  natalPayloadMode: "chart_guided" | "json_blob"
  chartJsonText: string
  extrasJsonText: string
  genericPayloadText: string
}

function defaultPayloadFields(feature: string): Pick<EditorState, "natalPayloadMode" | "chartJsonText" | "extrasJsonText" | "genericPayloadText"> {
  const natal = isNatalFeature(feature)
  return {
    natalPayloadMode: natal ? "chart_guided" : "json_blob",
    chartJsonText: DEFAULT_NATAL_CHART,
    extrasJsonText: "",
    genericPayloadText: natal ? DEFAULT_NATAL_CHART : DEFAULT_GENERIC_PAYLOAD,
  }
}

function emptyEditor(feature: string): EditorState {
  return {
    mode: "create",
    name: "",
    description: "",
    isDefault: false,
    isActive: true,
    ...defaultPayloadFields(feature),
  }
}

function editorFromDetail(detail: AdminLlmSamplePayload, mode: EditorMode): EditorState {
  const natal = isNatalFeature(detail.feature)
  const payload = detail.payload_json
  let chartJsonText = DEFAULT_NATAL_CHART
  let extrasJsonText = ""
  let genericPayloadText = DEFAULT_GENERIC_PAYLOAD
  let natalPayloadMode: EditorState["natalPayloadMode"] = "json_blob"
  if (natal && payload && typeof payload.chart_json === "object" && payload.chart_json !== null) {
    natalPayloadMode = "chart_guided"
    chartJsonText = JSON.stringify(payload.chart_json, null, 2)
    const rest = { ...payload }
    delete rest.chart_json
    extrasJsonText = Object.keys(rest).length > 0 ? JSON.stringify(rest, null, 2) : ""
  } else {
    genericPayloadText = JSON.stringify(payload ?? {}, null, 2)
  }
  return {
    mode,
    id: mode === "edit" ? detail.id : undefined,
    name: detail.name,
    description: detail.description ?? "",
    isDefault: detail.is_default,
    isActive: detail.is_active,
    natalPayloadMode,
    chartJsonText,
    extrasJsonText,
    genericPayloadText,
  }
}

type DeleteTarget = Pick<AdminLlmSamplePayloadSummary, "id" | "name">

export function AdminSamplePayloadsAdmin({ seedFeature, seedLocale }: AdminSamplePayloadsAdminProps) {
  const catalogForFacets = useAdminLlmCatalog(
    { page: 1, pageSize: 25, sortBy: "feature", sortOrder: "asc" },
    true,
  )

  const featureOptions = useMemo(() => {
    const fromCatalog = catalogForFacets.data?.meta?.facets?.feature ?? []
    const merged = new Set<string>([...fromCatalog, ...FALLBACK_FEATURES])
    return Array.from(merged).sort()
  }, [catalogForFacets.data?.meta?.facets?.feature])

  const localeOptions = useMemo(() => {
    const fromCatalog = catalogForFacets.data?.meta?.facets?.locale ?? []
    const merged = new Set<string>([...fromCatalog, "fr-FR", "en-US"])
    return Array.from(merged).sort()
  }, [catalogForFacets.data?.meta?.facets?.locale])

  const [mgmtFeature, setMgmtFeature] = useState("")
  const [mgmtLocale, setMgmtLocale] = useState("")
  const [includeInactive, setIncludeInactive] = useState(true)

  useEffect(() => {
    if (seedFeature && seedLocale) {
      setMgmtFeature(seedFeature)
      setMgmtLocale(seedLocale)
    }
  }, [seedFeature, seedLocale])

  useEffect(() => {
    if (seedFeature && seedLocale) {
      return
    }
    if (mgmtFeature || !featureOptions.length) {
      return
    }
    setMgmtFeature(featureOptions[0] ?? "")
  }, [seedFeature, seedLocale, featureOptions, mgmtFeature])

  useEffect(() => {
    if (seedFeature && seedLocale) {
      return
    }
    if (mgmtLocale || !localeOptions.length) {
      return
    }
    setMgmtLocale(localeOptions[0] ?? "")
  }, [seedFeature, seedLocale, localeOptions, mgmtLocale])

  const listQuery = useAdminLlmSamplePayloads(mgmtFeature || null, mgmtLocale || null, {
    enabled: Boolean(mgmtFeature && mgmtLocale),
    includeInactive,
  })

  const createMutation = useCreateAdminLlmSamplePayload()
  const updateMutation = useUpdateAdminLlmSamplePayload()
  const deleteMutation = useDeleteAdminLlmSamplePayload()

  const [editorOpen, setEditorOpen] = useState(false)
  const [editor, setEditor] = useState<EditorState | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [banner, setBanner] = useState<string | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)
  /** Feature « de référence » du formulaire ouvert : si le filtre feature change, on vide les champs payload (revue code 68-3). */
  const payloadBaselineFeatureRef = useRef<string>("")

  useEffect(() => {
    if (!editorOpen) {
      payloadBaselineFeatureRef.current = mgmtFeature
      return
    }
    const baseline = payloadBaselineFeatureRef.current
    if (baseline === mgmtFeature) {
      return
    }
    payloadBaselineFeatureRef.current = mgmtFeature
    setFormError(null)
    setEditor((prev) => (prev ? { ...prev, ...defaultPayloadFields(mgmtFeature) } : prev))
  }, [editorOpen, mgmtFeature])

  const openCreate = () => {
    if (!mgmtFeature || !mgmtLocale) {
      return
    }
    payloadBaselineFeatureRef.current = mgmtFeature
    setFormError(null)
    setEditor(emptyEditor(mgmtFeature))
    setEditorOpen(true)
  }

  const openEdit = async (id: string) => {
    setFormError(null)
    setBanner(null)
    try {
      const detail = await getAdminLlmSamplePayload(id)
      payloadBaselineFeatureRef.current = mgmtFeature
      setEditor(editorFromDetail(detail, "edit"))
      setEditorOpen(true)
    } catch (error) {
      setFormError(formatSamplePayloadApiError(error))
    }
  }

  const openDuplicate = async (id: string) => {
    setFormError(null)
    setBanner(null)
    try {
      const detail = await getAdminLlmSamplePayload(id)
      payloadBaselineFeatureRef.current = mgmtFeature
      const copy = editorFromDetail(detail, "create")
      copy.name = `${detail.name} (copie)`
      copy.isDefault = false
      copy.isActive = true
      setEditor(copy)
      setEditorOpen(true)
    } catch (error) {
      setFormError(formatSamplePayloadApiError(error))
    }
  }

  const buildPayloadJsonForSubmit = (): Record<string, unknown> => {
    if (!mgmtFeature) {
      throw new Error("Feature manquante.")
    }
    if (isNatalFeature(mgmtFeature) && editor?.natalPayloadMode === "chart_guided") {
      return buildNatalPayload(editor.chartJsonText, editor.extrasJsonText)
    }
    return parseJsonObject(editor?.genericPayloadText ?? "", "payload_json")
  }

  const handleSubmitEditor = async () => {
    if (!editor || !mgmtFeature || !mgmtLocale) {
      return
    }
    setFormError(null)
    try {
      const payloadJson = buildPayloadJsonForSubmit()
      if (editor.mode === "create") {
        await createMutation.mutateAsync({
          name: editor.name.trim(),
          feature: mgmtFeature,
          locale: mgmtLocale,
          payload_json: payloadJson,
          description: editor.description.trim() || null,
          is_default: editor.isDefault,
          is_active: editor.isActive,
        })
        setBanner("Sample payload créé.")
      } else if (editor.id) {
        await updateMutation.mutateAsync({
          samplePayloadId: editor.id,
          payload: {
            name: editor.name.trim(),
            locale: mgmtLocale,
            payload_json: payloadJson,
            description: editor.description.trim().length > 0 ? editor.description.trim() : null,
            is_default: editor.isDefault,
            is_active: editor.isActive,
          },
        })
        setBanner("Sample payload mis à jour.")
      }
      setEditorOpen(false)
      setEditor(null)
    } catch (error) {
      setFormError(formatSamplePayloadApiError(error))
    }
  }

  const handleToggleActive = async (row: AdminLlmSamplePayloadSummary) => {
    setFormError(null)
    setBanner(null)
    try {
      await updateMutation.mutateAsync({
        samplePayloadId: row.id,
        payload: { is_active: !row.is_active },
      })
      setBanner(row.is_active ? "Sample payload désactivé." : "Sample payload réactivé.")
    } catch (error) {
      setFormError(formatSamplePayloadApiError(error))
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) {
      return
    }
    setFormError(null)
    try {
      await deleteMutation.mutateAsync(deleteTarget.id)
      setBanner(`Sample payload « ${deleteTarget.name} » supprimé.`)
      setDeleteTarget(null)
    } catch (error) {
      setFormError(formatSamplePayloadApiError(error))
    }
  }

  const recommendedId = listQuery.data?.recommended_default_id ?? null
  const items = listQuery.data?.items ?? []
  const isPending = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending

  return (
    <section className="panel sample-payloads-admin" aria-label="Gestion des sample payloads">
      <header>
        <h3>Échantillons runtime (sample payloads)</h3>
        <p className="sample-payloads-admin__intro">
          Créez, dupliquez ou désactivez des jeux de données de test pour la prévisualisation runtime, par feature et
          locale. Les champs sensibles sont refusés côté API.
        </p>
      </header>

      {catalogForFacets.isError ? (
        <p className="chat-error">Impossible de charger les facettes du catalogue (filtres partiels).</p>
      ) : null}

      {banner ? (
        <p className="state-line state-success" role="status">
          {banner}
        </p>
      ) : null}
      {formError && !editorOpen ? (
        <p className="chat-error" role="alert">
          {formError}
        </p>
      ) : null}

      <div className="sample-payloads-admin__toolbar">
        <label>
          Feature
          <select
            aria-label="Feature pour les sample payloads"
            value={mgmtFeature}
            onChange={(event) => {
              setMgmtFeature(event.target.value)
            }}
          >
            <option value="">—</option>
            {featureOptions.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          Locale
          <select
            aria-label="Locale pour les sample payloads"
            value={mgmtLocale}
            onChange={(event) => {
              setMgmtLocale(event.target.value)
            }}
          >
            <option value="">—</option>
            {localeOptions.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label className="sample-payloads-admin__toolbar-actions">
          <span>Afficher les inactifs</span>
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(event) => {
              setIncludeInactive(event.target.checked)
            }}
            aria-label="Afficher les sample payloads inactifs"
          />
        </label>
        <div className="sample-payloads-admin__toolbar-actions">
          <button className="action-button action-button--primary" type="button" onClick={openCreate} disabled={!mgmtFeature || !mgmtLocale}>
            Nouveau sample payload
          </button>
        </div>
      </div>

      {!mgmtFeature || !mgmtLocale ? (
        <p className="text-muted">Choisissez une feature et une locale pour afficher la liste.</p>
      ) : null}

      {listQuery.isPending && mgmtFeature && mgmtLocale ? <div className="loading-placeholder">Chargement…</div> : null}
      {listQuery.isError ? <p className="chat-error">Impossible de charger les sample payloads.</p> : null}

      {mgmtFeature && mgmtLocale && listQuery.data ? (
        <div className="sample-payloads-admin__table-wrap">
          <table className="sample-payloads-admin__table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Défaut</th>
                <th>Actif</th>
                <th>Mis à jour</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    <span className="text-muted">Aucun sample payload pour cette combinaison.</span>
                  </td>
                </tr>
              ) : (
                items.map((row) => (
                  <tr key={row.id}>
                    <td>
                      <strong>{row.name}</strong>
                      {recommendedId === row.id ? (
                        <span className="text-muted"> · recommandé runtime</span>
                      ) : null}
                      {row.description ? <div className="text-muted">{row.description}</div> : null}
                    </td>
                    <td>{row.is_default ? "oui" : "non"}</td>
                    <td>{row.is_active ? "oui" : "non"}</td>
                    <td>{formatDate(row.updated_at)}</td>
                    <td>
                      <div className="sample-payloads-admin__row-actions">
                        <button className="text-button" type="button" onClick={() => void openEdit(row.id)}>
                          Modifier
                        </button>
                        <button className="text-button" type="button" onClick={() => void openDuplicate(row.id)}>
                          Dupliquer
                        </button>
                        <button className="text-button" type="button" onClick={() => void handleToggleActive(row)} disabled={isPending}>
                          {row.is_active ? "Désactiver" : "Réactiver"}
                        </button>
                        <button
                          className="text-button"
                          type="button"
                          onClick={() => {
                            setFormError(null)
                            setDeleteTarget({ id: row.id, name: row.name })
                          }}
                        >
                          Supprimer
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      ) : null}

      {editorOpen && editor ? (
        <div className="modal-overlay" role="presentation">
          <div
            className="modal-content admin-prompts-modal sample-payloads-admin__modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="sample-payload-editor-title"
          >
            <h3 id="sample-payload-editor-title">
              {editor.mode === "create" ? "Nouveau sample payload" : "Modifier le sample payload"}
            </h3>
            <p className="sample-payloads-admin__modal-hint">
              Cible liste : <strong>{mgmtFeature}</strong> / <strong>{mgmtLocale}</strong>
              {editor.mode === "edit"
                ? " · la feature de l’entrée en base ne change pas via l’API (PATCH). "
                : null}
              Si vous modifiez la <strong>feature</strong> dans les filtres pendant que cette fenêtre est ouverte, les
              champs <strong>payload</strong> (JSON / chart) sont réinitialisés pour rester alignés sur la nouvelle
              cible ; le nom, la description et les cases à cocher ne sont pas effacés.
            </p>
            {formError ? (
              <p className="chat-error" role="alert">
                {formError}
              </p>
            ) : null}

            <div className="sample-payloads-admin__modal-field">
              <label htmlFor="sample-payload-name">Nom</label>
              <input
                id="sample-payload-name"
                type="text"
                value={editor.name}
                onChange={(event) => {
                  setEditor({ ...editor, name: event.target.value })
                }}
                autoComplete="off"
              />
            </div>

            <div className="sample-payloads-admin__modal-field">
              <label htmlFor="sample-payload-desc">Description (optionnel)</label>
              <textarea
                id="sample-payload-desc"
                value={editor.description}
                onChange={(event) => {
                  setEditor({ ...editor, description: event.target.value })
                }}
              />
            </div>

            <div className="sample-payloads-admin__checkbox-row">
              <label>
                <input
                  type="checkbox"
                  checked={editor.isDefault}
                  onChange={(event) => {
                    setEditor({ ...editor, isDefault: event.target.checked })
                  }}
                />
                Définir comme défaut pour cette locale
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={editor.isActive}
                  onChange={(event) => {
                    setEditor({ ...editor, isActive: event.target.checked })
                  }}
                />
                Actif
              </label>
            </div>

            {isNatalFeature(mgmtFeature) && editor.natalPayloadMode === "chart_guided" ? (
              <>
                <div className="sample-payloads-admin__modal-field">
                  <label htmlFor="sample-payload-chart">chart_json (objet JSON)</label>
                  <textarea
                    id="sample-payload-chart"
                    value={editor.chartJsonText}
                    onChange={(event) => {
                      setEditor({ ...editor, chartJsonText: event.target.value })
                    }}
                  />
                </div>
                <div className="sample-payloads-admin__modal-field">
                  <label htmlFor="sample-payload-extras">Autres clés du payload (objet JSON optionnel)</label>
                  <textarea
                    id="sample-payload-extras"
                    value={editor.extrasJsonText}
                    onChange={(event) => {
                      setEditor({ ...editor, extrasJsonText: event.target.value })
                    }}
                  />
                </div>
              </>
            ) : (
              <div className="sample-payloads-admin__modal-field">
                <label htmlFor="sample-payload-generic">
                  {isNatalFeature(mgmtFeature)
                    ? "payload_json natal (objet JSON complet, chart_json obligatoire)"
                    : "payload_json (objet JSON, non vide)"}
                </label>
                <textarea
                  id="sample-payload-generic"
                  value={editor.genericPayloadText}
                  onChange={(event) => {
                    setEditor({ ...editor, genericPayloadText: event.target.value })
                  }}
                />
              </div>
            )}

            <div className="modal-actions">
              <button
                className="text-button"
                type="button"
                onClick={() => {
                  setEditorOpen(false)
                  setEditor(null)
                  setFormError(null)
                }}
              >
                Annuler
              </button>
              <button className="action-button action-button--primary" type="button" onClick={() => void handleSubmitEditor()} disabled={isPending}>
                {isPending ? "Enregistrement…" : "Enregistrer"}
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {deleteTarget ? (
        <div className="modal-overlay" role="presentation">
          <div className="modal-content admin-prompts-modal" role="dialog" aria-modal="true" aria-labelledby="sample-payload-delete-title">
            <h3 id="sample-payload-delete-title">Supprimer le sample payload</h3>
            <p className="admin-prompts-modal__copy">
              Confirmer la suppression de <strong>{deleteTarget.name}</strong> ? Cette action est irréversible.
            </p>
            {formError ? (
              <p className="chat-error" role="alert">
                {formError}
              </p>
            ) : null}
            <div className="modal-actions">
              <button
                className="text-button"
                type="button"
                onClick={() => {
                  setDeleteTarget(null)
                  setFormError(null)
                }}
              >
                Annuler
              </button>
              <button className="action-button action-button--secondary" type="button" onClick={() => void handleDelete()} disabled={isPending}>
                {isPending ? "Suppression…" : "Supprimer"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  )
}

import { useEffect, useState, type ChangeEvent } from "react"

import {
  useOpsPersonaConfig,
  useUpdateOpsPersonaConfig,
  useRollbackOpsPersonaConfig,
  type OpsPersonaApiError,
} from "@api"
import { useTranslation } from "../i18n"

type Tone = "calm" | "direct" | "empathetic"
type PrudenceLevel = "high" | "standard"
type ScopePolicy = "strict" | "balanced"
type ResponseStyle = "concise" | "detailed"

export function OpsPersonaPanel() {
  const t = useTranslation("admin").b2b.opsPersona
  const configQuery = useOpsPersonaConfig()
  const updateConfig = useUpdateOpsPersonaConfig()
  const rollbackConfig = useRollbackOpsPersonaConfig()

  const [tone, setTone] = useState<Tone>("calm")
  const [prudenceLevel, setPrudenceLevel] = useState<PrudenceLevel>("standard")
  const [scopePolicy, setScopePolicy] = useState<ScopePolicy>("balanced")
  const [responseStyle, setResponseStyle] = useState<ResponseStyle>("concise")

  useEffect(() => {
    if (configQuery.data) {
      setTone(configQuery.data.tone)
      setPrudenceLevel(configQuery.data.prudence_level)
      setScopePolicy(configQuery.data.scope_policy)
      setResponseStyle(configQuery.data.response_style)
    }
  }, [configQuery.data])

  const handleToneChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setTone(event.target.value as Tone)
  }

  const handlePrudenceChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setPrudenceLevel(event.target.value as PrudenceLevel)
  }

  const handleScopeChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setScopePolicy(event.target.value as ScopePolicy)
  }

  const handleStyleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setResponseStyle(event.target.value as ResponseStyle)
  }

  const handleUpdate = () => {
    updateConfig.mutate({
      tone,
      prudence_level: prudenceLevel,
      scope_policy: scopePolicy,
      response_style: responseStyle,
    })
  }

  const updateError = updateConfig.error as OpsPersonaApiError | null
  const rollbackError = rollbackConfig.error as OpsPersonaApiError | null

  return (
    <section className="panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>
      {configQuery.isPending ? <p className="state-line state-loading">{t.loading}</p> : null}
      {configQuery.error ? <p className="chat-error">{t.errorLoad}</p> : null}

      {configQuery.data && (
        <div className="ops-persona-grid">
          <div className="ops-persona-field">
            <label htmlFor="persona-tone">{t.toneLabel}</label>
            <select
              id="persona-tone"
              value={tone}
              onChange={handleToneChange}
            >
              <option value="calm">calm</option>
              <option value="direct">direct</option>
              <option value="empathetic">empathetic</option>
            </select>
          </div>

          <div className="ops-persona-field">
            <label htmlFor="persona-prudence">{t.prudenceLabel}</label>
            <select
              id="persona-prudence"
              value={prudenceLevel}
              onChange={handlePrudenceChange}
            >
              <option value="high">high</option>
              <option value="standard">standard</option>
            </select>
          </div>

          <div className="ops-persona-field">
            <label htmlFor="persona-scope">{t.scopeLabel}</label>
            <select
              id="persona-scope"
              value={scopePolicy}
              onChange={handleScopeChange}
            >
              <option value="strict">strict</option>
              <option value="balanced">balanced</option>
            </select>
          </div>

          <div className="ops-persona-field">
            <label htmlFor="persona-style">{t.styleLabel}</label>
            <select
              id="persona-style"
              value={responseStyle}
              onChange={handleStyleChange}
            >
              <option value="concise">concise</option>
              <option value="detailed">detailed</option>
            </select>
          </div>
        </div>
      )}

      <div className="action-row mt-6">
        <button
          type="button"
          onClick={handleUpdate}
          disabled={updateConfig.isPending}
        >
          {t.successUpdate}
        </button>
        <button
          type="button"
          onClick={() => rollbackConfig.mutate()}
          disabled={rollbackConfig.isPending}
        >
          {t.successRollback}
        </button>
      </div>

      {updateConfig.isSuccess ? <p className="state-line state-success">{t.successUpdate}</p> : null}
      {rollbackConfig.isSuccess ? <p className="state-line state-success">{t.successRollback}</p> : null}
      {updateError ? <p className="chat-error">{t.errorGeneral(updateError.message)}</p> : null}
      {rollbackError ? <p className="chat-error">{t.errorGeneral(rollbackError.message)}</p> : null}
    </section>
  )
}

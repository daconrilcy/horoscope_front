import { useState, useEffect } from "react"

import { useOpsPersonaConfig, useUpdateOpsPersonaConfig, useRollbackOpsPersonaConfig } from "@api"
import { useTranslation } from "../i18n"

export function OpsPersonaPanel() {
  const t = useTranslation("admin").b2b.opsPersona
  const configQuery = useOpsPersonaConfig()
  const updateConfig = useUpdateOpsPersonaConfig()
  const rollbackConfig = useRollbackOpsPersonaConfig()

  const [tone, setTone] = useState<"calm" | "direct" | "empathetic">("calm")
  const [prudence, setPrudence] = useState<"high" | "standard">("standard")
  const [scope, setScope] = useState<"strict" | "balanced">("balanced")
  const [style, setStyle] = useState<"concise" | "detailed">("concise")

  useEffect(() => {
    if (configQuery.data) {
      setTone(configQuery.data.tone)
      setPrudence(configQuery.data.prudence)
      setScope(configQuery.data.scope)
      setStyle(configQuery.data.style)
    }
  }, [configQuery.data])

  const handleUpdate = () => {
    updateConfig.mutate({
      tone,
      prudence,
      scope,
      style,
    })
  }

  const updateError = updateConfig.error as Error | null
  const rollbackError = rollbackConfig.error as Error | null

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
              onChange={(e) => setTone(e.target.value as any)}
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
              value={prudence}
              onChange={(e) => setPrudence(e.target.value as any)}
            >
              <option value="high">high</option>
              <option value="standard">standard</option>
            </select>
          </div>

          <div className="ops-persona-field">
            <label htmlFor="persona-scope">{t.scopeLabel}</label>
            <select
              id="persona-scope"
              value={scope}
              onChange={(e) => setScope(e.target.value as any)}
            >
              <option value="strict">strict</option>
              <option value="balanced">balanced</option>
            </select>
          </div>

          <div className="ops-persona-field">
            <label htmlFor="persona-style">{t.styleLabel}</label>
            <select
              id="persona-style"
              value={style}
              onChange={(e) => setStyle(e.target.value as any)}
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
          className="button-ghost"
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

import { useState } from "react"
import type { FormEvent } from "react"

import {
  OpsPersonaApiError,
  type OpsPersonaUpdatePayload,
  useActivePersonaConfig,
  useRollbackPersonaConfig,
  useUpdatePersonaConfig,
} from "../api/opsPersona"

export function OpsPersonaPanel() {
  return <OpsPersonaPanelContent />
}

function OpsPersonaPanelContent() {
  const configQuery = useActivePersonaConfig()
  const updateConfig = useUpdatePersonaConfig()
  const rollbackConfig = useRollbackPersonaConfig()
  const [tone, setTone] = useState<OpsPersonaUpdatePayload["tone"]>("calm")
  const [prudenceLevel, setPrudenceLevel] = useState<OpsPersonaUpdatePayload["prudence_level"]>("high")
  const [scopePolicy, setScopePolicy] = useState<OpsPersonaUpdatePayload["scope_policy"]>("strict")
  const [responseStyle, setResponseStyle] = useState<OpsPersonaUpdatePayload["response_style"]>("concise")

  const updateError = updateConfig.error as OpsPersonaApiError | null
  const rollbackError = rollbackConfig.error as OpsPersonaApiError | null
  const isBusy = updateConfig.isPending || rollbackConfig.isPending

  return (
    <section className="panel">
      <h2>Parametrage Persona Ops</h2>
      <p>Controlez le ton et les bornes de l astrologue virtuel.</p>
      {configQuery.isPending ? <p>Chargement configuration persona...</p> : null}
      {configQuery.error ? <p>Erreur chargement persona.</p> : null}
      {configQuery.data ? (
        <p>
          Configuration active: v{configQuery.data.version} ({configQuery.data.tone},{" "}
          {configQuery.data.prudence_level}, {configQuery.data.scope_policy},{" "}
          {configQuery.data.response_style})
        </p>
      ) : null}
      <form
        className="chat-form"
        onSubmit={(event: FormEvent<HTMLFormElement>) => {
          event.preventDefault()
          updateConfig.mutate({
            tone,
            prudence_level: prudenceLevel,
            scope_policy: scopePolicy,
            response_style: responseStyle,
          })
        }}
      >
        <label htmlFor="persona-tone">Tone</label>
        <select id="persona-tone" value={tone} onChange={(event) => setTone(event.target.value as OpsPersonaUpdatePayload["tone"])}>
          <option value="calm">calm</option>
          <option value="direct">direct</option>
          <option value="empathetic">empathetic</option>
        </select>
        <label htmlFor="persona-prudence">Prudence</label>
        <select
          id="persona-prudence"
          value={prudenceLevel}
          onChange={(event) =>
            setPrudenceLevel(event.target.value as OpsPersonaUpdatePayload["prudence_level"])
          }
        >
          <option value="high">high</option>
          <option value="standard">standard</option>
        </select>
        <label htmlFor="persona-scope">Scope</label>
        <select
          id="persona-scope"
          value={scopePolicy}
          onChange={(event) => setScopePolicy(event.target.value as OpsPersonaUpdatePayload["scope_policy"])}
        >
          <option value="strict">strict</option>
          <option value="balanced">balanced</option>
        </select>
        <label htmlFor="persona-style">Style</label>
        <select
          id="persona-style"
          value={responseStyle}
          onChange={(event) =>
            setResponseStyle(event.target.value as OpsPersonaUpdatePayload["response_style"])
          }
        >
          <option value="concise">concise</option>
          <option value="detailed">detailed</option>
        </select>
        <button type="submit" disabled={isBusy}>
          Activer configuration persona
        </button>
      </form>
      <button type="button" disabled={isBusy} onClick={() => rollbackConfig.mutate()}>
        Rollback persona
      </button>
      {updateConfig.isSuccess ? <p>Configuration persona mise a jour.</p> : null}
      {rollbackConfig.isSuccess ? <p>Rollback persona effectue.</p> : null}
      {updateError ? <p>Erreur persona: {updateError.message}</p> : null}
      {rollbackError ? <p>Erreur rollback persona: {rollbackError.message}</p> : null}
    </section>
  )
}

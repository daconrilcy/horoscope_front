// Panneau admin exposant les indicateurs de monitoring operationnel.
import { useState } from "react"

import { useOpsMonitoring, useRollbackOpsPersonaConfig, type OpsPersonaApiError } from "@api"
import { useTranslation } from "../i18n"

type OpsMonitoringKpisView = {
  aggregation_scope: string
  messages_total: number
  quality_score_avg?: number
  p95_latency_ms: number | null
}

function formatLatencyMs(ms: number | null): string {
  if (ms === null) return "N/A"
  return `${ms.toFixed(0)}ms`
}

function formatQualityScore(score: number | undefined): string {
  if (score === undefined) return "N/A"
  return `${(score * 100).toFixed(1)}%`
}

export function OpsMonitoringPanel() {
  const t = useTranslation("admin").b2b.opsMonitoring
  const [windowMinutes, setWindowMinutes] = useState(60)
  const monitoring = useOpsMonitoring(windowMinutes)
  const rollbackPersona = useRollbackOpsPersonaConfig()

  const monitoringError = monitoring.error as Error | null
  const isEmpty = monitoring.isSuccess && monitoring.data === null

  return (
    <section className="panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      <label htmlFor="ops-monitoring-window">{t.windowLabel}</label>
      <select
        id="ops-monitoring-window"
        value={windowMinutes}
        onChange={(event) => setWindowMinutes(Number(event.target.value))}
      >
        <option value={15}>15 min</option>
        <option value={60}>1 hour</option>
        <option value={1440}>24 hours</option>
      </select>

      {monitoring.isPending ? <p className="state-line state-loading">Loading...</p> : null}
      {monitoringError ? <p role="alert" className="chat-error">{t.error(monitoringError.message)}</p> : null}
      {isEmpty ? <p className="state-line state-empty">{t.empty}</p> : null}

      {monitoring.data && (
        <ul className="chat-list compact-list">
          {(() => {
            const monitoringData = monitoring.data as OpsMonitoringKpisView
            return (
              <>
                <li className="chat-item">{t.scope(monitoringData.aggregation_scope)}</li>
                <li className="chat-item">{t.totalMessages(monitoringData.messages_total)}</li>
                <li className="chat-item">Quality avg: {formatQualityScore(monitoringData.quality_score_avg)}</li>
                <li className="chat-item">{t.p95Latency(formatLatencyMs(monitoringData.p95_latency_ms))}</li>
              </>
            )
          })()}
        </ul>
      )}

      <div className="action-row mt-6">
        <button
          type="button"
          className="button-danger"
          onClick={() => rollbackPersona.mutate()}
          disabled={rollbackPersona.isPending}
        >
          Emergency Rollback Persona
        </button>
      </div>

      {rollbackPersona.isSuccess ? <p className="state-line state-success">{t.successRollback}</p> : null}
      {rollbackPersona.isError && (
        <p role="alert" className="chat-error">{(rollbackPersona.error as OpsPersonaApiError).message}</p>
      )}
    </section>
  )
}


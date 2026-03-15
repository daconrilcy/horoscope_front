import { useState } from "react"

import { useOpsMonitoring, useRollbackOpsPersonaConfig } from "@api"
import { useTranslation } from "../i18n"

function formatLatencyMs(ms: number | null): string {
  if (ms === null) return "N/A"
  return `${ms.toFixed(0)}ms`
}

export function OpsMonitoringPanel() {
  const t = useTranslation("admin").b2b.opsMonitoring
  const [windowMinutes, setWindowWindowMinutes] = useState(60)
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
        onChange={(e) => setWindowWindowMinutes(Number(e.target.value))}
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
          <li className="chat-item">{t.scope(monitoring.data.aggregation_scope)}</li>
          <li className="chat-item">{t.totalMessages(monitoring.data.messages_total)}</li>
          <li className="chat-item">Quality avg: {(monitoring.data.quality_score_avg * 100).toFixed(1)}%</li>
          <li className="chat-item">{t.p95Latency(formatLatencyMs(monitoring.data.p95_latency_ms))}</li>
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
        <p role="alert" className="chat-error">{(rollbackPersona.error as Error).message}</p>
      )}
    </section>
  )
}

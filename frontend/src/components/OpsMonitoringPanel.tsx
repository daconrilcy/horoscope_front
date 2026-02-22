import { useState } from "react"

import { type MonitoringWindow, OpsMonitoringApiError, useConversationKpis } from "../api/opsMonitoring"
import { useRollbackPersonaConfig } from "../api/opsPersona"

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`
}

function formatLatencyMs(value: number): string {
  return `${Math.round(value)} ms`
}

export function OpsMonitoringPanel() {
  return <OpsMonitoringPanelContent />
}

function OpsMonitoringPanelContent() {
  const [window, setWindow] = useState<MonitoringWindow>("24h")
  const monitoring = useConversationKpis(window, true)
  const rollbackPersona = useRollbackPersonaConfig()

  const monitoringError = monitoring.error as OpsMonitoringApiError | null
  const isEmpty = !monitoring.isPending && !monitoring.error && monitoring.data?.messages_total === 0

  return (
    <section className="panel">
      <h2>Monitoring conversationnel Ops</h2>
      <p>Suivi de la qualite conversationnelle et action rapide de rollback.</p>

      <label htmlFor="ops-monitoring-window">Fenetre</label>
      <select
        id="ops-monitoring-window"
        value={window}
        onChange={(event) => setWindow(event.target.value as MonitoringWindow)}
      >
        <option value="1h">1h</option>
        <option value="24h">24h</option>
        <option value="7d">7d</option>
      </select>
      <div className="action-row">
        <button type="button" onClick={() => void monitoring.refetch()} disabled={monitoring.isFetching}>
          Rafraichir KPI
        </button>
      </div>

      {monitoring.isPending ? (
        <p aria-busy="true" className="state-line state-loading">
          Chargement KPI monitoring...
        </p>
      ) : null}
      {monitoringError ? <p role="alert" className="chat-error">Erreur monitoring: {monitoringError.message}</p> : null}
      {isEmpty ? <p className="state-line state-empty">Aucune donnee conversationnelle sur cette fenetre.</p> : null}

      {monitoring.data && !isEmpty ? (
        <ul className="chat-list compact-list">
          <li className="chat-item">Portee aggregation: {monitoring.data.aggregation_scope}</li>
          <li className="chat-item">Messages total: {monitoring.data.messages_total}</li>
          <li className="chat-item">
            Hors-scope: {monitoring.data.out_of_scope_count} ({formatPercent(monitoring.data.out_of_scope_rate)})
          </li>
          <li className="chat-item">
            Erreurs LLM: {monitoring.data.llm_error_count} ({formatPercent(monitoring.data.llm_error_rate)})
          </li>
          <li className="chat-item">Latence p95: {formatLatencyMs(monitoring.data.p95_latency_ms)}</li>
        </ul>
      ) : null}

      <div className="action-row">
        <button
          type="button"
          disabled={rollbackPersona.isPending}
          onClick={() => rollbackPersona.mutate()}
        >
          Rollback configuration persona
        </button>
      </div>
      {rollbackPersona.isSuccess ? <p className="state-line state-success">Rollback persona effectue.</p> : null}
      {rollbackPersona.error ? (
        <p role="alert" className="chat-error">Erreur rollback persona: {(rollbackPersona.error as Error).message}</p>
      ) : null}
    </section>
  )
}

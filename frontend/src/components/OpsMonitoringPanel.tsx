import { useState } from "react"

import { type MonitoringWindow, OpsMonitoringApiError, useConversationKpis } from "../api/opsMonitoring"
import { useRollbackPersonaConfig } from "../api/opsPersona"

function getRoleFromAccessToken(): string | null {
  const token = localStorage.getItem("access_token")
  if (!token) {
    return null
  }
  const parts = token.split(".")
  if (parts.length !== 3) {
    return null
  }
  try {
    const base64Url = parts[1].replace(/-/g, "+").replace(/_/g, "/")
    const padding = "=".repeat((4 - (base64Url.length % 4)) % 4)
    const payload = JSON.parse(atob(`${base64Url}${padding}`)) as { role?: string }
    return payload.role ?? null
  } catch {
    return null
  }
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`
}

function formatLatencyMs(value: number): string {
  return `${Math.round(value)} ms`
}

export function OpsMonitoringPanel() {
  const role = getRoleFromAccessToken()
  if (role !== "ops") {
    return null
  }
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
      <button type="button" onClick={() => void monitoring.refetch()} disabled={monitoring.isFetching}>
        Rafraichir KPI
      </button>

      {monitoring.isPending ? <p aria-busy="true">Chargement KPI monitoring...</p> : null}
      {monitoringError ? <p role="alert">Erreur monitoring: {monitoringError.message}</p> : null}
      {isEmpty ? <p>Aucune donnee conversationnelle sur cette fenetre.</p> : null}

      {monitoring.data && !isEmpty ? (
        <ul className="chat-list">
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

      <button
        type="button"
        disabled={rollbackPersona.isPending}
        onClick={() => rollbackPersona.mutate()}
      >
        Rollback configuration persona
      </button>
      {rollbackPersona.isSuccess ? <p>Rollback persona effectue.</p> : null}
      {rollbackPersona.error ? (
        <p role="alert">Erreur rollback persona: {(rollbackPersona.error as Error).message}</p>
      ) : null}
    </section>
  )
}

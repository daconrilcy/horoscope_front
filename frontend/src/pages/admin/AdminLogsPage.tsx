import React, { useState } from "react"
import { useMutation, useQuery } from "@tanstack/react-query"

import { apiFetch } from "../../api/client"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import "./AdminLogsPage.css"

interface QuotaAlert {
  user_id: number
  user_email_masked: string
  plan_code: string
  feature_code: string
  used: number
  limit: number
  consumption_rate: number
}

interface AppError {
  id: number
  timestamp: string
  request_id: string
  action: string
  status: string
  details: Record<string, unknown>
}

interface LlmLog {
  id: string
  request_id: string
  timestamp: string
  use_case: string
  validation_status: string
  latency_ms: number
  tokens_total: number
  prompt_version_id: string | null
}

interface StripeEvent {
  id: number
  stripe_event_id: string
  event_type: string
  status: string
  received_at: string
  last_error: string | null
}

interface ReplayModalProps {
  isPending: boolean
  log: LlmLog
  replayResult: string | null
  onClose: () => void
  onConfirm: () => void
}

function ReplayModal({
  isPending,
  log,
  replayResult,
  onClose,
  onConfirm,
}: ReplayModalProps) {
  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content admin-logs-modal"
        aria-modal="true"
        role="dialog"
        aria-labelledby="admin-logs-replay-title"
      >
        <h3 id="admin-logs-replay-title">Rejouer cet appel LLM</h3>
        <div className="modal-summary">
          <div>
            <strong>Use case</strong>
            <span>{log.use_case}</span>
          </div>
          <div>
            <strong>Request ID</strong>
            <code>{log.request_id}</code>
          </div>
          <div>
            <strong>Prompt version</strong>
            <code>{log.prompt_version_id ?? "Indisponible"}</code>
          </div>
        </div>
        <p className="modal-note">
          Cette action relance le replay sur la version de prompt d&apos;origine et génère un audit.
        </p>
        {replayResult && <p className="modal-result">{replayResult}</p>}
        <div className="modal-actions">
          <button className="text-button" onClick={onClose}>
            Annuler
          </button>
          <button
            className="action-button action-button--primary"
            disabled={isPending || !log.prompt_version_id}
            onClick={onConfirm}
          >
            {isPending ? "Replay en cours..." : "Confirmer le replay"}
          </button>
        </div>
      </div>
    </div>
  )
}

function buildLlmLogsPath(
  useCaseFilter: string,
  statusFilter: string,
  periodFilter: string,
) {
  const params = new URLSearchParams()
  if (useCaseFilter !== "all") {
    params.set("use_case", useCaseFilter)
  }
  if (statusFilter !== "all") {
    params.set("status", statusFilter)
  }
  if (periodFilter !== "all") {
    const now = new Date()
    const fromDate = new Date(now)
    if (periodFilter === "7d") {
      fromDate.setDate(now.getDate() - 7)
    } else if (periodFilter === "30d") {
      fromDate.setDate(now.getDate() - 30)
    }
    params.set("from_date", fromDate.toISOString())
  }
  const query = params.toString()
  return query ? `/v1/admin/llm/call-logs?${query}` : "/v1/admin/llm/call-logs"
}

export function AdminLogsPage() {
  const token = useAccessTokenSnapshot()
  const [activeTab, setActiveTab] = useState<"errors" | "llm" | "stripe">("errors")
  const [llmStatusFilter, setLlmStatusFilter] = useState("all")
  const [llmUseCaseFilter, setLlmUseCaseFilter] = useState("all")
  const [llmPeriodFilter, setLlmPeriodFilter] = useState("30d")
  const [selectedReplayLog, setSelectedReplayLog] = useState<LlmLog | null>(null)
  const [replayResult, setReplayResult] = useState<string | null>(null)

  const { data: alertsData } = useQuery<{ data: QuotaAlert[] }>({
    queryKey: ["admin-quota-alerts"],
    queryFn: async () => {
      const response = await apiFetch("/v1/admin/logs/quota-alerts", {
        headers: { Authorization: `Bearer ${token}` },
      })
      return response.json()
    },
    enabled: Boolean(token),
  })

  const llmLogsPath = buildLlmLogsPath(llmUseCaseFilter, llmStatusFilter, llmPeriodFilter)

  const { data: logsData, isLoading } = useQuery<{ data: AppError[] | LlmLog[] | StripeEvent[] }>({
    queryKey: ["admin-logs", activeTab, llmUseCaseFilter, llmStatusFilter, llmPeriodFilter],
    queryFn: async () => {
      const path =
        activeTab === "errors"
          ? "/v1/admin/logs/errors"
          : activeTab === "llm"
            ? llmLogsPath
            : "/v1/admin/logs/stripe"
      const response = await apiFetch(path, {
        headers: { Authorization: `Bearer ${token}` },
      })
      return response.json()
    },
    enabled: Boolean(token),
  })

  const llmLogs = activeTab === "llm" ? ((logsData?.data ?? []) as LlmLog[]) : []
  const rows = logsData?.data ?? []
  const llmUseCaseOptions = Array.from(new Set(llmLogs.map((log) => log.use_case))).sort()

  const replayMutation = useMutation({
    mutationFn: async (log: LlmLog) => {
      const response = await apiFetch("/v1/admin/llm/replay", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          request_id: log.request_id,
          prompt_version_id: log.prompt_version_id,
        }),
      })
      const payload = await response.json()
      if (!response.ok) {
        throw new Error(payload?.error?.message ?? "Replay failed")
      }
      return payload
    },
    onSuccess: (payload) => {
      setReplayResult(
        payload?.data ? "Replay exécuté avec succès." : "Replay terminé sans résultat exploitable.",
      )
    },
  })

  const openReplayModal = (log: LlmLog) => {
    setReplayResult(null)
    setSelectedReplayLog(log)
  }

  return (
    <div className="admin-logs-page">
      <header className="admin-page-header">
        <h2>Observabilité Technique</h2>
        <div className="admin-tabs">
          <button
            className={`tab-button ${activeTab === "errors" ? "tab-button--active" : ""}`}
            onClick={() => setActiveTab("errors")}
          >
            Erreurs App
          </button>
          <button
            className={`tab-button ${activeTab === "llm" ? "tab-button--active" : ""}`}
            onClick={() => setActiveTab("llm")}
          >
            Logs LLM
          </button>
          <button
            className={`tab-button ${activeTab === "stripe" ? "tab-button--active" : ""}`}
            onClick={() => setActiveTab("stripe")}
          >
            Events Stripe
          </button>
        </div>
      </header>

      {alertsData && alertsData.data.length > 0 && (
        <section className="alerts-banner">
          <h3 className="banner-title">Alertes quotas (&gt;90%)</h3>
          <div className="alerts-list">
            {alertsData.data.map((alert) => (
              <div key={`${alert.user_id}-${alert.feature_code}`} className="alert-item">
                <span className="alert-user">{alert.user_email_masked}</span>
                <span className="alert-info">
                  {alert.plan_code} · {alert.feature_code} · {alert.used}/{alert.limit}
                </span>
                <progress
                  className="alert-progress"
                  max={100}
                  value={Math.min(Math.round(alert.consumption_rate * 100), 100)}
                />
              </div>
            ))}
          </div>
        </section>
      )}

      {activeTab === "llm" && (
        <section className="filter-panel">
          <div className="filter-group">
            <label htmlFor="llm-use-case-filter">Use case</label>
            <select
              id="llm-use-case-filter"
              value={llmUseCaseFilter}
              onChange={(event) => setLlmUseCaseFilter(event.target.value)}
            >
              <option value="all">Tous</option>
              {llmUseCaseOptions.map((useCase) => (
                <option key={useCase} value={useCase}>
                  {useCase}
                </option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="llm-status-filter">Statut</label>
            <select
              id="llm-status-filter"
              value={llmStatusFilter}
              onChange={(event) => setLlmStatusFilter(event.target.value)}
            >
              <option value="all">Tous</option>
              <option value="valid">Valide</option>
              <option value="error">Erreur</option>
              <option value="repair_success">Réparé</option>
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="llm-period-filter">Période</label>
            <select
              id="llm-period-filter"
              value={llmPeriodFilter}
              onChange={(event) => setLlmPeriodFilter(event.target.value)}
            >
              <option value="7d">7 derniers jours</option>
              <option value="30d">30 derniers jours</option>
              <option value="all">Historique</option>
            </select>
          </div>
        </section>
      )}

      <section className="logs-content">
        {isLoading ? (
          <div className="loading-placeholder">Chargement des logs...</div>
        ) : (
          <div className="table-container">
            <table className="admin-table">
              {activeTab === "errors" && (
                <>
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Action</th>
                      <th>Request ID</th>
                      <th>Détails</th>
                    </tr>
                  </thead>
                  <tbody>
                    {((logsData?.data ?? []) as AppError[]).map((log) => (
                      <tr key={log.id}>
                        <td>{new Date(log.timestamp).toLocaleString()}</td>
                        <td className="text-danger">{log.action}</td>
                        <td>
                          <code>{log.request_id}</code>
                        </td>
                        <td className="json-cell">{JSON.stringify(log.details)}</td>
                      </tr>
                    ))}
                  </tbody>
                </>
              )}

              {activeTab === "llm" && (
                <>
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Use Case</th>
                      <th>Statut</th>
                      <th>Latence</th>
                      <th>Tokens</th>
                      <th>Request ID</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {llmLogs.map((log) => (
                      <tr key={log.id}>
                        <td>{new Date(log.timestamp).toLocaleString()}</td>
                        <td>{log.use_case}</td>
                        <td>
                          <span
                            className={`badge badge--status-${log.validation_status.toLowerCase()}`}
                          >
                            {log.validation_status}
                          </span>
                        </td>
                        <td>{log.latency_ms}ms</td>
                        <td>{log.tokens_total}</td>
                        <td>
                          <code>{log.request_id}</code>
                        </td>
                        <td>
                          {log.validation_status === "error" ? (
                            <button
                              className="text-button"
                              disabled={!log.prompt_version_id}
                              onClick={() => openReplayModal(log)}
                            >
                              Rejouer
                            </button>
                          ) : (
                            <span className="text-muted">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </>
              )}

              {activeTab === "stripe" && (
                <>
                  <thead>
                    <tr>
                      <th>Reçu le</th>
                      <th>Type</th>
                      <th>Statut</th>
                      <th>Stripe ID</th>
                      <th>Erreur</th>
                    </tr>
                  </thead>
                  <tbody>
                    {((logsData?.data ?? []) as StripeEvent[]).map((event) => (
                      <tr key={event.id}>
                        <td>{new Date(event.received_at).toLocaleString()}</td>
                        <td className="event-type">{event.event_type}</td>
                        <td>
                          <span className={`badge badge--status-${event.status}`}>
                            {event.status}
                          </span>
                        </td>
                        <td>
                          <code>{event.stripe_event_id}</code>
                        </td>
                        <td className="text-danger">{event.last_error || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </>
              )}
            </table>
            {rows.length === 0 && (
              <div className="empty-table-state">Aucun log trouvé.</div>
            )}
          </div>
        )}
      </section>

      {selectedReplayLog && (
        <ReplayModal
          isPending={replayMutation.isPending}
          log={selectedReplayLog}
          replayResult={replayResult}
          onClose={() => setSelectedReplayLog(null)}
          onConfirm={() => replayMutation.mutate(selectedReplayLog)}
        />
      )}
    </div>
  )
}

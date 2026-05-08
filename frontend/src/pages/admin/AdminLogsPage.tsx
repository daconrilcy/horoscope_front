import React, { useState } from "react"

import {
  useAdminAuditLogsQuery,
  useAdminLlmLogsQuery,
  useAdminQuotaAlertsQuery,
  useAdminStripeLogsQuery,
  useExportAdminAuditMutation,
  useReplayAdminLlmLogMutation,
  type AdminAuditLog,
  type AdminLlmLog,
} from "../../api/adminLogs"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import { formatLocalDateTime } from "../../utils/formatDate"
import "./AdminLogsPage.css"

interface ReplayModalProps {
  isPending: boolean
  log: AdminLlmLog
  replayResult: string | null
  onClose: () => void
  onConfirm: () => void
}

interface AuditDetailModalProps {
  log: AdminAuditLog
  onClose: () => void
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

function AuditDetailModal({ log, onClose }: AuditDetailModalProps) {
  // AC10: Defense-in-depth: Mask sensitive keys in the UI as a safety net
  // Finding Fix: Broaden the list of keys to mask
  const SENSITIVE_KEYS_TO_MASK = [
    "password",
    "token",
    "secret",
    "api_key",
    "apikey",
    "authorization",
    "credentials",
    "email",
    "phone",
    "address",
    "user_id",
    "target_id",
    "profile_id",
    "account",
    "birth_data",
    "birth_date",
    "birthdate",
    "natal_data",
    "chart_json",
  ]

  const sanitizeDetails = (data: unknown): unknown => {
    if (data === null || data === undefined) return data

    if (Array.isArray(data)) {
      return data.map((item) => sanitizeDetails(item))
    }

    if (typeof data === "object") {
      const obj = data as Record<string, unknown>
      const sanitized: Record<string, unknown> = {}

      Object.keys(obj).forEach((key) => {
        const lowerKey = key.toLowerCase()
        const value = obj[key]

        if (SENSITIVE_KEYS_TO_MASK.some((s) => lowerKey.includes(s))) {
          sanitized[key] = "[MASKED_UI]"
        } else if (typeof value === "string" && value.includes("@") && value.includes(".")) {
          sanitized[key] = "[MASKED_UI_EMAIL]"
        } else {
          sanitized[key] = sanitizeDetails(value)
        }
      })
      return sanitized
    }

    return data
  }

  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content admin-logs-modal admin-logs-modal--wide"
        aria-modal="true"
        role="dialog"
        aria-labelledby="admin-audit-detail-title"
      >
        <h3 id="admin-audit-detail-title">Détail de l&apos;événement d&apos;audit</h3>
        <div className="modal-summary admin-audit-summary">
          <div>
            <strong>Timestamp</strong>
            <span>{formatLocalDateTime(log.timestamp)}</span>
          </div>
          <div>
            <strong>Acteur</strong>
            <span>{log.actor_email_masked ?? log.actor_role}</span>
          </div>
          <div>
            <strong>Action</strong>
            <span>{log.action}</span>
          </div>
          <div>
            <strong>Cible</strong>
            <span>{log.target_id_masked ?? log.target_type ?? "Système"}</span>
          </div>
          <div>
            <strong>Statut</strong>
            <span>{log.status}</span>
          </div>
        </div>
        <pre className="audit-details-json">
          {JSON.stringify(sanitizeDetails(log.details), null, 2)}
        </pre>
        <div className="modal-actions">
          <button className="action-button action-button--primary" onClick={onClose}>
            Fermer
          </button>
        </div>
      </div>
    </div>
  )
}

export function AdminLogsPage() {
  const token = useAccessTokenSnapshot()
  const [activeTab, setActiveTab] = useState<"audit" | "llm" | "stripe">("audit")
  const [auditActorFilter, setAuditActorFilter] = useState("")
  const [auditActionFilter, setAuditActionFilter] = useState("all")
  const [auditPeriodFilter, setAuditPeriodFilter] = useState("30d")
  const [selectedAuditLog, setSelectedAuditLog] = useState<AdminAuditLog | null>(null)
  const [auditExportMessage, setAuditExportMessage] = useState<string | null>(null)
  const [llmStatusFilter, setLlmStatusFilter] = useState("all")
  const [llmUseCaseFilter, setLlmUseCaseFilter] = useState("all")
  const [llmPeriodFilter, setLlmPeriodFilter] = useState("30d")
  const [selectedReplayLog, setSelectedReplayLog] = useState<AdminLlmLog | null>(null)
  const [replayResult, setReplayResult] = useState<string | null>(null)

  const { data: alertsData } = useAdminQuotaAlertsQuery(token)
  const { data: auditLogsData, isLoading: isAuditLoading } = useAdminAuditLogsQuery(
    token,
    auditActorFilter,
    auditActionFilter,
    auditPeriodFilter,
    activeTab === "audit",
  )
  const { data: llmLogsData, isLoading: isLlmLoading } = useAdminLlmLogsQuery(
    token,
    llmUseCaseFilter,
    llmStatusFilter,
    llmPeriodFilter,
    activeTab === "llm",
  )
  const { data: stripeLogsData, isLoading: isStripeLoading } = useAdminStripeLogsQuery(token, activeTab === "stripe")

  const auditLogs = auditLogsData?.data ?? []
  const llmLogs = llmLogsData?.data ?? []
  const stripeEvents = stripeLogsData?.data ?? []
  const quotaAlerts = alertsData?.data ?? []
  const rows = activeTab === "audit" ? auditLogs : activeTab === "llm" ? llmLogs : stripeEvents
  const llmUseCaseOptions = Array.from(new Set(llmLogs.map((log) => log.use_case))).sort()
  const auditActionOptions = Array.from(new Set(auditLogs.map((log) => log.action))).sort()
  const isLoading = activeTab === "audit" ? isAuditLoading : activeTab === "llm" ? isLlmLoading : isStripeLoading

  const replayMutation = useReplayAdminLlmLogMutation(token)
  const exportMutation = useExportAdminAuditMutation(token)

  const runReplay = (log: AdminLlmLog) => {
    replayMutation.mutate(log, {
    onSuccess: (payload) => {
      setReplayResult(
        payload?.data ? "Replay exécuté avec succès." : "Replay terminé sans résultat exploitable.",
      )
    },
    })
  }

  const runAuditExport = () => {
    exportMutation.mutate(
      {
        actor: auditActorFilter.trim() || null,
        action: auditActionFilter === "all" ? null : auditActionFilter,
        period: auditPeriodFilter,
      },
      {
        onSuccess: async (response) => {
      const blob = await response.blob()
      const header = response.headers.get("Content-Disposition")
      const filename = header?.match(/filename=([^;]+)/)?.[1] ?? "audit_log.csv"
      const objectUrl = window.URL.createObjectURL(blob)
      const anchor = document.createElement("a")
      anchor.href = objectUrl
      anchor.download = filename.replace(/\"/g, "")
      document.body.appendChild(anchor)
      anchor.click()
      document.body.removeChild(anchor)
      window.URL.revokeObjectURL(objectUrl)
      setAuditExportMessage(`Export CSV généré: ${filename}`)
        },
        onError: (error) => {
      setAuditExportMessage(error instanceof Error ? error.message : "Export CSV impossible.")
        },
      },
    )
  }

  const openReplayModal = (log: AdminLlmLog) => {
    setReplayResult(null)
    setSelectedReplayLog(log)
  }

  const openAuditDetail = (log: AdminAuditLog) => {
    setSelectedAuditLog(log)
  }

  return (
    <div className="admin-logs-page">
      <header className="admin-page-header">
        <h2>Observabilité Technique</h2>
        <div className="admin-tabs">
          <button
            className={`tab-button ${activeTab === "audit" ? "tab-button--active" : ""}`}
            onClick={() => setActiveTab("audit")}
          >
            Erreurs applicatives
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
            Événements Stripe
          </button>
        </div>
      </header>

      {quotaAlerts.length > 0 && (
        <section className="alerts-banner">
          <h3 className="banner-title">Alertes quotas (&gt;90%)</h3>
          <div className="alerts-list">
            {quotaAlerts.map((alert) => (
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

      {activeTab === "audit" && (
        <section className="filter-panel">
          <div className="filter-group">
            <label htmlFor="audit-actor-filter">Acteur</label>
            <input
              id="audit-actor-filter"
              type="search"
              value={auditActorFilter}
              onChange={(event) => setAuditActorFilter(event.target.value)}
              placeholder="email ou rôle"
            />
          </div>
          <div className="filter-group">
            <label htmlFor="audit-action-filter">Action</label>
            <select
              id="audit-action-filter"
              value={auditActionFilter}
              onChange={(event) => setAuditActionFilter(event.target.value)}
            >
              <option value="all">Toutes</option>
              {auditActionOptions.map((action) => (
                <option key={action} value={action}>
                  {action}
                </option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="audit-period-filter">Période</label>
            <select
              id="audit-period-filter"
              value={auditPeriodFilter}
              onChange={(event) => setAuditPeriodFilter(event.target.value)}
            >
              <option value="7d">7 derniers jours</option>
              <option value="30d">30 derniers jours</option>
              <option value="all">Historique</option>
            </select>
          </div>
          <div className="filter-actions">
            <button
              className="action-button action-button--primary"
              disabled={exportMutation.isPending}
              onClick={runAuditExport}
            >
              {exportMutation.isPending ? "Export..." : "Exporter CSV"}
            </button>
            {auditExportMessage && <p className="status-message">{auditExportMessage}</p>}
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
              {activeTab === "audit" && (
                <>
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Acteur</th>
                      <th>Action</th>
                      <th>Cible</th>
                      <th>Statut</th>
                      <th>Détails</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.map((log) => (
                      <tr key={log.id}>
                        <td>{formatLocalDateTime(log.timestamp)}</td>
                        <td>{log.actor_email_masked ?? log.actor_role}</td>
                        <td>{log.action}</td>
                        <td>{log.target_id_masked ?? log.target_type ?? "Système"}</td>
                        <td>
                          <span className={`badge badge--status-${log.status.toLowerCase()}`}>
                            {log.status}
                          </span>
                        </td>
                        <td>
                          <button className="text-button" onClick={() => openAuditDetail(log)}>
                            Voir détail
                          </button>
                        </td>
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
                        <td>{formatLocalDateTime(log.timestamp)}</td>
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
                    {stripeEvents.map((event) => (
                      <tr key={event.id}>
                        <td>{formatLocalDateTime(event.received_at)}</td>
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
            {rows.length === 0 && <div className="empty-table-state">Aucun log trouvé.</div>}
          </div>
        )}
      </section>

      {selectedAuditLog && (
        <AuditDetailModal log={selectedAuditLog} onClose={() => setSelectedAuditLog(null)} />
      )}

      {selectedReplayLog && (
        <ReplayModal
          isPending={replayMutation.isPending}
          log={selectedReplayLog}
          replayResult={replayResult}
          onClose={() => setSelectedReplayLog(null)}
          onConfirm={() => runReplay(selectedReplayLog)}
        />
      )}
    </div>
  )
}

import React, { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
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
  details: any
}

interface LlmLog {
  id: string
  timestamp: string
  use_case: string
  validation_status: string
  latency_ms: number
  tokens_total: number
}

interface StripeEvent {
  id: number
  stripe_event_id: string
  event_type: string
  status: string
  received_at: string
  last_error: string | null
}

export function AdminLogsPage() {
  const token = useAccessTokenSnapshot()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<"errors" | "llm" | "stripe">("errors")

  // 1. Quota Alerts
  const { data: alertsData } = useQuery<{ data: QuotaAlert[] }>({
    queryKey: ["admin-quota-alerts"],
    queryFn: async () => {
      const response = await apiFetch("/v1/admin/logs/quota-alerts", {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.json()
    },
    enabled: Boolean(token),
  })

  // 2. Tab-specific Data
  const { data: logsData, isLoading } = useQuery<{ data: any[] }>({
    queryKey: ["admin-logs", activeTab],
    queryFn: async () => {
      const path = activeTab === "errors" ? "/v1/admin/logs/errors" : 
                   activeTab === "llm" ? "/v1/admin/llm/call-logs" : 
                   "/v1/admin/logs/stripe"
      const response = await apiFetch(path, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.json()
    },
    enabled: Boolean(token),
  })

  const replayMutation = useMutation({
    mutationFn: async (requestId: string) => {
      // Find a draft version to test with (simplified)
      const response = await apiFetch("/v1/admin/llm/replay", {
        method: "POST",
        headers: { 
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ request_id: requestId, prompt_version_id: "" }) // Need a real ID
      })
      return response.json()
    }
  })

  return (
    <div className="admin-logs-page">
      <header className="admin-page-header">
        <h2>Observabilité Technique</h2>
        <div className="admin-tabs">
          <button className={`tab-button ${activeTab === "errors" ? "tab-button--active" : ""}`} onClick={() => setActiveTab("errors")}>Erreurs App</button>
          <button className={`tab-button ${activeTab === "llm" ? "tab-button--active" : ""}`} onClick={() => setActiveTab("llm")}>Logs LLM</button>
          <button className={`tab-button ${activeTab === "stripe" ? "tab-button--active" : ""}`} onClick={() => setActiveTab("stripe")}>Events Stripe</button>
        </div>
      </header>

      {alertsData && alertsData.data.length > 0 && (
        <section className="alerts-banner">
          <h3 className="banner-title">⚠️ Alertes Quotas (&gt;90%)</h3>
          <div className="alerts-list">
            {alertsData.data.map((alert, i) => (
              <div key={i} className="alert-item">
                <span className="alert-user">{alert.user_email_masked}</span>
                <span className="alert-info">{alert.feature_code}: {alert.used}/{alert.limit}</span>
                <div className="alert-progress-bg">
                  <div className="alert-progress-fill" style={{ width: `${alert.consumption_rate * 100}%` }}></div>
                </div>
              </div>
            ))}
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
                    <tr><th>Timestamp</th><th>Action</th><th>Request ID</th><th>Details</th></tr>
                  </thead>
                  <tbody>
                    {logsData?.data.map((log: AppError) => (
                      <tr key={log.id}>
                        <td>{new Date(log.timestamp).toLocaleString()}</td>
                        <td className="text-danger">{log.action}</td>
                        <td><code>{log.request_id}</code></td>
                        <td className="json-cell">{JSON.stringify(log.details)}</td>
                      </tr>
                    ))}
                  </tbody>
                </>
              )}

              {activeTab === "llm" && (
                <>
                  <thead>
                    <tr><th>Timestamp</th><th>Use Case</th><th>Status</th><th>Latence</th><th>Tokens</th><th>Actions</th></tr>
                  </thead>
                  <tbody>
                    {logsData?.data.map((log: LlmLog) => (
                      <tr key={log.id}>
                        <td>{new Date(log.timestamp).toLocaleString()}</td>
                        <td>{log.use_case}</td>
                        <td><span className={`badge badge--status-${log.validation_status.toLowerCase()}`}>{log.validation_status}</span></td>
                        <td>{log.latency_ms}ms</td>
                        <td>{log.tokens_total}</td>
                        <td>
                          {log.validation_status === "ERROR" && (
                            <button className="text-button" onClick={() => window.alert("Replay feature in progress")}>Rejouer</button>
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
                    <tr><th>Received</th><th>Type</th><th>Status</th><th>Stripe ID</th><th>Error</th></tr>
                  </thead>
                  <tbody>
                    {logsData?.data.map((evt: StripeEvent) => (
                      <tr key={evt.id}>
                        <td>{new Date(evt.received_at).toLocaleString()}</td>
                        <td className="event-type">{evt.event_type}</td>
                        <td><span className={`badge badge--status-${evt.status}`}>{evt.status}</span></td>
                        <td><code>{evt.stripe_event_id}</code></td>
                        <td className="text-danger">{evt.last_error || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </>
              )}
            </table>
            {(!logsData || logsData.data.length === 0) && (
              <div className="empty-table-state">Aucun log trouvé.</div>
            )}
          </div>
        )}
      </section>
    </div>
  )
}

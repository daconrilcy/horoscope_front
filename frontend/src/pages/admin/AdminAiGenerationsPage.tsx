import React, { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { apiFetch } from "../../api/client"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import "./AdminAiGenerationsPage.css"

interface UseCaseMetrics {
  use_case: string
  call_count: number
  total_tokens: number
  estimated_cost_usd: float
  avg_latency_ms: int
  error_rate: float
  retry_rate: float
}

interface TrendPoint {
  date: string
  call_count: number
  error_count: number
}

interface FailedCall {
  id: string
  timestamp: string
  error_code: string
  user_id_masked: string | null
}

interface UseCaseDetail {
  use_case: string
  metrics: UseCaseMetrics
  trend_data: TrendPoint[]
  recent_failed_calls: FailedCall[]
}

export function AdminAiGenerationsPage() {
  const token = useAccessTokenSnapshot()
  const [period, setPeriod] = useState("30d")
  const [selectedUseCase, setSelectedUseCase] = useState<string | null>(null)

  // 1. List all use cases metrics
  const { data: metricsData, isLoading: metricsLoading } = useQuery<{ data: UseCaseMetrics[] }>({
    queryKey: ["admin-ai-metrics", period],
    queryFn: async () => {
      const response = await apiFetch(`/v1/admin/ai/metrics?period=${period}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) throw new Error("Failed to fetch AI metrics")
      return response.json()
    },
    enabled: Boolean(token),
  })

  // 2. Detail for selected use case
  const { data: detailData, isLoading: detailLoading } = useQuery<UseCaseDetail>({
    queryKey: ["admin-ai-use-case-detail", selectedUseCase, period],
    queryFn: async () => {
      const response = await apiFetch(`/v1/admin/ai/metrics/${selectedUseCase}?period=${period}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) throw new Error("Failed to fetch detail")
      return response.json()
    },
    enabled: Boolean(token && selectedUseCase),
  })

  return (
    <div className="admin-ai-generations-page">
      <header className="admin-page-header">
        <h2>Supervision IA (LLM)</h2>
        <div className="filter-bar">
          <label>Période :</label>
          <select value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="7d">7 derniers jours</option>
            <option value="30d">30 derniers jours</option>
          </select>
        </div>
      </header>

      <section className="metrics-summary">
        {metricsLoading ? (
          <div className="loading-placeholder">Chargement des métriques...</div>
        ) : (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Use Case</th>
                <th>Appels</th>
                <th>Tokens</th>
                <th>Coût Est.</th>
                <th>Latence Moy.</th>
                <th>Taux d'Échec</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {metricsData?.data.map(m => (
                <tr 
                  key={m.use_case} 
                  className={m.error_rate > 0.05 ? "row--alert" : ""}
                  onClick={() => setSelectedUseCase(m.use_case)}
                >
                  <td className="use-case-name">{m.use_case}</td>
                  <td>{m.call_count}</td>
                  <td>{(m.total_tokens / 1000).toFixed(1)}k</td>
                  <td>${m.estimated_cost_usd.toFixed(2)}</td>
                  <td>{m.avg_latency_ms}ms</td>
                  <td className={m.error_rate > 0.05 ? "text-danger" : ""}>
                    {(m.error_rate * 100).toFixed(1)}%
                  </td>
                  <td>
                    <button className="text-button" onClick={(e) => {
                      e.stopPropagation()
                      setSelectedUseCase(m.use_case)
                    }}>Détails</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {selectedUseCase && (
        <section className="use-case-detail-panel">
          <div className="detail-panel-header">
            <h3>Détail : {selectedUseCase}</h3>
            <button className="close-button" onClick={() => setSelectedUseCase(null)}>×</button>
          </div>

          {detailLoading ? (
            <div className="loading-placeholder">Chargement du détail...</div>
          ) : detailData && (
            <div className="detail-content">
              <div className="trend-section">
                <h4>Tendance Volume vs Erreurs</h4>
                <div className="mini-chart-placeholder">
                  {/* Reuse TrendChart or simple bar logic */}
                  <p>(Graphique de tendance temporel ici)</p>
                </div>
              </div>

              <div className="failed-calls-section">
                <h4>10 derniers échecs</h4>
                <table className="admin-table admin-table--mini">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Request ID</th>
                      <th>Erreur</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detailData.recent_failed_calls.map(f => (
                      <tr key={f.id}>
                        <td>{new Date(f.timestamp).toLocaleString()}</td>
                        <td><code>{f.user_id_masked}</code></td>
                        <td><span className="badge badge--error">{f.error_code}</span></td>
                      </tr>
                    ))}
                    {detailData.recent_failed_calls.length === 0 && (
                      <tr><td colSpan={3} className="empty-table-state">Aucun échec récent.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  )
}

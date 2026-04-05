import React, { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { apiFetch } from "../../api/client"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import "./AdminDashboardPage.css"

interface KpisSnapshot {
  total_users: number
  active_users_7j: number
  active_users_30j: number
  subscriptions_by_plan: Record<string, number>
  mrr_cents: number
  arr_cents: number
  trials_count: number
  last_updated: string
}

interface TrendPoint {
  date: string
  new_users: number
}

interface KpisFlux {
  period: string
  plan: string
  new_users: number
  churn_count: number
  upgrades_count: number
  downgrades_count: number
  payment_failures_count: number
  revenue_cents: number
  trend_data: TrendPoint[]
  last_updated: string
}

function KpiCard({ title, value, unit = "", loading = false, highlight = false }: { title: string, value?: string | number, unit?: string, loading?: boolean, highlight?: boolean }) {
  return (
    <div className={`kpi-card ${highlight ? "kpi-card--highlight" : ""}`}>
      <h3 className="kpi-card-title">{title}</h3>
      <div className="kpi-card-value">
        {loading ? (
          <span className="kpi-skeleton">...</span>
        ) : (
          <>
            <span className="kpi-number">{value ?? 0}</span>
            {unit && <span className="kpi-unit">{unit}</span>}
          </>
        )}
      </div>
    </div>
  )
}

function TrendChart({ data }: { data: TrendPoint[] }) {
  if (data.length === 0) return <div className="chart-empty">Aucune donnée de tendance.</div>

  const maxVal = Math.max(...data.map(p => p.new_users), 1)
  const width = 400
  const height = 100
  const padding = 10
  
  const points = data.map((p, i) => {
    const x = padding + (i * (width - 2 * padding)) / (data.length - 1 || 1)
    const y = height - padding - (p.new_users * (height - 2 * padding)) / maxVal
    return `${x},${y}`
  }).join(" ")

  return (
    <div className="trend-chart-container">
      <svg viewBox={`0 0 ${width} ${height}`} className="trend-chart">
        <polyline
          fill="none"
          stroke="var(--color-primary)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />
        {data.map((p, i) => {
          const x = padding + (i * (width - 2 * padding)) / (data.length - 1 || 1)
          const y = height - padding - (p.new_users * (height - 2 * padding)) / maxVal
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="3"
              fill="var(--color-primary-strong)"
              className="chart-dot"
            >
              <title>{p.date}: {p.new_users}</title>
            </circle>
          )
        })}
      </svg>
      <div className="chart-labels">
        <span>{data[0].date}</span>
        <span>{data[data.length - 1].date}</span>
      </div>
    </div>
  )
}

export function AdminDashboardPage() {
  const token = useAccessTokenSnapshot()
  const [period, setPeriod] = useState("30d")
  const [plan, setPlan] = useState("all")
  
  // 1. Snapshot KPIs (independent of period/plan filters for some parts, but here we keep them separate)
  const snapshotQuery = useQuery<{ data: KpisSnapshot }>({
    queryKey: ["admin-kpis-snapshot"],
    queryFn: async () => {
      const response = await apiFetch("/v1/admin/dashboard/kpis-snapshot", {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) throw new Error("Failed to fetch snapshot KPIs")
      return response.json()
    },
    enabled: Boolean(token),
  })

  // 2. Flux KPIs (filtered)
  const fluxQuery = useQuery<{ data: KpisFlux }>({
    queryKey: ["admin-kpis-flux", period, plan],
    queryFn: async () => {
      const response = await apiFetch(`/v1/admin/dashboard/kpis-flux?period=${period}&plan=${plan}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) throw new Error("Failed to fetch flux KPIs")
      return response.json()
    },
    enabled: Boolean(token),
  })

  const snapshot = snapshotQuery.data?.data
  const flux = fluxQuery.data?.data

  return (
    <div className="admin-dashboard-page">
      <header className="admin-page-header">
        <h2>Tableau de bord</h2>
        <div className="dashboard-filters">
          <div className="filter-group">
            <label htmlFor="period-select">Période :</label>
            <select id="period-select" value={period} onChange={(e) => setPeriod(e.target.value)}>
              <option value="7d">7 derniers jours</option>
              <option value="30d">30 derniers jours</option>
              <option value="12m">12 derniers mois</option>
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="plan-select">Plan :</label>
            <select id="plan-select" value={plan} onChange={(e) => setPlan(e.target.value)}>
              <option value="all">Tous les plans</option>
              <option value="free">Free</option>
              <option value="basic">Basic</option>
              <option value="premium">Premium</option>
            </select>
          </div>
        </div>
      </header>

      <section className="dashboard-section">
        <h3 className="section-title">État Instantané</h3>
        <div className="kpi-grid">
          <KpiCard title="Inscrits totaux" value={snapshot?.total_users} loading={snapshotQuery.isLoading} />
          <KpiCard title="Actifs (7j)" value={snapshot?.active_users_7j} loading={snapshotQuery.isLoading} />
          <KpiCard title="MRR Actuel" value={snapshot ? (snapshot.mrr_cents / 100).toLocaleString() : undefined} unit="€" loading={snapshotQuery.isLoading} highlight />
          <KpiCard title="Essais en cours" value={snapshot?.trials_count} loading={snapshotQuery.isLoading} />
        </div>
      </section>

      <section className="dashboard-section">
        <h3 className="section-title">Métriques de Flux ({period === "12m" ? "12 mois" : period})</h3>
        <div className="kpi-grid">
          <KpiCard title="Nouveaux inscrits" value={flux?.new_users} loading={fluxQuery.isLoading} />
          <KpiCard title="Churn (annulations)" value={flux?.churn_count} loading={fluxQuery.isLoading} />
          <KpiCard title="Échecs paiement" value={flux?.payment_failures_count} loading={fluxQuery.isLoading} />
          <KpiCard title="Revenu estimé" value={flux ? (flux.revenue_cents / 100).toLocaleString() : undefined} unit="€" loading={fluxQuery.isLoading} />
        </div>
      </section>

      <section className="dashboard-section dashboard-visuals">
        <div className="visual-card">
          <h3 className="visual-card-title">Tendance des inscriptions</h3>
          {fluxQuery.isLoading ? (
            <div className="loading-placeholder">Chargement du graphe...</div>
          ) : (
            <TrendChart data={flux?.trend_data ?? []} />
          )}
        </div>
        
        <div className="visual-card">
          <h3 className="visual-card-title">Abonnements par plan</h3>
          {snapshotQuery.isLoading ? (
            <div className="loading-placeholder">Chargement...</div>
          ) : (
            <div className="plan-list">
              {snapshot && Object.entries(snapshot.subscriptions_by_plan).map(([p, count]) => (
                <div key={p} className="plan-item">
                  <span className="plan-name">{p}</span>
                  <span className="plan-count">{count}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

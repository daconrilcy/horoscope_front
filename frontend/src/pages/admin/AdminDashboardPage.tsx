import React from "react"
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

function KpiCard({ title, value, unit = "", loading = false }: { title: string, value?: string | number, unit?: string, loading?: boolean }) {
  return (
    <div className="kpi-card">
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

export function AdminDashboardPage() {
  const token = useAccessTokenSnapshot()
  
  const { data, isLoading, error } = useQuery<{ data: KpisSnapshot }>({
    queryKey: ["admin-kpis-snapshot"],
    queryFn: async () => {
      const response = await apiFetch("/v1/admin/dashboard/kpis-snapshot", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      if (!response.ok) throw new Error("Failed to fetch KPIs")
      return response.json()
    },
    enabled: Boolean(token),
    refetchInterval: 5 * 60 * 1000, // 5 min
  })

  const kpis = data?.data

  if (error) {
    return (
      <div className="admin-dashboard-page">
        <div className="admin-error">
          <p>Erreur lors du chargement des KPIs.</p>
          <button onClick={() => window.location.reload()}>Réessayer</button>
        </div>
      </div>
    )
  }

  return (
    <div className="admin-dashboard-page">
      <header className="admin-page-header">
        <h2>Tableau de bord</h2>
        {kpis && (
          <span className="last-updated">
            Mis à jour le : {new Date(kpis.last_updated).toLocaleString()}
          </span>
        )}
      </header>

      <section className="kpi-grid">
        <KpiCard 
          title="Inscrits totaux" 
          value={kpis?.total_users} 
          loading={isLoading} 
        />
        <KpiCard 
          title="Actifs (7j)" 
          value={kpis?.active_users_7j} 
          loading={isLoading} 
        />
        <KpiCard 
          title="Actifs (30j)" 
          value={kpis?.active_users_30j} 
          loading={isLoading} 
        />
        <KpiCard 
          title="Essais en cours" 
          value={kpis?.trials_count} 
          loading={isLoading} 
        />
        <KpiCard 
          title="MRR" 
          value={kpis ? (kpis.mrr_cents / 100).toLocaleString() : undefined} 
          unit="€" 
          loading={isLoading} 
        />
        <KpiCard 
          title="ARR" 
          value={kpis ? (kpis.arr_cents / 100).toLocaleString() : undefined} 
          unit="€" 
          loading={isLoading} 
        />
      </section>

      <section className="dashboard-details">
        <div className="details-card">
          <h3 className="details-card-title">Abonnements par plan</h3>
          {isLoading ? (
            <div className="loading-placeholder">Chargement...</div>
          ) : (
            <div className="plan-list">
              {kpis && Object.entries(kpis.subscriptions_by_plan).length > 0 ? (
                Object.entries(kpis.subscriptions_by_plan).map(([plan, count]) => (
                  <div key={plan} className="plan-item">
                    <span className="plan-name">{plan}</span>
                    <span className="plan-count">{count}</span>
                  </div>
                ))
              ) : (
                <p className="empty-state">Aucun abonnement actif.</p>
              )}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

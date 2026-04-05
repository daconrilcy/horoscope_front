import React, { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiFetch } from "../../api/client"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import "./AdminUserDetailPage.css"

interface UserDetail {
  id: number
  email: string
  role: string
  created_at: string
  is_active: boolean
  is_suspended: boolean
  is_locked: boolean
  plan_code: string | null
  subscription_status: string | null
  stripe_customer_id_masked: string | null
  payment_method_summary: string | null
  last_invoice_amount_cents: number | null
  last_invoice_date: string | null
  quotas: Array<{
    feature_code: string
    used: number
    limit: number | null
    period: string
  }>
  recent_tickets: Array<{
    id: number
    title: string
    status: string
    created_at: string
  }>
  recent_audit_events: Array<{
    id: number
    action: string
    actor_role: string
    created_at: string
  }>
}

export function AdminUserDetailPage() {
  const { userId } = useParams()
  const token = useAccessTokenSnapshot()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [revealedStripeId, setRevealedStripeId] = useState<string | null>(null)

  const { data, isLoading, error } = useQuery<{ data: UserDetail }>({
    queryKey: ["admin-user-detail", userId],
    queryFn: async () => {
      const response = await apiFetch(`/v1/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) throw new Error("Failed to fetch user detail")
      return response.json()
    },
    enabled: Boolean(token && userId),
  })

  const actionMutation = useMutation({
    mutationFn: async ({ action, body }: { action: string, body?: any }) => {
      const response = await apiFetch(`/v1/admin/users/${userId}/${action}`, {
        method: "POST",
        headers: { 
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: body ? JSON.stringify(body) : undefined
      })
      if (!response.ok) throw new Error(`${action} failed`)
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-user-detail", userId] })
    }
  })

  const revealMutation = useMutation({
    mutationFn: async () => {
      const response = await apiFetch(`/v1/admin/users/${userId}/reveal-stripe-id`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) throw new Error("Reveal failed")
      return response.json()
    },
    onSuccess: (res) => {
      setRevealedStripeId(res.stripe_customer_id)
      queryClient.invalidateQueries({ queryKey: ["admin-user-detail", userId] })
    }
  })

  const handleAction = (action: string, label: string, body?: any) => {
    if (window.confirm(`Êtes-vous sûr de vouloir ${label} cet utilisateur ?`)) {
      actionMutation.mutate({ action, body })
    }
  }

  if (isLoading) return <div className="admin-loading">Chargement de la fiche utilisateur...</div>
  if (error || !data) return <div className="admin-error">Utilisateur non trouvé ou erreur serveur.</div>

  const user = data.data

  return (
    <div className="admin-user-detail-page">
      <header className="admin-page-header">
        <div className="header-left">
          <button className="back-button" onClick={() => navigate("/admin/users")}>← Retour</button>
          <h2>Fiche Utilisateur #{user.id}</h2>
        </div>
        <div className="header-actions">
          <span className={`badge badge--role-${user.role}`}>{user.role}</span>
          {user.is_suspended && <span className="badge badge--suspended">Suspendu</span>}
          {user.is_locked && <span className="badge badge--locked">Verrouillé</span>}
        </div>
      </header>

      <div className="detail-grid">
        <div className="detail-column">
          <section className="detail-card">
            <div className="card-header-with-actions">
              <h3 className="card-title">Profil</h3>
              <div className="card-actions">
                {user.is_suspended ? (
                  <button 
                    className="action-button action-button--success"
                    onClick={() => handleAction("unsuspend", "réactiver")}
                    disabled={actionMutation.isPending}
                  >
                    Réactiver
                  </button>
                ) : (
                  <button 
                    className="action-button action-button--danger"
                    onClick={() => handleAction("suspend", "suspendre")}
                    disabled={actionMutation.isPending}
                  >
                    Suspendre
                  </button>
                )}
                {user.is_locked && (
                  <button 
                    className="action-button action-button--warning"
                    onClick={() => handleAction("unlock", "débloquer")}
                    disabled={actionMutation.isPending}
                  >
                    Débloquer
                  </button>
                )}
              </div>
            </div>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">Email</span>
                <span className="info-value">{user.email}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Créé le</span>
                <span className="info-value">{new Date(user.created_at).toLocaleString()}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Statut Compte</span>
                <span className="info-value">
                  {user.is_suspended ? (
                    <span className="status-suspended">Suspendu</span>
                  ) : (
                    <span className="status-active">Actif</span>
                  )}
                </span>
              </div>
            </div>
          </section>

          <section className="detail-card">
            <h3 className="card-title">Abonnement & Billing</h3>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">Plan Actuel</span>
                <span className="info-value"><strong>{user.plan_code}</strong></span>
              </div>
              <div className="info-item">
                <span className="info-label">Statut Stripe</span>
                <span className="info-value">
                  <span className={`badge badge--status-${user.subscription_status}`}>
                    {user.subscription_status || "N/A"}
                  </span>
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Customer ID</span>
                <div className="info-value stripe-id-container">
                  <code>{revealedStripeId || user.stripe_customer_id_masked || "N/A"}</code>
                  {!revealedStripeId && user.stripe_customer_id_masked && (
                    <button 
                      className="reveal-button" 
                      onClick={() => revealMutation.mutate()}
                      disabled={revealMutation.isPending}
                      title="Révéler l'ID (Action journalisée)"
                    >
                      {revealMutation.isPending ? "..." : "👁️"}
                    </button>
                  )}
                </div>
              </div>
            </div>
          </section>

          <section className="detail-card">
            <h3 className="card-title">Quotas (Usage courant)</h3>
            <div className="quota-list">
              {user.quotas.map(q => (
                <div key={q.feature_code} className="quota-item">
                  <div className="quota-header">
                    <span className="quota-name">{q.feature_code}</span>
                    <div className="quota-header-right">
                      <span className="quota-values">{q.used} / {q.limit || "∞"}</span>
                      <button 
                        className="reset-button"
                        onClick={() => handleAction("reset-quota", `réinitialiser le quota ${q.feature_code}`, { feature_code: q.feature_code })}
                        disabled={actionMutation.isPending}
                        title="Réinitialiser le quota"
                      >
                        🔄
                      </button>
                    </div>
                  </div>
                  <div className="quota-bar-container">
                    <div
                      className="quota-bar-fill"
                      style={{ ["--quota-fill-width" as string]: q.limit ? `${Math.min((q.used / q.limit) * 100, 100)}%` : "0%" }}
                    ></div>
                  </div>
                  <span className="quota-period">{q.period}</span>
                </div>
              ))}
              {user.quotas.length === 0 && <p className="empty-text">Aucun quota actif.</p>}
            </div>
          </section>
        </div>

        <div className="detail-column">
          <section className="detail-card">
            <h3 className="card-title">Derniers Tickets Support</h3>
            <div className="ticket-list">
              {user.recent_tickets.map(t => (
                <div key={t.id} className="list-item">
                  <div className="list-item-main">
                    <span className="list-item-title">{t.title}</span>
                    <span className="list-item-date">{new Date(t.created_at).toLocaleDateString()}</span>
                  </div>
                  <span className={`badge badge--status-${t.status.toLowerCase()}`}>{t.status}</span>
                </div>
              ))}
              {user.recent_tickets.length === 0 && <p className="empty-text">Aucun ticket.</p>}
            </div>
          </section>

          <section className="detail-card">
            <h3 className="card-title">Journal d'Audit</h3>
            <div className="audit-list">
              {user.recent_audit_events.map(a => (
                <div key={a.id} className="list-item audit-item">
                  <div className="list-item-main">
                    <span className="audit-action">{a.action}</span>
                    <span className="list-item-date">{new Date(a.created_at).toLocaleString()}</span>
                  </div>
                  <span className="audit-actor">{a.actor_role}</span>
                </div>
              ))}
              {user.recent_audit_events.length === 0 && <p className="empty-text">Aucun événement d'audit.</p>}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

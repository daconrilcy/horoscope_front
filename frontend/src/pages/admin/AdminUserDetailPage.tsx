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
  plan_code: string | None
  subscription_status: string | None
  stripe_customer_id_masked: string | None
  payment_method_summary: string | None
  last_invoice_amount_cents: number | None
  last_invoice_date: string | None
  quotas: Array<{
    feature_code: string
    used: number
    limit: number | None
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
      // Refresh audit logs to show the reveal action
      queryClient.invalidateQueries({ queryKey: ["admin-user-detail", userId] })
    }
  })

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
        </div>
      </header>

      <div className="detail-grid">
        {/* Section Profil & Plan */}
        <div className="detail-column">
          <section className="detail-card">
            <h3 className="card-title">Profil</h3>
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
                  <span className="status-active">Actif</span>
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
                    <span className="quota-values">{q.used} / {q.limit || "∞"}</span>
                  </div>
                  <div className="quota-bar-container">
                    <div 
                      className="quota-bar-fill" 
                      style={{ width: q.limit ? `${Math.min((q.used / q.limit) * 100, 100)}%` : "0%" }}
                    ></div>
                  </div>
                  <span className="quota-period">{q.period}</span>
                </div>
              ))}
              {user.quotas.length === 0 && <p className="empty-text">Aucun quota actif.</p>}
            </div>
          </section>
        </div>

        {/* Section Tickets & Audit */}
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

import React, { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate, useParams } from "react-router-dom"

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
  activity_summary: {
    total_tokens: number
    tokens_in: number
    tokens_out: number
    messages_count: number
    natal_charts_total: number
    natal_charts_short: number
    natal_charts_complete: number
  }
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

type ActionDialogState =
  | { type: "refresh-subscription" }
  | { type: "assign-plan" }
  | { type: "commercial-gesture" }
  | null

interface ActionDialogProps {
  actionMutationPending: boolean
  assignPlanForm: {
    plan_code: string
    reason: string
  }
  commercialGestureForm: {
    gesture_type: string
    value: number
    reason: string
  }
  dialog: NonNullable<ActionDialogState>
  onAssignPlanChange: (field: "plan_code" | "reason", value: string) => void
  onCommercialGestureChange: (
    field: "gesture_type" | "value" | "reason",
    value: string,
  ) => void
  onClose: () => void
  onSubmit: () => void
}

function ActionDialog({
  actionMutationPending,
  assignPlanForm,
  commercialGestureForm,
  dialog,
  onAssignPlanChange,
  onCommercialGestureChange,
  onClose,
  onSubmit,
}: ActionDialogProps) {
  const isRefreshSubscription = dialog.type === "refresh-subscription"
  const isAssignPlan = dialog.type === "assign-plan"

  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content admin-user-detail-modal"
        aria-modal="true"
        role="dialog"
        aria-labelledby="admin-user-detail-modal-title"
      >
        <h3 id="admin-user-detail-modal-title">
          {isRefreshSubscription
            ? "Forcer un refresh d'abonnement"
            : isAssignPlan
              ? "Attribuer un plan manuellement"
              : "Enregistrer un geste commercial"}
        </h3>

        {isRefreshSubscription ? (
          <>
            <p className="scope-badge scope-badge--warning">
              Cette action resynchronise le statut et le plan depuis Stripe en lecture+écriture.
              Aucun changement de facturation ne sera effectué côté Stripe.
            </p>
            <p className="modal-note">
              Le refresh met à jour l&apos;état local du compte à partir de Stripe et journalise
              l&apos;opération.
            </p>
          </>
        ) : isAssignPlan ? (
          <>
            <p className="scope-badge">Applicatif uniquement — sans effet Stripe</p>
            <div className="modal-form-grid">
              <label>
                Plan
                <select
                  value={assignPlanForm.plan_code}
                  onChange={(event) => onAssignPlanChange("plan_code", event.target.value)}
                >
                  <option value="free">Free</option>
                  <option value="basic">Basic</option>
                  <option value="premium">Premium</option>
                </select>
              </label>
              <label>
                Motif obligatoire
                <textarea
                  rows={3}
                  value={assignPlanForm.reason}
                  onChange={(event) => onAssignPlanChange("reason", event.target.value)}
                />
              </label>
            </div>
          </>
        ) : (
          <>
            <p className="scope-badge">Applicatif uniquement — aucun crédit Stripe</p>
            <div className="modal-form-grid">
              <label>
                Type de geste
                <select
                  value={commercialGestureForm.gesture_type}
                  onChange={(event) =>
                    onCommercialGestureChange("gesture_type", event.target.value)
                  }
                >
                  <option value="extra_days">Jours supplémentaires</option>
                  <option value="extra_messages">Messages supplémentaires</option>
                </select>
              </label>
              <label>
                Valeur
                <input
                  min={1}
                  type="number"
                  value={commercialGestureForm.value}
                  onChange={(event) => onCommercialGestureChange("value", event.target.value)}
                />
              </label>
              <label>
                Motif
                <textarea
                  rows={3}
                  value={commercialGestureForm.reason}
                  onChange={(event) => onCommercialGestureChange("reason", event.target.value)}
                />
              </label>
            </div>
          </>
        )}

        <div className="modal-actions">
          <button className="text-button" onClick={onClose}>
            Annuler
          </button>
          <button
            className="action-button action-button--primary"
            disabled={actionMutationPending}
            onClick={onSubmit}
          >
            {actionMutationPending ? "Action en cours..." : "Confirmer"}
          </button>
        </div>
      </div>
    </div>
  )
}

export function AdminUserDetailPage() {
  const { userId } = useParams()
  const token = useAccessTokenSnapshot()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [revealedStripeId, setRevealedStripeId] = useState<string | null>(null)
  const [dialog, setDialog] = useState<ActionDialogState>(null)
  const [assignPlanForm, setAssignPlanForm] = useState({
    plan_code: "basic",
    reason: "",
  })
  const [commercialGestureForm, setCommercialGestureForm] = useState({
    gesture_type: "extra_days",
    value: 7,
    reason: "",
  })

  const { data, isLoading, error } = useQuery<{ data: UserDetail }>({
    queryKey: ["admin-user-detail", userId],
    queryFn: async () => {
      const response = await apiFetch(`/v1/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!response.ok) {
        throw new Error("Failed to fetch user detail")
      }
      return response.json()
    },
    enabled: Boolean(token && userId),
  })

  const actionMutation = useMutation({
    mutationFn: async ({
      action,
      body,
    }: {
      action: string
      body?: Record<string, string | number>
    }) => {
      const response = await apiFetch(`/v1/admin/users/${userId}/${action}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: body ? JSON.stringify(body) : undefined,
      })
      if (!response.ok) {
        throw new Error(`${action} failed`)
      }
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-user-detail", userId] })
      setDialog(null)
    },
  })

  const revealMutation = useMutation({
    mutationFn: async () => {
      const response = await apiFetch(`/v1/admin/users/${userId}/reveal-stripe-id`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!response.ok) {
        throw new Error("Reveal failed")
      }
      return response.json()
    },
    onSuccess: (response) => {
      setRevealedStripeId(response.stripe_customer_id)
      queryClient.invalidateQueries({ queryKey: ["admin-user-detail", userId] })
    },
  })

  const runImmediateAction = (action: string, body?: Record<string, string>) => {
    actionMutation.mutate({ action, body })
  }

  const submitDialogAction = () => {
    if (dialog?.type === "refresh-subscription") {
      actionMutation.mutate({ action: "refresh-subscription" })
      return
    }

    if (dialog?.type === "assign-plan") {
      actionMutation.mutate({
        action: "assign-plan",
        body: {
          plan_code: assignPlanForm.plan_code,
          reason: assignPlanForm.reason,
        },
      })
      return
    }

    if (dialog?.type === "commercial-gesture") {
      actionMutation.mutate({
        action: "commercial-gesture",
        body: {
          gesture_type: commercialGestureForm.gesture_type,
          value: commercialGestureForm.value,
          reason: commercialGestureForm.reason,
        },
      })
    }
  }

  if (isLoading) {
    return <div className="admin-loading">Chargement de la fiche utilisateur...</div>
  }
  if (error || !data) {
    return <div className="admin-error">Utilisateur non trouvé ou erreur serveur.</div>
  }

  const user = data.data

  return (
    <div className="admin-user-detail-page">
      <header className="admin-page-header">
        <div className="header-left">
          <button className="back-button" onClick={() => navigate("/admin/users")}>
            Retour à la liste
          </button>
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
                    onClick={() => runImmediateAction("unsuspend")}
                    disabled={actionMutation.isPending}
                  >
                    Réactiver
                  </button>
                ) : (
                  <button
                    className="action-button action-button--danger"
                    onClick={() => runImmediateAction("suspend")}
                    disabled={actionMutation.isPending}
                  >
                    Suspendre
                  </button>
                )}
                {user.is_locked && (
                  <button
                    className="action-button action-button--warning"
                    onClick={() => runImmediateAction("unlock")}
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
            <div className="card-header-with-actions">
              <h3 className="card-title">Abonnement & Billing</h3>
              <div className="card-actions card-actions--wrap">
                <button
                  className="action-button action-button--primary"
                  disabled={actionMutation.isPending}
                  onClick={() => setDialog({ type: "refresh-subscription" })}
                >
                  Refresh abonnement
                </button>
                <button
                  className="action-button"
                  disabled={actionMutation.isPending}
                  onClick={() => setDialog({ type: "assign-plan" })}
                >
                  Attribuer un plan
                </button>
                <button
                  className="action-button"
                  disabled={actionMutation.isPending}
                  onClick={() => setDialog({ type: "commercial-gesture" })}
                >
                  Geste commercial
                </button>
              </div>
            </div>
            <div className="scope-list">
              <p className="scope-badge scope-badge--warning">
                Refresh abonnement: synchronisation Stripe en lecture+écriture, sans effet de
                facturation.
              </p>
              <p className="scope-badge">Plan manuel: applicatif uniquement, sans effet Stripe.</p>
              <p className="scope-badge">Geste commercial: applicatif uniquement, aucun crédit Stripe.</p>
            </div>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">Plan Actuel</span>
                <span className="info-value">
                  <strong>{user.plan_code}</strong>
                </span>
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
                      title="Révéler l'ID (action journalisée)"
                    >
                      Révéler
                    </button>
                  )}
                </div>
              </div>
            </div>
          </section>

          <section className="detail-card">
            <h3 className="card-title">Activité</h3>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">Tokens totaux</span>
                <span className="info-value">{user.activity_summary.total_tokens}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Tokens envoyés</span>
                <span className="info-value">{user.activity_summary.tokens_in}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Tokens reçus</span>
                <span className="info-value">{user.activity_summary.tokens_out}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Messages</span>
                <span className="info-value">{user.activity_summary.messages_count}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Thèmes natals (total)</span>
                <span className="info-value">{user.activity_summary.natal_charts_total}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Thèmes natals courts</span>
                <span className="info-value">{user.activity_summary.natal_charts_short}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Thèmes natals complets</span>
                <span className="info-value">{user.activity_summary.natal_charts_complete}</span>
              </div>
            </div>
          </section>

          <section className="detail-card">
            <h3 className="card-title">Quotas (Usage courant)</h3>
            <div className="quota-list">
              {user.quotas.map((quota) => {
                const progressValue =
                  quota.limit && quota.limit > 0
                    ? Math.min(Math.round((quota.used / quota.limit) * 100), 100)
                    : 0

                return (
                  <div key={`${quota.feature_code}-${quota.period}`} className="quota-item">
                    <div className="quota-header">
                      <span className="quota-name">{quota.feature_code}</span>
                      <div className="quota-header-right">
                        <span className="quota-values">
                          {quota.used} / {quota.limit || "∞"}
                        </span>
                        <button
                          className="reset-button"
                          onClick={() =>
                            runImmediateAction("reset-quota", {
                              feature_code: quota.feature_code,
                            })
                          }
                          disabled={actionMutation.isPending}
                          title="Réinitialiser le quota"
                        >
                          Reset
                        </button>
                      </div>
                    </div>
                    <progress className="quota-progress" max={100} value={progressValue} />
                    <span className="quota-period">{quota.period}</span>
                  </div>
                )
              })}
              {user.quotas.length === 0 && <p className="empty-text">Aucun quota actif.</p>}
            </div>
          </section>
        </div>

        <div className="detail-column">
          <section className="detail-card">
            <h3 className="card-title">Derniers Tickets Support</h3>
            <div className="ticket-list">
              {user.recent_tickets.map((ticket) => (
                <div key={ticket.id} className="list-item">
                  <div className="list-item-main">
                    <span className="list-item-title">{ticket.title}</span>
                    <span className="list-item-date">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <span className={`badge badge--status-${ticket.status.toLowerCase()}`}>
                    {ticket.status}
                  </span>
                </div>
              ))}
              {user.recent_tickets.length === 0 && <p className="empty-text">Aucun ticket.</p>}
            </div>
          </section>

          <section className="detail-card">
            <h3 className="card-title">Journal d&apos;Audit</h3>
            <div className="audit-list">
              {user.recent_audit_events.map((event) => (
                <div key={event.id} className="list-item audit-item">
                  <div className="list-item-main">
                    <span className="audit-action">{event.action}</span>
                    <span className="list-item-date">
                      {new Date(event.created_at).toLocaleString()}
                    </span>
                  </div>
                  <span className="audit-actor">{event.actor_role}</span>
                </div>
              ))}
              {user.recent_audit_events.length === 0 && (
                <p className="empty-text">Aucun événement d&apos;audit.</p>
              )}
            </div>
          </section>
        </div>
      </div>

      {dialog && (
        <ActionDialog
          actionMutationPending={actionMutation.isPending}
          assignPlanForm={assignPlanForm}
          commercialGestureForm={commercialGestureForm}
          dialog={dialog}
          onAssignPlanChange={(field, value) =>
            setAssignPlanForm((current) => ({ ...current, [field]: value }))
          }
          onCommercialGestureChange={(field, value) =>
            setCommercialGestureForm((current) => ({
              ...current,
              [field]: field === "value" ? Number(value) : value,
            }))
          }
          onClose={() => setDialog(null)}
          onSubmit={submitDialogAction}
        />
      )}
    </div>
  )
}

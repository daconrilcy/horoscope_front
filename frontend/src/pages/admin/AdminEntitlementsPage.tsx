import React, { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiFetch } from "../../api/client"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import { useAdminPermissions } from "../../state/AdminPermissionsContext"
import "./AdminEntitlementsPage.css"

interface EntitlementPlan {
  id: number
  code: string
  name: string
  audience: string
}

interface EntitlementFeature {
  id: number
  code: string
  name: string
  is_metered: boolean
}

interface EntitlementCell {
  access_mode: string
  is_enabled: boolean
  variant_code: string | null
  quota_limit: number | null
  period: string | null
  is_incoherent: boolean
}

interface MatrixResponse {
  plans: EntitlementPlan[]
  features: EntitlementFeature[]
  cells: Record<string, EntitlementCell>
}

export function AdminEntitlementsPage() {
  const token = useAccessTokenSnapshot()
  const { canEdit } = useAdminPermissions()
  const queryClient = useQueryClient()
  const [hoveredCell, setHoveredCell] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)

  const { data, isLoading, error } = useQuery<MatrixResponse>({
    queryKey: ["admin-entitlements-matrix"],
    queryFn: async () => {
      const response = await apiFetch("/v1/admin/entitlements/matrix", {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) throw new Error("Failed to fetch matrix")
      return response.json()
    },
    enabled: Boolean(token),
  })

  const updateMutation = useMutation({
    mutationFn: async ({ planId, featureId, payload }: { planId: number, featureId: number, payload: any }) => {
      const response = await apiFetch(`/v1/admin/entitlements/${planId}/${featureId}`, {
        method: "PATCH",
        headers: { 
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      })
      if (!response.ok) throw new Error("Update failed")
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-entitlements-matrix"] })
    }
  })

  if (isLoading) return <div className="admin-loading">Chargement de la matrice des droits...</div>
  if (error || !data) return <div className="admin-error">Erreur lors de la récupération des données.</div>

  const { plans, features, cells } = data

  const handleCellChange = (planId: number, featureId: number, field: string, value: any, label: string) => {
    if (window.confirm(`Confirmer la modification : ${label} ?`)) {
      updateMutation.mutate({ planId, featureId, payload: { [field]: value } })
    }
  }

  return (
    <div className={`admin-entitlements-page ${isEditing ? "admin-entitlements-page--editing" : ""}`}>
      <header className="admin-page-header">
        <div className="header-left">
          <h2>Matrice des Droits (Entitlements)</h2>
          {isEditing && <span className="editing-banner">MODE ÉDITION ACTIF — Toute modification est journalisée</span>}
        </div>
        <div className="header-actions">
          {canEdit("entitlements") && (
            <button className={`action-button ${isEditing ? "action-button--active" : ""}`} onClick={() => setIsEditing(!isEditing)}>
              {isEditing ? "Quitter l'édition" : "Modifier la matrice"}
            </button>
          )}
        </div>
      </header>

      <section className="matrix-section">
        <div className="matrix-container">
          <table className="entitlement-matrix">
            <thead>
              <tr>
                <th className="sticky-col">Features \ Plans</th>
                {plans.map(plan => (
                  <th key={plan.id}>
                    <div className="plan-header">
                      <span className="plan-name">{plan.code}</span>
                      <span className="plan-audience">{plan.audience}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {features.map(feature => (
                <tr key={feature.id}>
                  <td className="feature-cell sticky-col">
                    <div className="feature-info">
                      <span className="feature-name">{feature.name}</span>
                      <span className="feature-code">{feature.code}</span>
                    </div>
                  </td>
                  {plans.map(plan => {
                    const key = `${plan.id}:${feature.id}`
                    const cell = cells[key]
                    if (!cell) return <td key={key} className="cell--empty">-</td>

                    return (
                      <td 
                        key={key} 
                        className={`matrix-cell cell--${cell.access_mode} ${cell.is_incoherent ? "cell--incoherent" : ""} ${isEditing ? "cell--editable" : ""}`}
                        onMouseEnter={() => !isEditing && setHoveredCell(key)}
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        <div className="cell-content">
                          {isEditing ? (
                            <div className="edit-controls">
                              <select 
                                value={cell.access_mode} 
                                onChange={(e) => handleCellChange(plan.id, feature.id, "access_mode", e.target.value, `Mode d'accès ${plan.code}/${feature.code}`)}
                              >
                                <option value="disabled">Disabled</option>
                                <option value="unlimited">Unlimited</option>
                                <option value="quota">Quota</option>
                              </select>
                              {cell.access_mode === "quota" && (
                                <input 
                                  type="number" 
                                  defaultValue={cell.quota_limit || 0}
                                  onBlur={(e) => {
                                    const newVal = parseInt(e.target.value)
                                    if (newVal !== cell.quota_limit) {
                                      handleCellChange(plan.id, feature.id, "quota_limit", newVal, `Quota ${plan.code}/${feature.code}`)
                                    }
                                  }}
                                />
                              )}
                              <label className="checkbox-label">
                                <input 
                                  type="checkbox" 
                                  checked={cell.is_enabled} 
                                  onChange={(e) => handleCellChange(plan.id, feature.id, "is_enabled", e.target.checked, `${e.target.checked ? 'Activer' : 'Désactiver'} ${plan.code}/${feature.code}`)}
                                />
                                En.
                              </label>
                            </div>
                          ) : (
                            <>
                              <span className="access-mode-icon">
                                {cell.access_mode === "disabled" ? "❌" : cell.access_mode === "unlimited" ? "♾️" : "📊"}
                              </span>
                              {cell.access_mode === "quota" && <span className="quota-val">{cell.quota_limit}</span>}
                              {cell.is_incoherent && <span className="incoherent-icon">⚠️</span>}
                            </>
                          )}
                        </div>
                        
                        {!isEditing && hoveredCell === key && (
                          <div className="cell-tooltip">
                            <div className="tooltip-row"><strong>Mode:</strong> {cell.access_mode}</div>
                            {cell.variant_code && <div className="tooltip-row"><strong>LLM Variant:</strong> {cell.variant_code}</div>}
                            {cell.quota_limit !== null && <div className="tooltip-row"><strong>Limite:</strong> {cell.quota_limit} ({cell.period})</div>}
                            <div className="tooltip-row"><strong>Activé:</strong> {cell.is_enabled ? "Oui" : "Non"}</div>
                          </div>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="matrix-footer">
        <h3>Règles & Comportements</h3>
        <div className="rules-grid">
          <div className="rule-card">
            <h4>Édition Restreinte</h4>
            <p>Seuls le <strong>mode d'accès</strong>, la <strong>limite de quota</strong> et le flag <strong>is_enabled</strong> sont modifiables ici. Le variant LLM est géré dans la section Prompts.</p>
          </div>
          <div className="rule-card">
            <h4>Audit Trail</h4>
            <p>Chaque modification confirmée crée une entrée dans le journal d'audit global avec les valeurs avant/après.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

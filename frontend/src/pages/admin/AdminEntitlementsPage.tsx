import React, { useState } from "react"
import { useQuery } from "@tanstack/react-query"
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
  is_metered: bool
}

interface EntitlementCell {
  access_mode: string
  is_enabled: bool
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
  const [hoveredCell, setHoveredCell] = useState<string | null>(null)

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

  if (isLoading) return <div className="admin-loading">Chargement de la matrice des droits...</div>
  if (error || !data) return <div className="admin-error">Erreur lors de la récupération des données.</div>

  const { plans, features, cells } = data

  const getCellLabel = (cell: EntitlementCell) => {
    if (!cell.is_enabled || cell.access_mode === "disabled") return "❌ Désactivé"
    if (cell.access_mode === "unlimited") return "♾️ Illimité"
    if (cell.access_mode === "quota") return `📊 ${cell.quota_limit} / ${cell.period}`
    return cell.access_mode
  }

  return (
    <div className="admin-entitlements-page">
      <header className="admin-page-header">
        <div className="header-left">
          <h2>Matrice des Droits (Entitlements)</h2>
          <span className="source-label">Source de vérité : Canonique DB</span>
        </div>
        <div className="header-actions">
          <button className="action-button" disabled={!canEdit("entitlements")}>
            {canEdit("entitlements") ? "Modifier la matrice" : "Lecture seule"}
          </button>
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
                      <span className="plan-name">{plan.name}</span>
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
                        className={`matrix-cell cell--${cell.access_mode} ${cell.is_incoherent ? "cell--incoherent" : ""}`}
                        onMouseEnter={() => setHoveredCell(key)}
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        <div className="cell-content">
                          {getCellLabel(cell)}
                          {cell.is_incoherent && <span className="incoherent-icon" title="Quota incohérent (ex: mode quota mais limite 0)">⚠️</span>}
                        </div>
                        
                        {hoveredCell === key && (
                          <div className="cell-tooltip">
                            <div className="tooltip-row"><strong>Mode:</strong> {cell.access_mode}</div>
                            {cell.variant_code && <div className="tooltip-row"><strong>Variant:</strong> {cell.variant_code}</div>}
                            {cell.quota_limit !== null && <div className="tooltip-row"><strong>Limite:</strong> {cell.quota_limit}</div>}
                            {cell.period && <div className="tooltip-row"><strong>Période:</strong> {cell.period}</div>}
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
        <h3>Règles backend & Comportements attendus</h3>
        <div className="rules-grid">
          <div className="rule-card">
            <h4>Horoscope Journalier</h4>
            <p>Le frontend masque la section si <code>disabled</code>. Affiche un cadenas si <code>teaser</code>.</p>
          </div>
          <div className="rule-card">
            <h4>Chat Astrologue</h4>
            <p>Le quota est décompté à chaque message envoyé. La réponse LLM utilise le <code>variant_code</code> défini.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

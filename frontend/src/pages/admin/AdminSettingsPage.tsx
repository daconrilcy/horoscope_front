import React, { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { exportAdminData, type AdminExportType } from "../../api/adminOperations"
import { useAdminPermissions } from "../../state/AdminPermissionsContext"
import "./AdminSettingsPage.css"

interface ExportModalProps {
  type: AdminExportType
  onClose: () => void
  onExportCompleted?: (result: ExportResult) => void
}

interface ExportResult {
}

function ExportModal({ type, onClose, onExportCompleted }: ExportModalProps) {
  const [period, setPeriod] = useState({ start: "", end: "" })
  const [format, setFormat] = useState("csv")
  const [confirmed, setConfirmed] = useState(false)

  const exportMutation = useMutation({
    mutationFn: async () => {
      const response = await exportAdminData(type, {
        period: period.start || period.end ? {
          start: period.start ? new Date(period.start).toISOString() : null,
          end: period.end ? new Date(period.end).toISOString() : null,
        } : null,
        format: type === "generations" ? format : undefined,
      })
      if (!response.ok) throw new Error("Export failed")

      const exportResult: ExportResult = {}
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${type}_export_${new Date().toISOString().split("T")[0]}.${type === "generations" ? format : "csv"}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
      return exportResult
    },
    onSuccess: (result) => {
      onExportCompleted?.(result)
      onClose()
    }
  })

  const labels = {
    users: "Liste des utilisateurs",
    generations: "Historique des générations",
    billing: "Données de facturation"
  }

  return (
    <div className="app-overlay">
      <div className="app-modal export-modal">
        <h3>Exporter : {labels[type]}</h3>
        
        <div className="alert-box alert-box--warning">
          <strong>⚠️ AVERTISSEMENT SÉCURITÉ</strong>
          <p>Cet export contient des données sensibles. L'opération sera journalisée et rattachée à votre compte admin.</p>
        </div>

        <div className="export-filters">
          <div className="filter-field">
            <label>Date de début (Optionnel)</label>
            <input type="date" value={period.start} onChange={(e) => setPeriod({ ...period, start: e.target.value })} />
          </div>
          <div className="filter-field">
            <label>Date de fin (Optionnel)</label>
            <input type="date" value={period.end} onChange={(e) => setPeriod({ ...period, end: e.target.value })} />
          </div>
          {type === "generations" && (
            <div className="filter-field">
              <label>Format</label>
              <select value={format} onChange={(e) => setFormat(e.target.value)}>
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
              </select>
            </div>
          )}
        </div>

        <div className="confirmation-area">
          <label className="checkbox-label">
            <input 
              type="checkbox" 
              checked={confirmed} 
              onChange={(e) => setConfirmed(e.target.checked)} 
            />
            Je confirme vouloir exporter ces données et j'ai conscience de ma responsabilité quant à leur protection.
          </label>
        </div>

        <div className="app-actions app-actions--end">
          <button className="text-button" onClick={onClose}>Annuler</button>
          <button 
            className="action-button action-button--primary" 
            disabled={!confirmed || exportMutation.isPending}
            onClick={() => exportMutation.mutate()}
          >
            {exportMutation.isPending ? "Génération..." : "Confirmer l'export"}
          </button>
        </div>
      </div>
    </div>
  )
}

export function AdminSettingsPage() {
  const { canExport } = useAdminPermissions()
  const [activeExport, setActiveExport] = useState<ExportModalProps["type"] | null>(null)

  const handleExportCompleted = (type: ExportModalProps["type"], result: ExportResult) => {
    void type
    void result
  }

  return (
    <div className="admin-control-page">
      <header className="admin-page-header">
        <h2>Paramètres & Exports</h2>
      </header>

      <section className="control-section">
        <h3>Exports de données</h3>
        <p className="section-description">Téléchargez les données brutes pour reporting ou backup.</p>

        <div className="export-list">
          <div className="export-card">
            <div className="export-info">
              <h4>Utilisateurs</h4>
              <p>Liste complète, plans, statuts et IDs Stripe.</p>
            </div>
            {canExport ? (
              <button className="action-button" onClick={() => setActiveExport("users")}>
                Exporter (CSV)
              </button>
            ) : (
              <span className="export-disabled-note">Export indisponible pour ce profil.</span>
            )}
          </div>

          <div className="export-card">
            <div className="export-info">
              <h4>Jobs Astral</h4>
              <p>Volumes, latence et erreurs (sans contenu).</p>
            </div>
            {canExport ? (
              <button className="action-button" onClick={() => setActiveExport("generations")}>
                Exporter (CSV/JSON)
              </button>
            ) : (
              <span className="export-disabled-note">Export indisponible pour ce profil.</span>
            )}
          </div>

          <div className="export-card">
            <div className="export-info">
              <h4>Facturation</h4>
              <p>Abonnements, prix, dates et échecs.</p>
            </div>
            {canExport ? (
              <button className="action-button" onClick={() => setActiveExport("billing")}>
                Exporter (CSV)
              </button>
            ) : (
              <span className="export-disabled-note">Export indisponible pour ce profil.</span>
            )}
          </div>
        </div>
      </section>

      {canExport && activeExport && (
        <ExportModal 
          type={activeExport} 
          onClose={() => setActiveExport(null)} 
          onExportCompleted={(result) => handleExportCompleted(activeExport, result)}
        />
      )}
    </div>
  )
}

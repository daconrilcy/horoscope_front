import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import {
  adminOperationsQueryKeys,
  useAdminFlaggedContent,
  useAdminSupportTickets,
  useReviewFlaggedContent,
} from "../../api/adminOperations"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import { formatLocalDate, formatLocalDateTime } from "../../utils/formatDate"
import "./AdminSupportPage.css"

export function AdminSupportPage() {
  const token = useAccessTokenSnapshot()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<"tickets" | "flagged">("tickets")
  const [statusFilter, setStatusFilter] = useState("all")

  const { data: ticketsData, isLoading: ticketsLoading } = useAdminSupportTickets(
    statusFilter,
    Boolean(token && activeTab === "tickets"),
  )

  const { data: flaggedData, isLoading: flaggedLoading } = useAdminFlaggedContent(
    Boolean(token && activeTab === "flagged"),
  )

  const reviewMutation = useReviewFlaggedContent()
  const handleReviewFlaggedContent = (id: number, status: string) => {
    reviewMutation.mutate({ id, status }, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: adminOperationsQueryKeys.flaggedContent })
      },
    })
  }

  return (
    <div className="admin-support-page">
      <header className="admin-page-header">
        <h2>Support & Modération</h2>
        <div className="admin-tabs">
          <button 
            className={`tab-button ${activeTab === "tickets" ? "tab-button--active" : ""}`}
            onClick={() => setActiveTab("tickets")}
          >
            Tickets Support
          </button>
          <button 
            className={`tab-button ${activeTab === "flagged" ? "tab-button--active" : ""}`}
            onClick={() => setActiveTab("flagged")}
          >
            Contenus Signalés
          </button>
        </div>
      </header>

      <section className="support-content">
        {activeTab === "tickets" ? (
          <div className="tickets-section">
            <div className="filter-bar">
              <label>Statut :</label>
              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option value="all">Tous</option>
                <option value="open">Ouverts</option>
                <option value="in_progress">En cours</option>
                <option value="resolved">Résolus</option>
              </select>
            </div>

            {ticketsLoading ? (
              <div className="loading-placeholder">Chargement des tickets...</div>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Titre</th>
                    <th>Utilisateur</th>
                    <th>Catégorie</th>
                    <th>Priorité</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {ticketsData?.data.map(ticket => (
                    <tr key={ticket.id}>
                      <td>#{ticket.id}</td>
                      <td className="ticket-title">{ticket.title}</td>
                      <td>
                        <button className="link-button" onClick={() => navigate(`/admin/users/${ticket.user_id}`)}>
                          {ticket.user_email}
                        </button>
                      </td>
                      <td>{ticket.category}</td>
                      <td>
                        <span className={`badge badge--priority-${ticket.priority.toLowerCase()}`}>
                          {ticket.priority}
                        </span>
                      </td>
                      <td>{formatLocalDate(ticket.created_at)}</td>
                      <td>
                        <button className="text-button">Voir</button>
                      </td>
                    </tr>
                  ))}
                  {ticketsData?.data.length === 0 && (
                    <tr>
                      <td colSpan={7} className="empty-table-state">Aucun ticket trouvé.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}
          </div>
        ) : (
          <div className="flagged-section">
            {flaggedLoading ? (
              <div className="loading-placeholder">Chargement des signalements...</div>
            ) : (
              <div className="flagged-grid">
                {flaggedData?.data.map(content => (
                  <div key={content.id} className="flagged-card">
                    <div className="flagged-card-header">
                      <span className="content-type">{content.content_type}</span>
                      <span className="reported-date">{formatLocalDateTime(content.reported_at)}</span>
                    </div>
                    <p className="excerpt">"{content.excerpt}"</p>
                    <div className="flagged-card-footer">
                      <div className="user-info">
                        Signalé par : 
                        <button className="link-button" onClick={() => navigate(`/admin/users/${content.user_id}`)}>
                          {content.user_email}
                        </button>
                      </div>
                      <div className="card-actions">
                        <button 
                          className="action-button action-button--success"
                          onClick={() => handleReviewFlaggedContent(content.id, "resolved")}
                          disabled={reviewMutation.isPending}
                        >
                          Traiter
                        </button>
                        <button 
                          className="action-button action-button--danger"
                          onClick={() => handleReviewFlaggedContent(content.id, "dismissed")}
                          disabled={reviewMutation.isPending}
                        >
                          Ignorer
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                {flaggedData?.data.length === 0 && (
                  <div className="empty-state">Aucun contenu à modérer.</div>
                )}
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  )
}

import React, { useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { apiFetch } from "../../api/client"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import "./AdminUsersPage.css"

interface UserSearchItem {
  id: number
  email: string
  role: string
  plan_code: string | null
  subscription_status: string | null
  created_at: string
}

export function AdminUsersPage() {
  const token = useAccessTokenSnapshot()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const initialFilter = searchParams.get("filter")
  const [searchQuery, setSearchQuery] = useState(initialFilter === "payment_failure" ? "payment_failure" : "")
  const [appliedQuery, setAppliedQuery] = useState(searchQuery)

  const { data, isLoading, error } = useQuery<{ data: UserSearchItem[], total: number }>({
    queryKey: ["admin-users-search", appliedQuery],
    queryFn: async () => {
      const response = await apiFetch(`/v1/admin/users?q=${encodeURIComponent(appliedQuery)}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) throw new Error("Search failed")
      return response.json()
    },
    enabled: Boolean(token),
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setAppliedQuery(searchQuery)
  }

  return (
    <div className="admin-users-page">
      <header className="admin-page-header">
        <h2>Gestion des utilisateurs</h2>
      </header>

      <section className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <input 
            type="text" 
            placeholder="Rechercher par email ou ID..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button">Rechercher</button>
        </form>
      </section>

      <section className="results-section">
        {isLoading ? (
          <div className="loading-placeholder">Recherche en cours...</div>
        ) : error ? (
          <div className="error-message">Erreur lors de la recherche.</div>
        ) : (
          <div className="table-container">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Utilisateur</th>
                  <th>Rôle</th>
                  <th>Plan</th>
                  <th>Statut</th>
                  <th>Inscription</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.data.map((user) => (
                  <tr key={user.id} className="user-row" onClick={() => navigate(`/admin/users/${user.id}`)}>
                    <td>{user.id}</td>
                    <td>{user.email}</td>
                    <td><span className={`badge badge--role-${user.role}`}>{user.role}</span></td>
                    <td>{user.plan_code || "free"}</td>
                    <td>
                      <span className={`badge badge--status-${user.subscription_status || "none"}`}>
                        {user.subscription_status || "N/A"}
                      </span>
                    </td>
                    <td>{new Date(user.created_at).toLocaleDateString()}</td>
                    <td>
                      <button className="text-button" onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/admin/users/${user.id}`)
                      }}>
                        Détails
                      </button>
                    </td>
                  </tr>
                ))}
                {data?.data.length === 0 && (
                  <tr>
                    <td colSpan={7} className="empty-table-state">Aucun utilisateur trouvé.</td>
                  </tr>
                )}
              </tbody>
            </table>
            <div className="table-footer">
              Total : {data?.total || 0} utilisateurs
            </div>
          </div>
        )}
      </section>
    </div>
  )
}

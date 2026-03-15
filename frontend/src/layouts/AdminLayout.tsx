import React from "react"
import { Link, useLocation } from "react-router-dom"
import "./AdminLayout.css"

export interface AdminSection {
  path: string
  label: string
  Icon: React.ComponentType<{ className?: string }>
}

interface AdminLayoutProps {
  title: string
  sections: AdminSection[]
  backToHubLabel: string
  children: React.ReactNode
  className?: string
}

export function AdminLayout({ 
  title, 
  sections, 
  backToHubLabel,
  children, 
  className 
}: AdminLayoutProps) {
  const location = useLocation()
  const normalizedPath = location.pathname.replace(/\/$/, "")
  const isHub = normalizedPath === "/admin"

  return (
    <div className={`admin-page ${className ?? ""}`}>
      <header className="admin-header">
        <h1>{title}</h1>
        {!isHub && (
          <Link to="/admin" className="admin-back-link">
            {backToHubLabel}
          </Link>
        )}
      </header>

      {isHub ? (
        <section className="admin-hub" aria-label="Sections d'administration">
          <div className="admin-grid">
            {sections.map((section) => (
              <Link
                key={section.path}
                to={section.path}
                className="admin-card"
                aria-label={section.label}
              >
                <section.Icon className="admin-card-icon-svg" />
                <span className="admin-card-label">{section.label}</span>
              </Link>
            ))}
          </div>
        </section>
      ) : (
        <div className="admin-content">
          {children}
        </div>
      )}
    </div>
  )
}

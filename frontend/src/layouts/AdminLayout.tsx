import React from "react"
import { Link, NavLink, useLocation } from "react-router-dom"
import { useAdminPermissions } from "../state/AdminPermissionsContext"
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
  const { allowedSections } = useAdminPermissions()
  const location = useLocation()
  const normalizedPath = location.pathname.replace(/\/$/, "")
  const isHub = normalizedPath === "/admin"

  // Filter sections based on permissions
  const filteredSections = sections.filter(section => {
    const sectionCode = section.path.split("/").pop()
    return sectionCode && (allowedSections.includes(sectionCode) || sectionCode === "admin")
  })

  return (
    <div className={`admin-layout ${className ?? ""}`}>
      <aside className="admin-sidebar">
        <div className="admin-sidebar-header">
          <Link to="/admin" className="admin-sidebar-logo">
            {title}
          </Link>
        </div>
        <nav className="admin-sidebar-nav" aria-label="Sections d'administration">
          {filteredSections.map((section) => (
            <NavLink
              key={section.path}
              to={section.path}
              className={({ isActive }) => 
                `admin-sidebar-link ${isActive ? "admin-sidebar-link--active" : ""}`
              }
              aria-current={location.pathname === section.path ? "page" : undefined}
            >
              <section.Icon className="admin-sidebar-icon" />
              <span className="admin-sidebar-label">{section.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="admin-main">
        {!isHub && (
          <header className="admin-content-header">
            <Link to="/admin" className="admin-back-link">
              {backToHubLabel}
            </Link>
          </header>
        )}

        <div className="admin-container">
          {children}
        </div>
      </main>
    </div>
  )
}

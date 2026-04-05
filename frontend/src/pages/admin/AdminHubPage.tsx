import React from "react"
import { Link, useOutletContext } from "react-router-dom"
import { useAdminPermissions } from "../../state/AdminPermissionsContext"

export function AdminHubPage() {
  const { sections } = useOutletContext<{ sections: any[] }>()
  const { allowedSections } = useAdminPermissions()
  
  const filteredSections = sections.filter(section => {
    const sectionCode = section.path.split("/").pop()
    return sectionCode && allowedSections.includes(sectionCode)
  })

  return (
    <section className="admin-hub" aria-label="Hub d'administration">
      <div className="admin-grid">
        {filteredSections.map((section) => (
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
  )
}

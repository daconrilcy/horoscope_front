import type { ReactNode } from "react"
import { Link } from "react-router-dom"

export type DashboardCardProps = {
  label: string
  path: string
  icon: ReactNode
  description?: string
}

export function DashboardCard({ label, path, icon, description }: DashboardCardProps) {
  return (
    <Link
      to={path}
      className="dashboard-card"
      aria-label={`Aller à ${label}`}
    >
      <span className="dashboard-card-icon" aria-hidden="true">
        {icon}
      </span>
      <span className="dashboard-card-label">{label}</span>
      {description && (
        <span className="dashboard-card-description">{description}</span>
      )}
    </Link>
  )
}

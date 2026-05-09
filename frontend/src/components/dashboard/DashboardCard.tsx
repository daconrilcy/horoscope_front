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
      className="summary-card select-card"
      aria-label={`Aller à ${label}`}
    >
      <span className="summary-card-icon" aria-hidden="true">
        {icon}
      </span>
      <span className="summary-card-label">{label}</span>
      {description && (
        <span className="summary-card-description">{description}</span>
      )}
    </Link>
  )
}

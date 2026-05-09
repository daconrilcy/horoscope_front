// Garde applicatif qui limite une branche de route aux roles autorises.
import type { ReactNode } from "react"
import { Navigate } from "react-router-dom"

import { useAccessTokenSnapshot } from "../../utils/authToken"
import { useAuthMe } from "../../api/authMe"

type RoleGuardProps = {
  children: ReactNode
  roles: string[]
}

export function RoleGuard({ children, roles }: RoleGuardProps) {
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)

  if (authMe.isLoading) {
    return (
      <div className="app-panel">
        <div className="app-state app-state--loading" role="status" aria-live="polite">
          Vérification des permissions...
        </div>
      </div>
    )
  }

  if (authMe.isError || !authMe.data) {
    return <Navigate to="/dashboard" replace />
  }

  const userRole = authMe.data.role
  if (!roles.includes(userRole)) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

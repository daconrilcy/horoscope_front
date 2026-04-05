import type { ReactNode } from "react"
import { Navigate, useLocation } from "react-router-dom"

import { useAccessTokenSnapshot } from "../utils/authToken"
import { useAuthMe } from "../api/authMe"
import "./AdminGuard.css"

type AdminGuardProps = {
  children: ReactNode
}

export function AdminGuard({ children }: AdminGuardProps) {
  const token = useAccessTokenSnapshot()
  const location = useLocation()
  const authMe = useAuthMe(token)

  if (authMe.isLoading) {
    return (
      <div className="admin-guard-loading">
        <div className="spinner" role="status" aria-live="polite">
          <span className="sr-only">Vérification des permissions...</span>
        </div>
      </div>
    )
  }

  if (!token || authMe.isError || !authMe.data) {
    const returnTo = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/login?returnTo=${returnTo}`} replace />
  }

  if (authMe.data.role !== "admin") {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

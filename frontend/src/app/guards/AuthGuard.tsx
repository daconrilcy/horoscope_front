// Garde applicatif qui reserve les routes protegees aux sessions authentifiees.
import type { ReactNode } from "react"
import { Navigate, useLocation } from "react-router-dom"

import { useAuthMe } from "../../api/authMe"
import {
  clearAccessToken,
  hasUsableAccessToken,
  isAccessTokenExpired,
  useAccessTokenSnapshot,
} from "../../utils/authToken"

type AuthGuardProps = {
  children: ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const token = useAccessTokenSnapshot()
  const location = useLocation()
  const authMe = useAuthMe(token)

  if (token && !hasUsableAccessToken(token)) {
    clearAccessToken()
  }

  if (!token || isAccessTokenExpired(token)) {
    const returnTo = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/login?returnTo=${returnTo}`} replace />
  }

  if (authMe.isLoading || authMe.isFetching) {
    return (
      <div className="app-panel">
        <div className="app-state app-state--loading" role="status" aria-live="polite">
          Vérification de la session...
        </div>
      </div>
    )
  }

  if (authMe.isError || !authMe.data) {
    clearAccessToken()
    const returnTo = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/login?returnTo=${returnTo}`} replace />
  }

  return <>{children}</>
}

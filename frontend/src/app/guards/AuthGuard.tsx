import type { ReactNode } from "react"
import { Navigate, useLocation } from "react-router-dom"

import { useAccessTokenSnapshot } from "../../utils/authToken"

type AuthGuardProps = {
  children: ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const token = useAccessTokenSnapshot()
  const location = useLocation()

  if (!token) {
    const returnTo = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/login?returnTo=${returnTo}`} replace />
  }

  return <>{children}</>
}

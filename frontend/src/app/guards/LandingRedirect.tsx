import { Suspense, lazy } from "react"
import { Navigate } from "react-router-dom"
import { isAccessTokenExpired, useAccessTokenSnapshot, clearAccessToken } from "../../utils/authToken"

const LandingPage = lazy(() => import("../../pages/landing/LandingPage"))

export function LandingRedirect() {
  const token = useAccessTokenSnapshot()

  if (token && isAccessTokenExpired(token)) {
    clearAccessToken()
    return (
      <Suspense fallback={null}>
        <LandingPage />
      </Suspense>
    )
  }

  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <Suspense fallback={null}>
      <LandingPage />
    </Suspense>
  )
}

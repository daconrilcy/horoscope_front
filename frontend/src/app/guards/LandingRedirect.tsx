// Route publique chargeant la landing avec son scope de variables semantiques.
import { Suspense, lazy } from "react"
import { Navigate } from "react-router-dom"
import { isAccessTokenExpired, useAccessTokenSnapshot, clearAccessToken } from "../../utils/authToken"
import "../../layouts/LandingLayout.css"

const LandingPage = lazy(() => import("../../pages/landing/LandingPage"))

function ScopedLandingPage() {
  return (
    <div className="landing-layout">
      <LandingPage />
    </div>
  )
}

export function LandingRedirect() {
  const token = useAccessTokenSnapshot()

  if (token && isAccessTokenExpired(token)) {
    clearAccessToken()
    return (
      <Suspense fallback={null}>
        <ScopedLandingPage />
      </Suspense>
    )
  }

  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <Suspense fallback={null}>
      <ScopedLandingPage />
    </Suspense>
  )
}

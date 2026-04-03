import { Navigate } from "react-router-dom"
import { isAccessTokenExpired, useAccessTokenSnapshot, clearAccessToken } from "../../utils/authToken"
import { LandingPage } from "../../pages/landing/LandingPage"

export function LandingRedirect() {
  const token = useAccessTokenSnapshot()

  if (token && isAccessTokenExpired(token)) {
    clearAccessToken()
    return <LandingPage />
  }

  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  return <LandingPage />
}

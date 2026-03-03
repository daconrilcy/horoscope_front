import { Navigate } from "react-router-dom"

import { clearAccessToken, isAccessTokenExpired, useAccessTokenSnapshot } from "../../utils/authToken"

export function RootRedirect() {
  const token = useAccessTokenSnapshot()

  if (token && isAccessTokenExpired(token)) {
    clearAccessToken()
    return <Navigate to="/login" replace />
  }

  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  return <Navigate to="/login" replace />
}

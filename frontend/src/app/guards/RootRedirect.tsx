import { Navigate } from "react-router-dom"

import { useAccessTokenSnapshot } from "../../utils/authToken"

export function RootRedirect() {
  const token = useAccessTokenSnapshot()

  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  return <Navigate to="/login" replace />
}

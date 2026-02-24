import { useNavigate, useLocation } from "react-router-dom"

import { clearAccessToken, useAccessTokenSnapshot } from "../../utils/authToken"
import { useAuthMe } from "../../api/authMe"

export function Header() {
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const navigate = useNavigate()
  const location = useLocation()

  function handleLogout() {
    clearAccessToken()
    navigate("/login", { replace: true })
  }

  // TodayPage (on /dashboard) has its own header title
  const showTitle = location.pathname !== "/dashboard"

  return (
    <header className="app-header">
      <div className="app-header-brand">
        {showTitle && <h1 className="app-header-title">Horoscope</h1>}
      </div>
      {token && (
        <div className="app-header-actions">
          {authMe.data && (
            <span className="app-header-user">
              <span className="app-header-role">
                {authMe.data.role === "user" ? "Utilisateur" : authMe.data.role}
              </span>
            </span>
          )}
          <button
            type="button"
            className="app-header-logout"
            onClick={handleLogout}
          >
            Se déconnecter
          </button>
        </div>
      )}
    </header>
  )
}

import { useNavigate, useLocation } from "react-router-dom"

import { clearAccessToken, useAccessTokenSnapshot } from "../../utils/authToken"
import { useAuthMe } from "../../api/authMe"
import { detectLang } from "../../i18n/astrology"
import { commonTranslations } from "../../i18n/common"

export function Header() {
  const lang = detectLang()
  const t = commonTranslations(lang)
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const navigate = useNavigate()
  const location = useLocation()

  function handleLogout() {
    clearAccessToken()
    navigate("/login", { replace: true })
  }

  // Dashboard pages (landing and detailed horoscope) have their own header titles
  const normalizedPath = location.pathname.replace(/\/+$/, "") || "/"
  const isDashboard = normalizedPath === "/dashboard" || normalizedPath === "/dashboard/horoscope"
  const showTitle = !isDashboard

  return (
    <header className={`app-header${isDashboard ? " app-header--dashboard" : ""}`}>
      <div className="app-header-brand">
        {showTitle && <h1 className="app-header-title">{t.header.appTitle}</h1>}
      </div>
      {token && (
        <div className="app-header-actions">
          {authMe.data && (
            <span className="app-header-user">
              <span className="app-header-role">
                {authMe.data.role === "user" ? t.header.defaultRole : authMe.data.role}
              </span>
            </span>
          )}
          <button
            type="button"
            className="app-header-logout"
            onClick={handleLogout}
          >
            {t.header.logout}
          </button>
        </div>
      )}
    </header>
  )
}

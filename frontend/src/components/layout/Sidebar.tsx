import { NavLink } from "react-router-dom"

import { useAccessTokenSnapshot } from "../../utils/authToken"
import { useAuthMe } from "../../api/authMe"
import { getAllNavItems } from "../../ui/nav"
import { detectLang } from "../../i18n/astrology"
import { navigationTranslations } from "../../i18n/navigation"

export function Sidebar() {
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const role = authMe.data?.role ?? null

  const lang = detectLang()
  const t = navigationTranslations(lang)
  const navItems = getAllNavItems(role)

  return (
    <aside className="app-sidebar">
      <nav className="app-sidebar-nav">
        {navItems.map((item) => {
          const translatedLabel = t.nav[item.key as keyof typeof t.nav] ?? item.label
          
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `app-sidebar-link ${isActive ? "app-sidebar-link--active" : ""}`
              }
            >
              {translatedLabel}
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}

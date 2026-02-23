import { NavLink } from "react-router-dom"

import { useAccessTokenSnapshot } from "../../utils/authToken"
import { useAuthMe } from "../../api/authMe"
import { getMobileNavItems } from "./navItems"

export function BottomNav() {
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const role = authMe.data?.role ?? null

  const mobileNavItems = getMobileNavItems(role)

  return (
    <nav className="app-bottom-nav">
      {mobileNavItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) =>
            `app-bottom-nav-link ${isActive ? "app-bottom-nav-link--active" : ""}`
          }
        >
          {item.mobileLabel ?? item.label}
        </NavLink>
      ))}
    </nav>
  )
}

import { NavLink } from "react-router-dom"

import { useAccessTokenSnapshot } from "../../utils/authToken"
import { useAuthMe } from "../../api/authMe"
import { getAllNavItems } from "../../ui/nav"

export function Sidebar() {
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const role = authMe.data?.role ?? null

  const navItems = getAllNavItems(role)

  return (
    <aside className="app-sidebar">
      <nav className="app-sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `app-sidebar-link ${isActive ? "app-sidebar-link--active" : ""}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

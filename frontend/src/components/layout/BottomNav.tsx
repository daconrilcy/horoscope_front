import { Link, useLocation } from 'react-router-dom'
import { getMobileNavItems } from '../../ui/nav'
import { useAccessTokenSnapshot } from "../../utils/authToken"
import { useAuthMe } from "../../api/authMe"

export function BottomNav() {
  const { pathname } = useLocation()
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const role = authMe.data?.role ?? null
  
  const navItems = getMobileNavItems(role)

  return (
    <nav className="bottom-nav" aria-label="Navigation principale">
      {navItems.map(({ key, label, icon: Icon, path }) => {
        const isActive = pathname === path || pathname.startsWith(path + '/')
        return (
          <Link
            key={key}
            to={path}
            className={`bottom-nav__item${isActive ? ' bottom-nav__item--active' : ''}`}
            aria-current={isActive ? 'page' : undefined}
          >
            <Icon size={24} strokeWidth={1.75} />
            <span className="bottom-nav__label">{label}</span>
          </Link>
        )
      })}
    </nav>
  )
}

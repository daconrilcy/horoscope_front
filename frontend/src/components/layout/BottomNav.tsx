import { Link, useLocation } from 'react-router-dom'
import { getMobileNavItems } from '../../ui/nav'
import { useAccessTokenSnapshot } from "../../utils/authToken"
import { useAuthMe } from "../../api/authMe"
import { detectLang } from "../../i18n/astrology"
import { navigationTranslations } from "../../i18n/navigation"

export function BottomNav() {
  const { pathname } = useLocation()
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const role = authMe.data?.role ?? null
  
  const lang = detectLang()
  const t = navigationTranslations(lang)
  const navItems = getMobileNavItems(role)

  return (
    <nav className="bottom-nav" aria-label="Navigation principale">
      {navItems.map(({ key, label, icon: Icon, path }) => {
        const isActive = pathname === path || pathname.startsWith(path + '/')
        const translatedLabel = t.nav[key as keyof typeof t.nav] ?? label
        
        return (
          <Link
            key={key}
            to={path}
            className={`bottom-nav__item${isActive ? ' bottom-nav__item--active' : ''}`}
            aria-current={isActive ? 'page' : undefined}
          >
            <Icon size={24} strokeWidth={1.75} aria-hidden="true" />
            <span className="bottom-nav__label">{translatedLabel}</span>
          </Link>
        )
      })}
    </nav>
  )
}

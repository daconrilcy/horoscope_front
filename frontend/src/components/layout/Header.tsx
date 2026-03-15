import "./Header.css"

import { Menu, Moon, Sun, X } from "lucide-react"
import { useState } from "react"

import { useAuthMe } from "@api/authMe"
import { detectLang } from "@i18n/astrology"
import { commonTranslations } from "@i18n/common"
import { useSidebarContext } from "@state/SidebarContext"
import { useThemeSafe } from "@state/ThemeProvider"
import { UserAvatar, UserMenu } from "@ui"
import { APP_LOGO, APP_NAME } from "@utils/appConfig"
import { useAccessTokenSnapshot } from "@utils/authToken"

export function Header() {
  const lang = detectLang()
  const t = commonTranslations(lang)
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const { sidebarState, toggleSidebar } = useSidebarContext()
  const themeContext = useThemeSafe()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const theme = themeContext?.theme ?? "light"
  const toggleTheme = themeContext?.toggleTheme ?? (() => {})

  const hamburgerLabel = sidebarState === "hidden" ? t.header.openMenu : t.header.closeMenu
  const avatarEmail = authMe.data?.email ?? "?"
  const avatarRole = authMe.data?.role ?? "user"

  return (
    <header className="app-header">
      <div className="app-header-left">
        <button
          type="button"
          className="app-header-hamburger"
          onClick={toggleSidebar}
          aria-label={hamburgerLabel}
        >
          {sidebarState === "hidden" ? <Menu size={24} aria-hidden="true" /> : <X size={24} aria-hidden="true" />}
        </button>
      </div>
      <div className="app-header-brand">
        <img src={APP_LOGO} alt={APP_NAME} className="app-header-logo" />
        <span className="app-header-title">{APP_NAME}</span>
      </div>
      <div className="app-header-actions">
        <button
          type="button"
          className="app-header-theme-toggle"
          onClick={toggleTheme}
          aria-label={t.header.toggleTheme}
        >
          {theme === "dark"
            ? <Sun size={20} aria-hidden="true" />
            : <Moon size={20} aria-hidden="true" />
          }
        </button>
        <div className="app-header-avatar-wrapper">
          <UserAvatar
            email={avatarEmail}
            displayName={t.header.openUserMenu}
            onClick={() => setIsUserMenuOpen((value) => !value)}
            aria-expanded={isUserMenuOpen}
          />
          <UserMenu
            email={avatarEmail}
            role={avatarRole}
            isOpen={isUserMenuOpen}
            onClose={() => setIsUserMenuOpen(false)}
          />
        </div>
      </div>
    </header>
  )
}

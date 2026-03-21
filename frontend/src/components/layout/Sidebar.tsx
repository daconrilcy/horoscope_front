import "./Sidebar.css"

import { NavLink } from "react-router-dom"

import { useEffect, useRef } from "react"

import { useAuthMe } from "@api/authMe"
import { detectLang } from "@i18n/astrology"
import { navigationTranslations } from "@i18n/navigation"
import { useSidebarContext } from "@state/SidebarContext"
import { useAccessTokenSnapshot } from "@utils/authToken"
import { useQueryClient } from "@tanstack/react-query"
import { prefetchDailyHoroscope } from "../../utils/prefetchHelpers"
import { getAllNavItems } from "../../ui/nav"

export function Sidebar() {
  const token = useAccessTokenSnapshot()
  const queryClient = useQueryClient()
  const authMe = useAuthMe(token)
  const role = authMe.data?.role ?? null
  const { sidebarState, collapseSidebar, closeSidebar } = useSidebarContext()
  const firstLinkRef = useRef<HTMLAnchorElement | null>(null)

  const lang = detectLang()
  const t = navigationTranslations(lang)
  const navItems = getAllNavItems(role)

  useEffect(() => {
    if (sidebarState === "expanded") {
      firstLinkRef.current?.focus()
    }
  }, [sidebarState])

  return (
    <>
      {sidebarState === "expanded" && (
        <div
          className="sidebar-backdrop"
          onClick={closeSidebar}
          aria-hidden="true"
        />
      )}
      <aside
        className={`app-sidebar app-sidebar--${sidebarState}`}
        aria-hidden={sidebarState === "hidden"}
      >
        <nav className="app-sidebar-nav" aria-label="Navigation principale">
          {navItems.map((item, index) => {
            const translatedLabel = t.nav[item.key as keyof typeof t.nav] ?? item.label
            const Icon = item.icon

            return (
              <NavLink
                key={item.path}
                ref={index === 0 ? firstLinkRef : undefined}
                to={item.path}
                onClick={() => {
                  collapseSidebar()
                  if (item.key === 'today') {
                    void prefetchDailyHoroscope(queryClient, token)
                  }
                }}
                className={({ isActive }) =>
                  `app-sidebar-link${isActive ? " app-sidebar-link--active" : ""}`
                }
                title={sidebarState === "icon-only" ? translatedLabel : undefined}
              >
                <Icon className="app-sidebar-link__icon" size={20} aria-hidden="true" />
                <span className="app-sidebar-link__label">{translatedLabel}</span>
              </NavLink>
            )
          })}
        </nav>
      </aside>
    </>
  )
}

import { useLocation, Link, useNavigate } from "react-router-dom"
import { useCallback, useMemo } from "react"
import { detectLang } from "../../i18n/astrology"
import { settingsTranslations } from "../../i18n/settings"

interface Tab {
  path: string
  labelKey: "account" | "subscription" | "usage"
}

const tabs: Tab[] = [
  { path: "account", labelKey: "account" },
  { path: "subscription", labelKey: "subscription" },
  { path: "usage", labelKey: "usage" },
]

export function SettingsTabs() {
  const lang = detectLang()
  const labels = settingsTranslations.tabs[lang]
  const location = useLocation()
  const navigate = useNavigate()

  const isActive = useCallback(
    (path: string): boolean => {
      return location.pathname.endsWith(`/${path}`)
    },
    [location.pathname]
  )

  const activeIndex = useMemo((): number => {
    return tabs.findIndex((tab) => isActive(tab.path))
  }, [isActive])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      let nextIndex = activeIndex

      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        e.preventDefault()
        nextIndex = (activeIndex + 1) % tabs.length
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault()
        nextIndex = (activeIndex - 1 + tabs.length) % tabs.length
      } else if (e.key === "Home") {
        e.preventDefault()
        nextIndex = 0
      } else if (e.key === "End") {
        e.preventDefault()
        nextIndex = tabs.length - 1
      } else {
        return
      }

      if (nextIndex !== activeIndex) {
        navigate(tabs[nextIndex].path)
        const nextTab = document.getElementById(`settings-tab-${tabs[nextIndex].path}`)
        nextTab?.focus()
      }
    },
    [activeIndex, navigate]
  )

  return (
    <nav
      className="settings-tabs"
      aria-label={labels.navLabel}
      onKeyDown={handleKeyDown}
    >
      {tabs.map((tab) => {
        const active = isActive(tab.path)
        return (
          <Link
            key={tab.path}
            to={tab.path}
            aria-current={active ? "page" : undefined}
            id={`settings-tab-${tab.path}`}
            className={`settings-tab ${active ? "settings-tab--active" : ""}`}
          >
            {labels[tab.labelKey]}
          </Link>
        )
      })}
    </nav>
  )
}

import { Outlet } from "react-router-dom"
import { SettingsTabs } from "../components/settings/SettingsTabs"
import { detectLang } from "../i18n/astrology"
import { settingsTranslations } from "../i18n/settings"

export function SettingsPage() {
  const lang = detectLang()
  const { title } = settingsTranslations.page[lang]

  return (
    <div className="settings-layout">
      <h1 className="settings-title">{title}</h1>
      <SettingsTabs />
      <div className="settings-content">
        <Outlet />
      </div>
    </div>
  )
}

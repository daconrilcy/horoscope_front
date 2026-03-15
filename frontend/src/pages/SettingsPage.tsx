import { Outlet } from "react-router-dom"
import { SettingsLayout } from "../layouts"
import { detectLang } from "../i18n/astrology"
import { settingsTranslations } from "../i18n/settings"

export function SettingsPage() {
  const lang = detectLang()
  const { title } = settingsTranslations.page[lang]

  return (
    <SettingsLayout title={title}>
      <Outlet />
    </SettingsLayout>
  )
}

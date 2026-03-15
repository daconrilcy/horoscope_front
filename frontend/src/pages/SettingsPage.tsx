import { Outlet } from "react-router-dom"
import { SettingsLayout } from "../layouts"
import { useTranslation } from "../i18n"

export function SettingsPage() {
  const { title } = useTranslation("settings")

  return (
    <SettingsLayout title={title}>
      <Outlet />
    </SettingsLayout>
  )
}

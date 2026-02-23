import { detectLang } from "../../i18n/astrology"
import { adminTranslations } from "../../i18n/admin"
import { OpsMonitoringPanel } from "../../components/OpsMonitoringPanel"

export function MonitoringAdmin() {
  const lang = detectLang()
  const t = adminTranslations.monitoring[lang]

  return (
    <section className="monitoring-admin" aria-labelledby="monitoring-admin-title">
      <h2 id="monitoring-admin-title" data-testid="monitoring-admin-title">{t.title}</h2>
      <OpsMonitoringPanel />
    </section>
  )
}

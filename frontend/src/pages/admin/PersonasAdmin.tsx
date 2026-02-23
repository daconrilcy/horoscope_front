import { detectLang } from "../../i18n/astrology"
import { adminTranslations } from "../../i18n/admin"
import { OpsPersonaPanel } from "../../components/OpsPersonaPanel"

export function PersonasAdmin() {
  const lang = detectLang()
  const t = adminTranslations.personas[lang]

  return (
    <section className="personas-admin" aria-labelledby="personas-admin-title">
      <h2 id="personas-admin-title" data-testid="personas-admin-title">{t.title}</h2>
      <OpsPersonaPanel />
    </section>
  )
}

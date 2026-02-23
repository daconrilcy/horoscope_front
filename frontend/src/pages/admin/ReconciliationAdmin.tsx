import { detectLang } from "../../i18n/astrology"
import { adminTranslations } from "../../i18n/admin"
import { B2BReconciliationPanel } from "../../components/B2BReconciliationPanel"

export function ReconciliationAdmin() {
  const lang = detectLang()
  const t = adminTranslations.reconciliation[lang]

  return (
    <section className="reconciliation-admin" aria-labelledby="reconciliation-admin-title">
      <h2 id="reconciliation-admin-title" data-testid="reconciliation-admin-title">
        {t.title}
      </h2>
      <B2BReconciliationPanel />
    </section>
  )
}

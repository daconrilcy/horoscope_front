import { BillingPanel } from "../../components/BillingPanel"
import { detectLang } from "../../i18n/astrology"
import { settingsTranslations } from "../../i18n/settings"

export function SubscriptionSettings() {
  const lang = detectLang()
  const { title } = settingsTranslations.subscription[lang]

  return (
    <section className="subscription-settings">
      <h2 className="settings-section-title">{title}</h2>
      <BillingPanel />
    </section>
  )
}

import { useBillingSubscription } from "@api/billing"
import { detectLang } from "@i18n/astrology"
import { settingsTranslations } from "@i18n/settings"
import { Check, CreditCard } from "lucide-react"
import "./Settings.css"

const PLANS = [
  { code: null,                label: "Gratuit",        limit: "5 msg/jour",   price: "0 €" },
  { code: "basic-entry",       label: "Basic",          limit: "50 msg/jour",  price: "9 €/mois" },
  { code: "premium-unlimited", label: "Premium",        limit: "1000 msg/jour",price: "29 €/mois" },
]

export function SubscriptionSettings() {
  const lang = detectLang()
  const t = settingsTranslations.subscription[lang]
  const { data: subscription, isLoading } = useBillingSubscription()

  const currentPlanCode = subscription?.active_plan?.code || null

  return (
    <div className="subscription-settings">
      <section className="settings-card">
        <h2 className="settings-section-title settings-section-title--decorated">
          {t.title}
        </h2>

        {isLoading ? (
          <p className="settings-save-feedback settings-save-feedback--saving">Chargement...</p>
        ) : (
          <>
            <h3 className="settings-section-title" style={{ marginTop: '24px', fontSize: '1.2rem' }}>
              {t.availablePlans}
            </h3>
            <div className="subscription-plans-grid">
              {PLANS.map((plan) => {
                const isActive = currentPlanCode === plan.code
                return (
                  <div 
                    key={plan.code || 'free'} 
                    className={`subscription-plan-card ${isActive ? 'subscription-plan-card--active' : ''}`}
                  >
                    {isActive && (
                      <div className="subscription-plan-card__badge">
                        <Check size={12} /> {t.active}
                      </div>
                    )}
                    <h4 className="subscription-plan-card__name">{plan.label}</h4>
                    <div className="subscription-plan-card__limit">{plan.limit}</div>
                    <div className="subscription-plan-card__price">{plan.price}</div>
                  </div>
                )
              })}
            </div>

            <div className="subscription-credits-section">
              <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                <div className="default-astrologer-option__avatar--placeholder" style={{ width: '48px', height: '48px' }}>
                  <CreditCard size={24} />
                </div>
                <div>
                  <h3 className="subscription-credits-section__title">{t.buyCredits}</h3>
                  <p className="subscription-credits-section__desc">{t.buyCreditsDesc}</p>
                  <button 
                    type="button" 
                    className="settings-tab" 
                    disabled 
                    title={t.soon}
                    style={{ opacity: 0.6, cursor: 'not-allowed' }}
                  >
                    {t.buyCredits} — {t.soon}
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  )
}

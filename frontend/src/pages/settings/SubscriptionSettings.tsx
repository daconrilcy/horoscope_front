import { useState, useEffect } from "react"
import { useBillingSubscription, useChangePlan, useCheckoutEntryPlan } from "@api/billing"
import { useQueryClient } from "@tanstack/react-query"
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

  const currentPlanCode = subscription?.plan?.code || null
  const [selectedPlanCode, setSelectedPlanCode] = useState<string | null | undefined>(undefined)

  useEffect(() => {
    if (!isLoading && selectedPlanCode === undefined) {
      setSelectedPlanCode(currentPlanCode)
    }
  }, [isLoading, currentPlanCode, selectedPlanCode])

  const displaySelected = selectedPlanCode === undefined ? currentPlanCode : selectedPlanCode

  const changePlan = useChangePlan()
  const checkoutPlan = useCheckoutEntryPlan()
  const qc = useQueryClient()

  const handleValidate = () => {
    if (selectedPlanCode === currentPlanCode) return
    
    if (!selectedPlanCode) {
      alert(t.cancelSoon)
      return
    }

    const onSuccess = () => {
      void qc.invalidateQueries({ queryKey: ["billing-subscription"] })
      void qc.invalidateQueries({ queryKey: ["chat-entitlement-usage"] })
    }
    const onError = (err: any) => {
      alert(err?.message || "Erreur lors de l'opération")
    }

    // Si l'utilisateur n'a pas de plan actif, il faut passer par le checkout
    if (!currentPlanCode || subscription?.status !== "active") {
      if (checkoutPlan.isPending) return
      checkoutPlan.mutate({ plan_code: selectedPlanCode }, { onSuccess, onError })
      return
    }

    // Sinon, c'est un changement de plan existant
    if (changePlan.isPending) return
    changePlan.mutate({ target_plan_code: selectedPlanCode }, { onSuccess, onError })
  }

  const isAnyPending = changePlan.isPending || checkoutPlan.isPending
  const hasChanges = displaySelected !== currentPlanCode

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
                const isCurrent = currentPlanCode === plan.code
                const isSelected = displaySelected === plan.code
                return (
                  <div 
                    key={plan.code || 'free'} 
                    className={`subscription-plan-card ${isSelected ? 'subscription-plan-card--active' : ''}`}
                    onClick={() => setSelectedPlanCode(plan.code)}
                    style={{ 
                      cursor: isAnyPending ? 'wait' : 'pointer',
                      opacity: isAnyPending ? 0.6 : 1,
                      borderColor: isCurrent && !isSelected ? 'rgba(255, 255, 255, 0.4)' : undefined
                    }}
                  >
                    {isCurrent && !isSelected && (
                      <div className="subscription-plan-card__badge" style={{ background: 'rgba(255, 255, 255, 0.2)', color: 'inherit', boxShadow: 'none' }}>
                        {t.currentPlan}
                      </div>
                    )}
                    {isSelected && (
                      <div className="subscription-plan-card__badge">
                        <Check size={12} /> {isCurrent ? t.currentPlan : t.selected}
                      </div>
                    )}
                    <h4 className="subscription-plan-card__name">
                      {plan.label}
                    </h4>
                    <div className="subscription-plan-card__limit">{plan.limit}</div>
                    <div className="subscription-plan-card__price">{plan.price}</div>
                  </div>
                )
              })}
            </div>

            <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '16px' }}>
               {hasChanges && displaySelected === null && (
                 <span className="settings-text-muted">{t.cancelSoon}</span>
               )}
               <button 
                  type="button"
                  className="settings-tab settings-tab--active"
                  style={{ 
                    minWidth: '160px', 
                    justifyContent: 'center', 
                    opacity: (!hasChanges || displaySelected === null || isAnyPending) ? 0.5 : 1, 
                    cursor: (!hasChanges || displaySelected === null || isAnyPending) ? 'not-allowed' : 'pointer' 
                  }}
                  onClick={handleValidate}
                  disabled={!hasChanges || displaySelected === null || isAnyPending}
               >
                  {isAnyPending ? t.validating : t.validatePlan}
               </button>
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

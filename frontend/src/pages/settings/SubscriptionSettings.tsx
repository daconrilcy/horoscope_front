import { useState, useEffect, useMemo } from "react"
import {
  useBillingSubscription,
  useBillingPlans,
  useStripeCheckoutSession,
  useStripePortalSession,
  useStripePortalSubscriptionUpdateSession,
  BillingApiError,
} from "@api/billing"
import { detectLang } from "@i18n/astrology"
import { settingsTranslations } from "@i18n/settings"
import { Check, CreditCard } from "lucide-react"
import "./Settings.css"

export function SubscriptionSettings() {
  const lang = detectLang()
  const t = settingsTranslations.subscription[lang]
  const { data: subscription, isLoading: subLoading } = useBillingSubscription()
  const { data: catalog, isLoading: plansLoading } = useBillingPlans()

  const isLoading = subLoading || plansLoading

  const PLANS = useMemo(() => {
    const formatPrice = (priceCents: number, currency: string) => {
      return new Intl.NumberFormat(lang === "fr" ? "fr-FR" : "en-US", {
        style: "currency",
        currency: currency,
        maximumFractionDigits: 0,
      }).format(priceCents / 100) + (lang === "fr" ? "/mois" : "/month")
    }

    const basicPlan = catalog?.find(p => p.code === "basic")
    const premiumPlan = catalog?.find(p => p.code === "premium")

    return [
      { 
        code: null, 
        label: t.planFree || "Gratuit", 
        limit: "5 msg/jour", 
        price: "0 €" 
      },
      { 
        code: "basic", 
        label: "Basic", 
        limit: "50 msg/jour", 
        price: basicPlan ? formatPrice(basicPlan.monthly_price_cents, basicPlan.currency) : "9 €/mois" 
      },
      { 
        code: "premium", 
        label: "Premium", 
        limit: "1000 msg/jour", 
        price: premiumPlan ? formatPrice(premiumPlan.monthly_price_cents, premiumPlan.currency) : "29 €/mois" 
      },
    ]
  }, [catalog, lang, t])

  const currentPlanCode = subscription?.plan?.code ?? null
  const stripeSubscriptionStatus = subscription?.subscription_status ?? null

  const [selectedPlanCode, setSelectedPlanCode] = useState<string | null | undefined>(undefined)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!isLoading && selectedPlanCode === undefined) {
      setSelectedPlanCode(currentPlanCode)
    }
  }, [isLoading, currentPlanCode, selectedPlanCode])

  const displaySelected = selectedPlanCode === undefined ? currentPlanCode : selectedPlanCode

  const checkoutSession = useStripeCheckoutSession()
  const portalSession = useStripePortalSession()
  const portalUpdateSession = useStripePortalSubscriptionUpdateSession()

  const handleValidate = () => {
    if (selectedPlanCode === currentPlanCode) return
    if (!selectedPlanCode) return

    setErrorMessage(null)

    const onError = (err: unknown) => {
      if (err instanceof BillingApiError) {
        if (err.code === "stripe_billing_profile_not_found") {
          setErrorMessage("Aucun profil de paiement Stripe trouvé. Veuillez contacter le support.")
        } else if (err.code === "stripe_subscription_not_found") {
          setErrorMessage("Abonnement Stripe introuvable. Veuillez réessayer depuis la page de souscription.")
        } else {
          setErrorMessage(err.message || "Erreur lors de l'opération")
        }
      } else {
        setErrorMessage("Erreur lors de l'opération")
      }
    }

    if (stripeSubscriptionStatus === null) {
      if (checkoutSession.isPending) return
      // Use direct canonical code
      const planToSub = selectedPlanCode as "basic" | "premium"
      checkoutSession.mutate(planToSub, {
        onSuccess: (data) => {
          window.location.href = data.checkout_url
        },
        onError,
      })
    } else if (stripeSubscriptionStatus === "active") {
      if (portalUpdateSession.isPending) return
      portalUpdateSession.mutate(undefined, {
        onSuccess: (data) => {
          window.location.href = data.url
        },
        onError: (err) => {
          if (err instanceof BillingApiError && err.code === "stripe_subscription_not_found") {
            portalSession.mutate(undefined, {
              onSuccess: (portalData) => {
                window.location.href = portalData.url
              },
              onError,
            })
          } else {
            onError(err)
          }
        },
      })
    } else {
      if (portalSession.isPending) return
      portalSession.mutate(undefined, {
        onSuccess: (data) => {
          window.location.href = data.url
        },
        onError,
      })
    }
  }

  const isAnyPending = checkoutSession.isPending || portalSession.isPending || portalUpdateSession.isPending
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
            <h3 className="settings-section-title settings-section-title--usage">
              {t.availablePlans}
            </h3>
            <div className="subscription-plans-grid">
              {PLANS.map((plan) => {
                const isCurrent = currentPlanCode === plan.code
                const isSelected = displaySelected === plan.code
                return (
                  <div
                    key={plan.code || "free"}
                    className={`subscription-plan-card ${isSelected ? 'subscription-plan-card--active' : ''}`}
                    onClick={() => setSelectedPlanCode(plan.code)}
                    role="button"
                    tabIndex={isAnyPending ? -1 : 0}
                    aria-pressed={isSelected}
                    onKeyDown={(event) => {
                      if (isAnyPending) return
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault()
                        setSelectedPlanCode(plan.code)
                      }
                    }}
                    data-current-unselected={isCurrent && !isSelected}
                    data-pending={isAnyPending}
                  >
                    {isCurrent && !isSelected && (
                      <div className="subscription-plan-card__badge subscription-plan-card__badge--muted">
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

            {errorMessage && (
              <p className="settings-save-feedback settings-save-feedback--error">{errorMessage}</p>
            )}

            <div className="subscription-actions">
              {hasChanges && displaySelected === null && (
                <span className="settings-text-muted">{t.cancelSoon}</span>
              )}
              <button
                type="button"
                className="settings-tab settings-tab--active subscription-actions__button"
                onClick={handleValidate}
                disabled={!hasChanges || displaySelected === null || isAnyPending}
              >
                {isAnyPending ? t.validating : t.validatePlan}
              </button>
            </div>

            <div className="subscription-credits-section">
              <div className="subscription-credits-section__content">
                <div className="default-astrologer-option__avatar--placeholder subscription-credits-section__icon">
                  <CreditCard size={24} />
                </div>
                <div>
                  <h3 className="subscription-credits-section__title">{t.buyCredits}</h3>
                  <p className="subscription-credits-section__desc">{t.buyCreditsDesc}</p>
                  <button
                    type="button"
                    className="settings-tab subscription-credits-section__button"
                    disabled
                    title={t.soon}
                  >
                    {t.buyCredits} - {t.soon}
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

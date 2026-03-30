import { useState, useEffect } from "react"
import {
  useBillingSubscription,
  useStripeCheckoutSession,
  useStripePortalSession,
  useStripePortalSubscriptionUpdateSession,
  toStripePlanCode,
  fromStripePlanCode,
  BillingApiError,
} from "@api/billing"
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

  // Fix HIGH-1 : l'API renvoie les codes canoniques Stripe ("basic", "premium").
  // On les normalise vers les codes UI legacy pour les comparaisons et l'affichage.
  const currentUIPlanCode = fromStripePlanCode(subscription?.plan?.code)

  // Fix HIGH-2 : utiliser subscription_status (champ Stripe brut) plutôt que
  // status (simplifié "inactive" même pour past_due) pour le routage checkout vs portal.
  const stripeSubscriptionStatus = subscription?.subscription_status ?? null

  const [selectedPlanCode, setSelectedPlanCode] = useState<string | null | undefined>(undefined)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!isLoading && selectedPlanCode === undefined) {
      setSelectedPlanCode(currentUIPlanCode)
    }
  }, [isLoading, currentUIPlanCode, selectedPlanCode])

  const displaySelected = selectedPlanCode === undefined ? currentUIPlanCode : selectedPlanCode

  const checkoutSession = useStripeCheckoutSession()
  const portalSession = useStripePortalSession()
  const portalUpdateSession = useStripePortalSubscriptionUpdateSession()

  const handleValidate = () => {
    if (selectedPlanCode === currentUIPlanCode) return
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

    // Fix HIGH-2 : routage basé sur subscription_status (champ Stripe brut).
    // - Pas de subscription Stripe (null) → Checkout Session (nouvel abonné)
    // - "active" → Portal Subscription Update Session (changement de plan)
    // - "past_due", "trialing", autre → Customer Portal générique (régulariser le paiement)
    if (stripeSubscriptionStatus === null) {
      // Pas de subscription Stripe existante
      if (checkoutSession.isPending) return
      checkoutSession.mutate(toStripePlanCode(selectedPlanCode), {
        onSuccess: (data) => {
          window.location.href = data.checkout_url
        },
        onError,
      })
    } else if (stripeSubscriptionStatus === "active") {
      // Abonnement actif → changement de plan via portal update
      if (portalUpdateSession.isPending) return
      portalUpdateSession.mutate(undefined, {
        onSuccess: (data) => {
          window.location.href = data.url
        },
        onError: (err) => {
          if (err instanceof BillingApiError && err.code === "stripe_subscription_not_found") {
            // Fallback vers le portal générique
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
      // past_due, trialing, etc. → portal générique pour régulariser
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
  // Fix HIGH-1 : comparer displaySelected contre les codes UI (pas les codes canoniques Stripe)
  const hasChanges = displaySelected !== currentUIPlanCode

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
                // Fix HIGH-1 : comparaison entre codes UI uniquement
                const isCurrent = currentUIPlanCode === plan.code
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

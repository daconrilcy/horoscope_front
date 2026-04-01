import { useState, useEffect, useMemo, useRef } from "react"
import {
  useBillingSubscription,
  useBillingPlans,
  useStripeCheckoutSession,
  useStripePortalSession,
  useStripePortalSubscriptionCancelSession,
  useStripePortalSubscriptionUpdateSession,
  useStripeSubscriptionReactivate,
  useStripeSubscriptionUpgrade,
  BillingApiError,
} from "@api/billing"
import { detectLang } from "@i18n/astrology"
import { settingsTranslations } from "@i18n/settings"
import { Check, CreditCard } from "lucide-react"
import "./Settings.css"

const BILLING_PORTAL_PENDING_ACTION_KEY = "billing_portal_pending_action"
const BILLING_PORTAL_SYNC_WINDOW_MS = 60_000
const BILLING_PORTAL_POLL_INTERVAL_MS = 3_000

type PendingBillingPortalAction = {
  action: "cancel"
  createdAt: number
  currentPeriodEnd?: string | null
}

function readPendingBillingPortalAction(): PendingBillingPortalAction | null {
  if (typeof window === "undefined") return null
  const raw = window.localStorage.getItem(BILLING_PORTAL_PENDING_ACTION_KEY)
  if (!raw) return null

  try {
    const parsed = JSON.parse(raw) as PendingBillingPortalAction
    if (parsed.action !== "cancel" || typeof parsed.createdAt !== "number") {
      return null
    }
    return parsed
  } catch {
    return null
  }
}

function persistPendingBillingPortalAction(
  action: PendingBillingPortalAction["action"],
  metadata: { currentPeriodEnd?: string | null } = {},
) {
  if (typeof window === "undefined") return
  window.localStorage.setItem(
    BILLING_PORTAL_PENDING_ACTION_KEY,
    JSON.stringify({ action, createdAt: Date.now(), ...metadata }),
  )
}

function clearPendingBillingPortalAction() {
  if (typeof window === "undefined") return
  window.localStorage.removeItem(BILLING_PORTAL_PENDING_ACTION_KEY)
}

export function SubscriptionSettings() {
  const lang = detectLang()
  const t = settingsTranslations.subscription[lang]
  const {
    data: subscription,
    isLoading: subLoading,
    refetch: refetchSubscription,
  } = useBillingSubscription()
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

    const formatLimit = (planCode: string | null) => {
      const isCurrent = (subscription?.plan?.code ?? null) === planCode
      const quota = subscription?.current_quota

      if (isCurrent && quota) {
        return `${quota.quota_limit} ${t.quotaUnit}/${t.periodUnit[quota.period_unit] || quota.period_unit}`
      }

      return `— ${t.quotaUnit}`
    }

    const basicPlan = catalog?.find(p => p.code === "basic")
    const premiumPlan = catalog?.find(p => p.code === "premium")

    return [
      {
        code: null,
        label: t.planFree || "Gratuit",
        limit: formatLimit(null),
        price: "0 €"
      },
      {
        code: "basic",
        label: "Basic",
        limit: formatLimit("basic"),
        price: basicPlan ? formatPrice(basicPlan.monthly_price_cents, basicPlan.currency) : "9 €/mois"
      },
      {
        code: "premium",
        label: "Premium",
        limit: formatLimit("premium"),
        price: premiumPlan ? formatPrice(premiumPlan.monthly_price_cents, premiumPlan.currency) : "29 €/mois"
      },
    ]
  }, [catalog, lang, t, subscription])

  const currentPlanCode = subscription?.plan?.code ?? null
  const stripeSubscriptionStatus = subscription?.subscription_status ?? null
  const isTrialingBasic = stripeSubscriptionStatus === "trialing" && currentPlanCode === "basic"
  const [pendingPortalAction, setPendingPortalAction] = useState<PendingBillingPortalAction | null>(
    () => readPendingBillingPortalAction(),
  )
  const optimisticCurrentPeriodEnd = pendingPortalAction?.currentPeriodEnd ?? null
  const isCancellationAlreadyScheduled =
    subscription?.cancel_at_period_end === true || pendingPortalAction?.action === "cancel"
  const effectiveCurrentPeriodEnd = subscription?.current_period_end ?? optimisticCurrentPeriodEnd
  const committedPlanCode = isCancellationAlreadyScheduled ? null : currentPlanCode

  const [selectedPlanCode, setSelectedPlanCode] = useState<string | null | undefined>(undefined)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [isPortalSyncPending, setIsPortalSyncPending] = useState(() => readPendingBillingPortalAction() !== null)
  const [upgradeSyncTargetPlanCode, setUpgradeSyncTargetPlanCode] = useState<string | null>(null)
  const previousCommittedPlanCodeRef = useRef<string | null | undefined>(undefined)

  useEffect(() => {
    if (!isLoading && selectedPlanCode === undefined) {
      setSelectedPlanCode(committedPlanCode)
    }
  }, [committedPlanCode, isLoading, selectedPlanCode])

  useEffect(() => {
    if (isLoading) return

    const previousCommittedPlanCode = previousCommittedPlanCodeRef.current
    if (
      previousCommittedPlanCode !== undefined
      && previousCommittedPlanCode !== committedPlanCode
      && selectedPlanCode === previousCommittedPlanCode
    ) {
      setSelectedPlanCode(committedPlanCode)
    }

    previousCommittedPlanCodeRef.current = committedPlanCode
  }, [committedPlanCode, isLoading, selectedPlanCode])

  useEffect(() => {
    const pendingAction = readPendingBillingPortalAction()
    setPendingPortalAction(pendingAction)
    if (!pendingAction) {
      setIsPortalSyncPending(false)
      return
    }

    const expiresAt = pendingAction.createdAt + BILLING_PORTAL_SYNC_WINDOW_MS
    if (Date.now() >= expiresAt) {
      clearPendingBillingPortalAction()
      setPendingPortalAction(null)
      setIsPortalSyncPending(false)
      return
    }

    if (pendingAction.action === "cancel" && subscription?.cancel_at_period_end) {
      clearPendingBillingPortalAction()
      setPendingPortalAction(null)
      setIsPortalSyncPending(false)
      return
    }

    setIsPortalSyncPending(true)
    void refetchSubscription()

    const intervalId = window.setInterval(() => {
      void refetchSubscription()
    }, BILLING_PORTAL_POLL_INTERVAL_MS)

    const timeoutId = window.setTimeout(() => {
      clearPendingBillingPortalAction()
      setPendingPortalAction(null)
      setIsPortalSyncPending(false)
      window.clearInterval(intervalId)
    }, Math.max(0, expiresAt - Date.now()))

    return () => {
      window.clearInterval(intervalId)
      window.clearTimeout(timeoutId)
    }
  }, [refetchSubscription, subscription?.cancel_at_period_end])

  useEffect(() => {
    if (!upgradeSyncTargetPlanCode) return

    const targetPlanLabel =
      PLANS.find((plan) => plan.code === upgradeSyncTargetPlanCode)?.label ?? upgradeSyncTargetPlanCode

    if (currentPlanCode === upgradeSyncTargetPlanCode && stripeSubscriptionStatus === "active") {
      setSuccessMessage(
        t.upgradeApplied.replace("{{plan}}", targetPlanLabel),
      )
      setUpgradeSyncTargetPlanCode(null)
      return
    }

    setSuccessMessage(
      t.upgradeSyncPending.replace("{{plan}}", targetPlanLabel),
    )
    void refetchSubscription()

    const intervalId = window.setInterval(() => {
      void refetchSubscription()
    }, BILLING_PORTAL_POLL_INTERVAL_MS)

    const timeoutId = window.setTimeout(() => {
      setUpgradeSyncTargetPlanCode(null)
    }, BILLING_PORTAL_SYNC_WINDOW_MS)

    return () => {
      window.clearInterval(intervalId)
      window.clearTimeout(timeoutId)
    }
  }, [PLANS, currentPlanCode, refetchSubscription, stripeSubscriptionStatus, t, upgradeSyncTargetPlanCode])

  const displaySelected = selectedPlanCode === undefined ? committedPlanCode : selectedPlanCode
  const isTrialUpgradeBlocked = isTrialingBasic && displaySelected === "premium"

  const checkoutSession = useStripeCheckoutSession()
  const portalSession = useStripePortalSession()
  const portalCancelSession = useStripePortalSubscriptionCancelSession()
  const portalUpdateSession = useStripePortalSubscriptionUpdateSession()
  const reactivateSubscription = useStripeSubscriptionReactivate()
  const upgradeSubscription = useStripeSubscriptionUpgrade()

  const getPlanPriceCents = (planCode: string | null) => {
    if (planCode === null) return 0
    const plan = catalog?.find((entry) => entry.code === planCode)
    return plan?.monthly_price_cents ?? 0
  }

  const currentPlanPriceCents = getPlanPriceCents(currentPlanCode)
  const selectedPlanPriceCents = getPlanPriceCents(displaySelected)
  const isUpgradeSyncPending = upgradeSyncTargetPlanCode !== null
  const isImmediatePaidUpgrade =
    stripeSubscriptionStatus === "active"
    && !isCancellationAlreadyScheduled
    && displaySelected !== null
    && currentPlanCode !== null
    && selectedPlanPriceCents > currentPlanPriceCents

  const handleValidate = () => {
    if (displaySelected === committedPlanCode) return
    
    // Bloquer uniquement si pas de subscription active (interdit d'être "null" sans payer)
    // Mais si subscription active, "null" veut dire résilier -> on laisse passer
    if (!displaySelected && stripeSubscriptionStatus === null) return

    if (isTrialUpgradeBlocked) {
      setSuccessMessage(null)
      setErrorMessage(t.trialBasicNotice)
      return
    }

    if (displaySelected === null && isCancellationAlreadyScheduled) {
      setSuccessMessage(null)
      setErrorMessage(t.cancelAlreadyScheduled)
      return
    }

    setErrorMessage(null)
    setSuccessMessage(null)

    const onError = (err: unknown) => {
      if (err instanceof BillingApiError) {
        if (err.code === "stripe_billing_profile_not_found") {
          setErrorMessage("Aucun profil de paiement Stripe trouvé. Veuillez contacter le support.")
        } else if (err.code === "stripe_subscription_not_found") {
          setErrorMessage("Abonnement Stripe introuvable. Veuillez réessayer depuis la page de souscription.")
        } else if (err.code === "stripe_portal_subscription_update_not_allowed_for_trial") {
          setErrorMessage(t.trialBasicNotice)
        } else if (err.code === "stripe_portal_subscription_update_no_change_options") {
          setErrorMessage(
            "La configuration Stripe ne permet pas encore de changer vers cet abonnement. Ajoutez les prix Basic et Premium dans la configuration du Customer Portal."
          )
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
      const planToSub = displaySelected as "basic" | "premium"
      checkoutSession.mutate(planToSub, {
        onSuccess: (data) => {
          window.location.href = data.checkout_url
        },
        onError,
      })
    } else if (stripeSubscriptionStatus === "active") {
      // Si on a sélectionné le plan Gratuit (null) -> flow portal cancel
      if (displaySelected === null) {
        if (portalCancelSession.isPending) return
        portalCancelSession.mutate(undefined, {
          onSuccess: (data) => {
            const nextPendingAction: PendingBillingPortalAction = {
              action: "cancel",
              createdAt: Date.now(),
              currentPeriodEnd: subscription?.current_period_end ?? null,
            }
            persistPendingBillingPortalAction("cancel", {
              currentPeriodEnd: nextPendingAction.currentPeriodEnd,
            })
            setPendingPortalAction(nextPendingAction)
            window.location.href = data.url
          },
          onError,
        })
        return
      }

      if (isCancellationAlreadyScheduled && displaySelected === currentPlanCode) {
        if (reactivateSubscription.isPending) return
        reactivateSubscription.mutate(undefined, {
          onSuccess: () => {
            clearPendingBillingPortalAction()
            setPendingPortalAction(null)
            setIsPortalSyncPending(false)
            void refetchSubscription()
          },
          onError,
        })
        return
      }

      if (isImmediatePaidUpgrade) {
        if (upgradeSubscription.isPending) return
        upgradeSubscription.mutate(displaySelected as "basic" | "premium", {
          onSuccess: (data) => {
            if (data.checkout_url) {
              window.location.href = data.checkout_url
              return
            }
            setUpgradeSyncTargetPlanCode(displaySelected)
            void refetchSubscription()
          },
          onError,
        })
        return
      }

      // Sinon flow portal update pour changement de plan payant
      if (portalUpdateSession.isPending) return
      portalUpdateSession.mutate(undefined, {
        onSuccess: (data) => {
          window.location.href = data.url
        },
        onError: (err) => {
          if (
            err instanceof BillingApiError
            && (
              err.code === "stripe_subscription_not_found"
              || err.code === "stripe_portal_subscription_update_disabled"
            )
          ) {
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

  const isAnyPending =
    checkoutSession.isPending
    || portalSession.isPending
    || portalCancelSession.isPending
    || portalUpdateSession.isPending
    || reactivateSubscription.isPending
    || upgradeSubscription.isPending
  const isUiLocked = isAnyPending || isUpgradeSyncPending
  const hasChanges = displaySelected !== committedPlanCode
  const isCancelActionBlocked = displaySelected === null && isCancellationAlreadyScheduled

  const scheduledMsg = useMemo(() => {
    if (!subscription) return null
    const formatDate = (dateStr: string) => {
      const d = new Date(dateStr)
      return d.toLocaleDateString(lang === "fr" ? "fr-FR" : "en-US", {
        day: "numeric",
        month: "long",
        year: "numeric",
      })
    }

    if (isCancellationAlreadyScheduled && effectiveCurrentPeriodEnd) {
      return t.cancelScheduled.replace("{{date}}", formatDate(effectiveCurrentPeriodEnd))
    }
    if (subscription.scheduled_plan && subscription.change_effective_at) {
      return t.planChangeScheduled
        .replace("{{plan}}", subscription.scheduled_plan.display_name)
        .replace("{{date}}", formatDate(subscription.change_effective_at))
    }
    return null
  }, [effectiveCurrentPeriodEnd, isCancellationAlreadyScheduled, subscription, t, lang])

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
                const isFrozen = isCancellationAlreadyScheduled && plan.code === null
                const showCurrentCancellationNotice =
                  isCancellationAlreadyScheduled
                  && isCurrent
                  && plan.code !== null
                  && scheduledMsg !== null
                const reactivateLabel =
                  isCancellationAlreadyScheduled && plan.code
                    ? plan.code === "basic"
                      ? t.reactivateWithBasic
                      : t.reactivateWithPremium
                    : null
                return (
                  <div
                    key={plan.code || "free"}
                    className={`subscription-plan-card ${isSelected ? 'subscription-plan-card--active' : ''} ${isFrozen ? 'subscription-plan-card--frozen' : ''}`}
                    onClick={() => {
                      if (isUiLocked || isFrozen) return
                      setSelectedPlanCode(plan.code)
                    }}
                    role="button"
                    tabIndex={isUiLocked || isFrozen ? -1 : 0}
                    aria-pressed={isSelected}
                    aria-disabled={isUiLocked || isFrozen}
                    onKeyDown={(event) => {
                      if (isUiLocked || isFrozen) return
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault()
                        setSelectedPlanCode(plan.code)
                      }
                    }}
                    data-current-unselected={isCurrent && !isSelected}
                    data-pending={isUiLocked}
                    data-frozen={isFrozen}
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
                    {showCurrentCancellationNotice && (
                      <div className="subscription-plan-card__status-note">
                        {scheduledMsg}
                      </div>
                    )}
                    {reactivateLabel && (
                      <div className="subscription-plan-card__action-hint">{reactivateLabel}</div>
                    )}
                  </div>
                )
              })}
            </div>

            {errorMessage && (
              <p className="settings-save-feedback settings-save-feedback--error">{errorMessage}</p>
            )}
            {!errorMessage && successMessage && (
              <p className="settings-save-feedback settings-save-feedback--success">{successMessage}</p>
            )}
            {!errorMessage && isTrialingBasic && (
              <p className="settings-save-feedback settings-save-feedback--saving">
                {t.trialBasicNotice}
              </p>
            )}

            <div className="subscription-actions">
              {scheduledMsg && (
                <span className="subscription-actions__scheduled-msg">{scheduledMsg}</span>
              )}
              {!scheduledMsg && isPortalSyncPending && (
                <span className="settings-text-muted">{t.portalSyncPending}</span>
              )}
              {!scheduledMsg && hasChanges && displaySelected === null && (
                <span className="settings-text-muted">{t.cancelSoon}</span>
              )}
              <button
                type="button"
                className="settings-tab settings-tab--active subscription-actions__button"
                onClick={handleValidate}
                disabled={!hasChanges || isUiLocked || isTrialUpgradeBlocked || isCancelActionBlocked}
              >
                {isAnyPending ? t.validating : isCancellationAlreadyScheduled ? t.reactivateSubscription : t.validatePlan}
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

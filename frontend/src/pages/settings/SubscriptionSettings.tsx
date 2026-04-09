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
import { supportTranslations } from "@i18n/support"
import { Modal } from "@components/ui"
import { ArrowRight, CalendarClock, Check, CreditCard, RefreshCcw, Sparkles } from "lucide-react"
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
  const subscriptionGuide = supportTranslations[lang].subscriptions
  const {
    data: subscription,
    isLoading: subLoading,
    refetch: refetchSubscription,
  } = useBillingSubscription()
  const { data: catalog, isLoading: plansLoading } = useBillingPlans()
  const currentSubscriptionPlan = subscription?.plan ?? subscription?.active_plan ?? null

  const isLoading = subLoading || plansLoading

  const PLANS = useMemo(() => {
    const locale = lang === "fr" ? "fr-FR" : lang === "es" ? "es-ES" : "en-US"
    const formatPrice = (priceCents: number, currency: string) => {
      return (
        new Intl.NumberFormat(locale, {
        style: "currency",
        currency: currency,
        maximumFractionDigits: 0,
      }).format(priceCents / 100)
        + ` ${subscriptionGuide.perMonth}`
      )
    }

    const basicPlan = catalog?.find(p => p.code === "basic")
    const premiumPlan = catalog?.find(p => p.code === "premium")

    return [
      {
        code: "basic",
        label: subscriptionGuide.plans.basic.name,
        tagline: subscriptionGuide.plans.basic.tagline,
        positioning: subscriptionGuide.plans.basic.positioning,
        lead: subscriptionGuide.plans.basic.description[0],
        highlights: subscriptionGuide.planHighlights.basic.slice(0, 4),
        priority: subscriptionGuide.priority.medium,
        price: basicPlan
          ? formatPrice(basicPlan.monthly_price_cents, basicPlan.currency)
          : `9 ${subscriptionGuide.perMonth}`,
      },
      {
        code: "premium",
        label: subscriptionGuide.plans.premium.name,
        tagline: subscriptionGuide.plans.premium.tagline,
        positioning: subscriptionGuide.plans.premium.positioning,
        lead: subscriptionGuide.plans.premium.description[0],
        highlights: subscriptionGuide.planHighlights.premium.slice(0, 4),
        priority: subscriptionGuide.priority.high,
        price: premiumPlan
          ? formatPrice(premiumPlan.monthly_price_cents, premiumPlan.currency)
          : `29 ${subscriptionGuide.perMonth}`,
      },
    ]
  }, [catalog, lang, subscriptionGuide])

  const currentPlanCode = currentSubscriptionPlan?.code ?? null
  const stripeSubscriptionStatus = subscription?.subscription_status ?? null
  const isTrialingBasic = stripeSubscriptionStatus === "trialing" && currentPlanCode === "basic"
  const [pendingPortalAction, setPendingPortalAction] = useState<PendingBillingPortalAction | null>(
    () => readPendingBillingPortalAction(),
  )
  const optimisticCurrentPeriodEnd = pendingPortalAction?.currentPeriodEnd ?? null
  const isCancellationAlreadyScheduled =
    subscription?.cancel_at_period_end === true || pendingPortalAction?.action === "cancel"
  const effectiveCurrentPeriodEnd = subscription?.current_period_end ?? optimisticCurrentPeriodEnd
  const committedPlanCode = currentPlanCode

  const [selectedPlanCode, setSelectedPlanCode] = useState<string | null | undefined>(undefined)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [isPortalSyncPending, setIsPortalSyncPending] = useState(() => readPendingBillingPortalAction() !== null)
  const [upgradeSyncTargetPlanCode, setUpgradeSyncTargetPlanCode] = useState<string | null>(null)
  const [isUpgradeInfoModalOpen, setIsUpgradeInfoModalOpen] = useState(false)
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
  const isFreeEntryPoint = currentPlanCode === null || currentPlanCode === "free"
  const hasActivePaidSubscription =
    stripeSubscriptionStatus === "active"
    && currentPlanCode !== null
    && currentPlanCode !== "free"
  const requiresNewCheckout = isFreeEntryPoint && !hasActivePaidSubscription
  const isFreeWithoutSubscription = isFreeEntryPoint && stripeSubscriptionStatus === null
  const isImmediatePaidUpgrade =
    stripeSubscriptionStatus === "active"
    && !isCancellationAlreadyScheduled
    && displaySelected !== null
    && currentPlanCode !== null
    && selectedPlanPriceCents > currentPlanPriceCents

  const formatDisplayDate = (dateStr: string) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString(lang === "fr" ? "fr-FR" : "en-US", {
      day: "numeric",
      month: "long",
      year: "numeric",
    })
  }

  const scrollToPlans = () => {
    document.getElementById("subscription-plans")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    })
  }

  const handleValidate = (skipUpgradeInfoModal = false) => {
    if (displaySelected === committedPlanCode) return
    if (!displaySelected) return

    if (isTrialUpgradeBlocked) {
      setSuccessMessage(null)
      setErrorMessage(t.trialBasicNotice)
      return
    }

    if (isImmediatePaidUpgrade && !skipUpgradeInfoModal) {
      setIsUpgradeInfoModalOpen(true)
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

    if (requiresNewCheckout) {
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

  const handleSubscriptionStatusAction = () => {
    setErrorMessage(null)
    setSuccessMessage(null)

    const onError = (err: unknown) => {
      if (err instanceof BillingApiError) {
        setErrorMessage(err.message || "Erreur lors de l'opération")
        return
      }
      setErrorMessage("Erreur lors de l'opération")
    }

    if (isCancellationAlreadyScheduled) {
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
  const selectedPlanLabel =
    PLANS.find((plan) => plan.code === displaySelected)?.label ?? displaySelected ?? ""
  const currentPlanLabel =
    PLANS.find((plan) => plan.code === currentPlanCode)?.label
    ?? (currentPlanCode === "free" ? t.planFree : currentPlanCode ?? "")
  const currentPlanExperience = isFreeEntryPoint
    ? subscriptionGuide.plans.free.positioning
    : PLANS.find((plan) => plan.code === currentPlanCode)?.positioning
  const currentPlanHighlights = isFreeEntryPoint
    ? subscriptionGuide.planHighlights.free.slice(0, 3)
    : PLANS.find((plan) => plan.code === currentPlanCode)?.highlights ?? []
  const currentPlanLead = isFreeEntryPoint
    ? subscriptionGuide.plans.free.description[0]
    : PLANS.find((plan) => plan.code === currentPlanCode)?.lead ?? t.overviewLeadActive
  const currentPlanStatusMessage = useMemo(() => {
    if (!effectiveCurrentPeriodEnd || isFreeEntryPoint) return null
    if (isCancellationAlreadyScheduled || subscription?.scheduled_plan) {
      return t.currentPlanEndsOn.replace("{{date}}", formatDisplayDate(effectiveCurrentPeriodEnd))
    }
    return null
  }, [
    effectiveCurrentPeriodEnd,
    formatDisplayDate,
    isFreeEntryPoint,
    isCancellationAlreadyScheduled,
    subscription?.scheduled_plan,
    t.currentPlanEndsOn,
  ])
  const overviewPlanLabel = currentPlanLabel || t.planFree
  const overviewBillingValue = effectiveCurrentPeriodEnd
    ? formatDisplayDate(effectiveCurrentPeriodEnd)
    : t.overviewNoBillingDate
  const overviewRenewalValue = isCancellationAlreadyScheduled
    ? t.overviewRenewalScheduled
    : hasActivePaidSubscription
      ? t.overviewRenewalAuto
      : t.overviewRenewalInactive
  const overviewLead = currentPlanLead
  const overviewActionMessage = useMemo(() => {
    if (subscription?.scheduled_plan?.display_name && subscription.change_effective_at) {
      return t.overviewActionScheduledChange
        .replace("{{plan}}", subscription.scheduled_plan.display_name)
        .replace("{{date}}", formatDisplayDate(subscription.change_effective_at))
    }

    if (isCancellationAlreadyScheduled && effectiveCurrentPeriodEnd) {
      return t.overviewActionCancellation.replace("{{date}}", formatDisplayDate(effectiveCurrentPeriodEnd))
    }

    if (hasChanges && selectedPlanLabel) {
      return t.overviewActionChangeTo.replace("{{plan}}", selectedPlanLabel)
    }

    if (isFreeEntryPoint) {
      return t.overviewActionFree
    }

    if (isTrialingBasic) {
      return t.trialBasicNotice
    }

    return t.overviewActionCurrent
  }, [
    effectiveCurrentPeriodEnd,
    formatDisplayDate,
    hasChanges,
    isFreeEntryPoint,
    isCancellationAlreadyScheduled,
    isTrialingBasic,
    selectedPlanLabel,
    subscription?.change_effective_at,
    subscription?.scheduled_plan?.display_name,
    t.overviewActionCancellation,
    t.overviewActionChangeTo,
    t.overviewActionCurrent,
    t.overviewActionFree,
    t.overviewActionScheduledChange,
    t.trialBasicNotice,
  ])

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
            <section className="subscription-overview">
              <div className="subscription-overview__header">
                <div className="subscription-overview__copy">
                  <span className="subscription-overview__eyebrow">{t.overviewEyebrow}</span>
                  <h3 className="subscription-overview__title" aria-label={overviewPlanLabel}>
                    {currentPlanExperience}
                  </h3>
                  <p className="subscription-overview__tagline">{currentPlanExperience}</p>
                  <p className="subscription-overview__lead">{overviewLead}</p>
                  <ul className="subscription-overview__highlights">
                    {currentPlanHighlights.map((highlight) => (
                      <li key={highlight} className="subscription-overview__highlight">
                        <Check size={14} />
                        <span>{highlight}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="subscription-overview__aside">
                  <span className="subscription-overview__aside-label">{t.overviewActionLabel}</span>
                  <p className="subscription-overview__aside-value">{overviewActionMessage}</p>
                  <button
                    type="button"
                    className="settings-tab subscription-overview__jump"
                    onClick={scrollToPlans}
                  >
                    {t.jumpToPlans}
                  </button>
                </div>
              </div>

              <div className="subscription-overview__stats">
                <div className="subscription-overview__stat">
                  <span className="subscription-overview__stat-label">{t.overviewPlanLabel}</span>
                  <strong className="subscription-overview__stat-value">{overviewPlanLabel}</strong>
                </div>
                <div className="subscription-overview__stat">
                  <span className="subscription-overview__stat-label">{t.overviewExperienceLabel}</span>
                  <strong className="subscription-overview__stat-value">{currentPlanExperience}</strong>
                </div>
                <div className="subscription-overview__stat">
                  <span className="subscription-overview__stat-label">{t.overviewBillingLabel}</span>
                  <strong className="subscription-overview__stat-value">{overviewBillingValue}</strong>
                </div>
                <div className="subscription-overview__stat">
                  <span className="subscription-overview__stat-label">{t.overviewRenewalLabel}</span>
                  <strong className="subscription-overview__stat-value">{overviewRenewalValue}</strong>
                </div>
              </div>
            </section>

            <section id="subscription-plans" className="subscription-plan-stage">
              <div className="subscription-plan-stage__header">
                <h3 className="settings-section-title settings-section-title--usage">
                  {t.availablePlans}
                </h3>
                <p className="subscription-plan-stage__lead">
                  {isFreeWithoutSubscription ? t.freePlanLimitedAccess : t.plansLead}
                </p>
              </div>

              <div className="subscription-plans-grid">
              {PLANS.map((plan) => {
                const isCurrent = currentPlanCode === plan.code
                const isSelected = displaySelected === plan.code
                const currentPlanNote = isCurrent ? currentPlanStatusMessage : null
                const scheduledPlanNote =
                  subscription?.scheduled_plan?.code === plan.code && subscription.change_effective_at
                    ? t.planChangeScheduled
                        .replace("{{plan}}", subscription.scheduled_plan.display_name)
                        .replace("{{date}}", formatDisplayDate(subscription.change_effective_at))
                    : null
                const reactivateLabel =
                  isCancellationAlreadyScheduled && plan.code
                    ? plan.code === "basic"
                      ? t.reactivateWithBasic
                      : t.reactivateWithPremium
                    : null
                const cardActionLabel = !isCurrent && isSelected
                    ? t.overviewActionChangeTo.replace("{{plan}}", plan.label)
                    : null
                return (
                  <button
                    key={plan.code || "free"}
                    type="button"
                    className={[
                      "subscription-plan-card",
                      isSelected ? "subscription-plan-card--active" : "",
                      `subscription-plan-card--${plan.code}`,
                    ].filter(Boolean).join(" ")}
                    onClick={() => {
                      if (isUiLocked) return
                      setSelectedPlanCode(plan.code)
                    }}
                    role="button"
                    tabIndex={isUiLocked ? -1 : 0}
                    aria-pressed={isSelected}
                    aria-disabled={isUiLocked}
                    onKeyDown={(event) => {
                      if (isUiLocked) return
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault()
                        setSelectedPlanCode(plan.code)
                      }
                    }}
                    data-current-unselected={isCurrent && !isSelected}
                    data-pending={isUiLocked}
                  >
                    <div className="subscription-plan-card__topline">
                      <div className="subscription-plan-card__copy">
                        <span className="subscription-plan-card__tagline">{plan.tagline}</span>
                        <h4 className="subscription-plan-card__name">
                          {plan.label}
                        </h4>
                      </div>
                      {isSelected && (
                        <div className="subscription-plan-card__badge">
                        <Check size={12} /> {isCurrent ? t.currentPlan : t.selected}
                        </div>
                      )}
                      {isCurrent && !isSelected && (
                        <div className="subscription-plan-card__badge subscription-plan-card__badge--muted">
                          {t.currentPlan}
                        </div>
                      )}
                    </div>
                    <div className="subscription-plan-card__priority">{plan.priority}</div>
                    <div className="subscription-plan-card__price">{plan.price}</div>
                    <p className="subscription-plan-card__lead">{plan.lead}</p>
                    <div className="subscription-plan-card__positioning">{plan.positioning}</div>
                    <ul className="subscription-plan-card__highlights">
                      {plan.highlights.map((highlight) => (
                        <li key={highlight} className="subscription-plan-card__highlight">
                          <Check size={14} />
                          <span>{highlight}</span>
                        </li>
                      ))}
                    </ul>
                    {cardActionLabel && (
                      <div className="subscription-plan-card__selection-note">
                        {cardActionLabel}
                      </div>
                    )}
                    {currentPlanNote && (
                      <div className="subscription-plan-card__status-note">
                        {currentPlanNote}
                      </div>
                    )}
                    {scheduledPlanNote && (
                      <div className="subscription-plan-card__status-note subscription-plan-card__status-note--scheduled">
                        {scheduledPlanNote}
                      </div>
                    )}
                    {reactivateLabel && (
                      <div className="subscription-plan-card__action-hint">{reactivateLabel}</div>
                    )}
                  </button>
                )
              })}
              </div>
            </section>

            <div className="subscription-feedback-stack" aria-live="polite">
              {errorMessage && (
                <p className="subscription-feedback-banner subscription-feedback-banner--error">
                  <Sparkles size={16} />
                  <span>{errorMessage}</span>
                </p>
              )}
              {!errorMessage && successMessage && (
                <p className="subscription-feedback-banner subscription-feedback-banner--success">
                  <Check size={16} />
                  <span>{successMessage}</span>
                </p>
              )}
              {!errorMessage && isTrialingBasic && (
                <p className="subscription-feedback-banner subscription-feedback-banner--info">
                  <CalendarClock size={16} />
                  <span>{t.trialBasicNotice}</span>
                </p>
              )}
            </div>

            <section className="subscription-actions-panel">
              <div className="subscription-actions-panel__copy">
                <span className="subscription-actions-panel__eyebrow">{t.overviewActionLabel}</span>
                <p className="subscription-actions-panel__summary">{overviewActionMessage}</p>
                {isPortalSyncPending && !currentPlanStatusMessage && (
                  <span className="subscription-actions-panel__meta">{t.portalSyncPending}</span>
                )}
              </div>
              <div className="subscription-actions-panel__buttons">
                <button
                  type="button"
                  className="settings-tab settings-tab--active subscription-actions__button"
                  onClick={() => handleValidate()}
                  disabled={!hasChanges || isUiLocked || isTrialUpgradeBlocked}
                >
                  {isAnyPending ? t.validating : t.validatePlan}
                  {!isAnyPending && <ArrowRight size={16} />}
                </button>

                {hasActivePaidSubscription && (
                  <button
                    type="button"
                    className="settings-tab subscription-management-button"
                    onClick={handleSubscriptionStatusAction}
                    disabled={isUiLocked}
                  >
                    {isCancellationAlreadyScheduled ? (
                      <>
                        <RefreshCcw size={16} />
                        {t.reactivateSubscription}
                      </>
                    ) : (
                      t.cancelSubscription
                    )}
                  </button>
                )}
              </div>
            </section>

            <div className="subscription-credits-section">
              <div className="subscription-credits-section__content">
                <div className="default-astrologer-option__avatar--placeholder subscription-credits-section__icon">
                  <CreditCard size={24} />
                </div>
                <div className="subscription-credits-section__body">
                  <div className="subscription-credits-section__badge">{t.soon}</div>
                  <h3 className="subscription-credits-section__title">{t.buyCredits}</h3>
                  <p className="subscription-credits-section__desc">{t.buyCreditsDesc}</p>
                  <p className="subscription-credits-section__hint">{t.buyCreditsHint}</p>
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

      <Modal
        isOpen={isUpgradeInfoModalOpen}
        onClose={() => setIsUpgradeInfoModalOpen(false)}
        title={t.upgradeModalTitle}
        size="sm"
        footer={
          <>
            <button
              type="button"
              className="settings-tab"
              onClick={() => setIsUpgradeInfoModalOpen(false)}
            >
              {t.upgradeModalCancel}
            </button>
            <button
              type="button"
              className="settings-tab settings-tab--active"
              onClick={() => {
                setIsUpgradeInfoModalOpen(false)
                handleValidate(true)
              }}
            >
              {t.upgradeModalProceed}
            </button>
          </>
        }
      >
        <div className="subscription-upgrade-modal">
          <p className="subscription-upgrade-modal__lead">
            {t.upgradeModalLead
              .replace("{{currentPlan}}", currentPlanLabel)
              .replace("{{targetPlan}}", selectedPlanLabel)}
          </p>
          <ul className="subscription-upgrade-modal__list">
            <li>{t.upgradeModalProration}</li>
            <li>{t.upgradeModalCredit}</li>
            <li>{t.upgradeModalRenewal.replace("{{targetPlan}}", selectedPlanLabel)}</li>
          </ul>
        </div>
      </Modal>
    </div>
  )
}

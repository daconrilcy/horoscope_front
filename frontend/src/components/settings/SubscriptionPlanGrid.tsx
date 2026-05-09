// Isole la grille des plans d'abonnement pour alleger la route preferences.
import { Check } from "lucide-react"

export type SubscriptionPlanOption = {
  code: string
  label: string
  tagline: string
  positioning: string
  lead: string
  highlights: string[]
  priority: string
  price: string
}

type SubscriptionPlanGridProps = {
  plans: SubscriptionPlanOption[]
  currentPlanCode: string | null
  displaySelected: string | null | undefined
  isUiLocked: boolean
  currentPlanStatusMessage: string | null
  scheduledPlan: { code?: string | null; display_name?: string | null } | null | undefined
  changeEffectiveAt: string | null | undefined
  isCancellationAlreadyScheduled: boolean
  labels: {
    currentPlan: string
    selected: string
    planChangeScheduled: string
    reactivateWithBasic: string
    reactivateWithPremium: string
    overviewActionChangeTo: string
  }
  formatDisplayDate: (date: string) => string
  onSelectPlan: (planCode: string) => void
}

type SubscriptionOverviewSectionProps = {
  labels: {
    eyebrow: string
    actionLabel: string
    jumpToPlans: string
    planLabel: string
    experienceLabel: string
    billingLabel: string
    renewalLabel: string
  }
  currentPlanExperience: string | undefined
  overviewLead: string
  currentPlanHighlights: string[]
  overviewActionMessage: string
  overviewPlanLabel: string
  overviewBillingValue: string
  overviewRenewalValue: string
  onJumpToPlans: () => void
}

/** Rend le recapitulatif d'abonnement sans posseder le scroll ni les donnees API. */
export function SubscriptionOverviewSection({
  labels,
  currentPlanExperience,
  overviewLead,
  currentPlanHighlights,
  overviewActionMessage,
  overviewPlanLabel,
  overviewBillingValue,
  overviewRenewalValue,
  onJumpToPlans,
}: SubscriptionOverviewSectionProps) {
  return (
    <section className="subscription-overview">
      <div className="subscription-overview__header">
        <div className="subscription-overview__copy">
          <span className="subscription-overview__eyebrow">{labels.eyebrow}</span>
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
          <span className="subscription-overview__aside-label">{labels.actionLabel}</span>
          <p className="subscription-overview__aside-value">{overviewActionMessage}</p>
          <button type="button" className="control-tab subscription-overview__jump" onClick={onJumpToPlans}>
            {labels.jumpToPlans}
          </button>
        </div>
      </div>

      <div className="subscription-overview__stats">
        <OverviewStat label={labels.planLabel} value={overviewPlanLabel} />
        <OverviewStat label={labels.experienceLabel} value={currentPlanExperience} />
        <OverviewStat label={labels.billingLabel} value={overviewBillingValue} />
        <OverviewStat label={labels.renewalLabel} value={overviewRenewalValue} />
      </div>
    </section>
  )
}

/** Rend les cartes de plans sans posseder la selection ni les mutations Stripe. */
export function SubscriptionPlanGrid({
  plans,
  currentPlanCode,
  displaySelected,
  isUiLocked,
  currentPlanStatusMessage,
  scheduledPlan,
  changeEffectiveAt,
  isCancellationAlreadyScheduled,
  labels,
  formatDisplayDate,
  onSelectPlan,
}: SubscriptionPlanGridProps) {
  return (
    <div className="subscription-plans-grid">
      {plans.map((plan) => {
        const isCurrent = currentPlanCode === plan.code
        const isSelected = displaySelected === plan.code
        const currentPlanNote = isCurrent ? currentPlanStatusMessage : null
        const scheduledPlanNote =
          scheduledPlan?.code === plan.code && changeEffectiveAt
            ? labels.planChangeScheduled
                .replace("{{plan}}", scheduledPlan.display_name ?? plan.label)
                .replace("{{date}}", formatDisplayDate(changeEffectiveAt))
            : null
        const reactivateLabel =
          isCancellationAlreadyScheduled && plan.code
            ? plan.code === "basic"
              ? labels.reactivateWithBasic
              : labels.reactivateWithPremium
            : null
        const cardActionLabel =
          !isCurrent && isSelected ? labels.overviewActionChangeTo.replace("{{plan}}", plan.label) : null

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
              onSelectPlan(plan.code)
            }}
            role="button"
            tabIndex={isUiLocked ? -1 : 0}
            aria-pressed={isSelected}
            aria-disabled={isUiLocked}
            onKeyDown={(event) => {
              if (isUiLocked) return
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault()
                onSelectPlan(plan.code)
              }
            }}
            data-current-unselected={isCurrent && !isSelected}
            data-pending={isUiLocked}
          >
            <div className="subscription-plan-card__topline">
              <div className="subscription-plan-card__copy">
                <span className="subscription-plan-card__tagline">{plan.tagline}</span>
                <h4 className="subscription-plan-card__name">{plan.label}</h4>
              </div>
              {isSelected && (
                <div className="subscription-plan-card__badge">
                  <Check size={12} /> {isCurrent ? labels.currentPlan : labels.selected}
                </div>
              )}
              {isCurrent && !isSelected && (
                <div className="subscription-plan-card__badge subscription-plan-card__badge--muted">
                  {labels.currentPlan}
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
            {cardActionLabel && <div className="subscription-plan-card__selection-note">{cardActionLabel}</div>}
            {currentPlanNote && <div className="subscription-plan-card__status-note">{currentPlanNote}</div>}
            {scheduledPlanNote && (
              <div className="subscription-plan-card__status-note subscription-plan-card__status-note--scheduled">
                {scheduledPlanNote}
              </div>
            )}
            {reactivateLabel && <div className="subscription-plan-card__action-hint">{reactivateLabel}</div>}
          </button>
        )
      })}
    </div>
  )
}

function OverviewStat({ label, value }: { label: string; value: string | undefined }) {
  return (
    <div className="subscription-overview__stat">
      <span className="subscription-overview__stat-label">{label}</span>
      <strong className="subscription-overview__stat-value">{value}</strong>
    </div>
  )
}

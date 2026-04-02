import { Link } from "react-router-dom"
import { Check, X } from "lucide-react"
import { PageLayout } from "@layouts/PageLayout"
import { useTranslation, useAstrologyLabels } from "@i18n"
import { useEntitlementsPlans, useBillingSubscription } from "@api/billing"
import { Button, SkeletonGroup, ErrorState, EmptyState } from "@ui"
import "./HelpPage.css"

export function SubscriptionGuidePage() {
  const { subscriptions: t } = useTranslation("support")
  const common = useTranslation("common")
  const { data: plans, isLoading, isError, refetch } = useEntitlementsPlans()
  const { data: subscription } = useBillingSubscription()
  const currentPlanCode = subscription?.plan?.code

  if (isLoading) {
    return (
      <PageLayout className="is-settings-page">
        <div className="help-bg-halo" />
        <div className="help-noise" />
        <div className="help-page">
          <SkeletonGroup count={3} className="help-subscriptions-grid" />
        </div>
      </PageLayout>
    )
  }

  if (isError) {
    return (
      <PageLayout className="is-settings-page">
        <div className="help-bg-halo" />
        <div className="help-noise" />
        <div className="help-page">
          <ErrorState message={common.states.error} onRetry={() => refetch()} />
        </div>
      </PageLayout>
    )
  }

  if (!plans || plans.length === 0) {
    return (
      <PageLayout className="is-settings-page">
        <div className="help-bg-halo" />
        <div className="help-noise" />
        <div className="help-page">
          <EmptyState title={common.states.empty} description={common.states.noData} />
        </div>
      </PageLayout>
    )
  }

  return (
    <PageLayout className="is-settings-page">
      <div className="help-bg-halo" />
      <div className="help-noise" />

      <div className="help-page">
        <section className="help-section help-subscriptions-hero">
          <h1>{t.hero.title}</h1>
          <p>{t.hero.subtitle}</p>
          <Link to="/settings/subscription">
            <Button variant="primary" className="help-subscriptions-hero-cta">
              {t.hero.cta}
            </Button>
          </Link>
        </section>

        <section className="help-section help-subscriptions-grid">
          {plans.map((plan) => (
            <PlanCard
              key={plan.plan_code}
              plan={plan}
              isCurrent={plan.plan_code === currentPlanCode}
              t={t}
            />
          ))}
        </section>

        <section className="help-section help-subscriptions-tokens">
          <div className="settings-card">
            <h2 className="help-subscriptions-plan-name">{t.tokensExplainer.title}</h2>
            <p>{t.tokensExplainer.body}</p>
          </div>
        </section>
      </div>
    </PageLayout>
  )
}

function PlanCard({ plan, isCurrent, t }: { plan: any; isCurrent: boolean; t: any }) {
  const { lang } = useAstrologyLabels()
  
  const priceFormatter = new Intl.NumberFormat(lang === "fr" ? "fr-FR" : "en-US", {
    style: "currency",
    currency: plan.currency,
    minimumFractionDigits: 0,
  })

  return (
    <div className={`subscription-plan-card ${isCurrent ? "subscription-plan-card--active" : ""}`}>
      {isCurrent && <div className="subscription-plan-card__badge">{t.currentPlan}</div>}

      <h2 className="help-subscriptions-plan-name">{t.plans[plan.plan_code]?.name || plan.plan_name}</h2>
      <p className="help-subscriptions-plan-tagline">{t.plans[plan.plan_code]?.tagline}</p>

      <div className="help-subscriptions-price">
        <span className="help-subscriptions-price-amount">
          {priceFormatter.format(plan.monthly_price_cents / 100)}
        </span>
        <span className="help-subscriptions-price-period">
          {lang === "fr" ? "/ mois" : "/ month"}
        </span>
      </div>

      <ul className="help-subscriptions-features-list">
        {plan.features.map((feature: any) => (
          <li key={feature.feature_code} className="help-subscriptions-feature-item">
            <div className="help-subscriptions-feature-icon">
              {feature.access_mode !== "disabled" ? (
                <Check className="help-subscriptions-feature-icon--check" size={18} />
              ) : (
                <X className="help-subscriptions-feature-icon--x" size={18} />
              )}
            </div>
            <div className="help-subscriptions-feature-details">
              <span className="help-subscriptions-feature-name">
                {t.features[feature.feature_code] || feature.feature_name}
              </span>
              {feature.access_mode === "quota" && feature.quotas.map((q: any, i: number) => (
                <span key={i} className="help-subscriptions-feature-quota">
                  {formatQuota(q, t)}
                </span>
              ))}
              {feature.access_mode === "unlimited" && (
                <span className="help-subscriptions-feature-quota">{t.quota.unlimited}</span>
              )}
              {feature.access_mode === "disabled" && (
                <span className="help-subscriptions-feature-quota">{t.quota.disabled}</span>
              )}
            </div>
          </li>
        ))}
      </ul>

      <Link to="/settings/subscription" className="help-subscriptions-cta">
        <Button variant={isCurrent ? "secondary" : "primary"} fullWidth>
          {isCurrent ? t.manageCta : t.upgradeCta}
        </Button>
      </Link>
    </div>
  )
}

function formatQuota(quota: any, t: any) {
  const amount = quota.quota_limit.toLocaleString()

  if (quota.quota_key === "tokens") {
    if (quota.period_unit === "day") return t.quota.tokens_per_day.replace("{{n}}", amount)
    if (quota.period_unit === "week") return t.quota.tokens_per_week.replace("{{n}}", amount)
    if (quota.period_unit === "month") return t.quota.tokens_per_month.replace("{{n}}", amount)
  }

  if (quota.period_unit === "lifetime") {
    return t.quota.interpretations_lifetime.replace("{{n}}", String(quota.quota_limit))
  }

  return amount
}

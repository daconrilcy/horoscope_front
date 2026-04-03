import { Link } from "react-router-dom"
import { Check, X } from "lucide-react"
import { PageLayout } from "@layouts/PageLayout"
import { useTranslation, useAstrologyLabels } from "@i18n"
import {
  type PlanCatalog,
  type PlanFeature,
  type PlanFeatureQuota,
  useEntitlementsPlans,
  useEntitlementsSnapshot,
  useBillingSubscription,
} from "@api/billing"
import { Button, SkeletonGroup, ErrorState, EmptyState } from "@ui"
import "./HelpPage.css"

type SupportSubscriptionsTranslation = ReturnType<typeof useTranslation<"support">>["subscriptions"]

const LOCALE_BY_LANG = {
  fr: "fr-FR",
  en: "en-US",
  es: "es-ES",
} as const

export function SubscriptionGuidePage() {
  const { subscriptions: t } = useTranslation("support")
  const common = useTranslation("common")
  const { data: plans, isLoading, isError, refetch } = useEntitlementsPlans()
  const { data: entitlements } = useEntitlementsSnapshot()
  const { data: subscription } = useBillingSubscription()
  const currentPlanCode = entitlements?.plan_code === "none"
    ? subscription?.plan?.code
    : entitlements?.plan_code ?? subscription?.plan?.code

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

function PlanCard({
  plan,
  isCurrent,
  t,
}: {
  plan: PlanCatalog
  isCurrent: boolean
  t: SupportSubscriptionsTranslation
}) {
  const { lang } = useAstrologyLabels()
  const locale = LOCALE_BY_LANG[lang]
  const planHighlights: string[] = t.planHighlights[plan.plan_code] ?? []
  const priceFormatter = new Intl.NumberFormat(locale, {
    style: "currency",
    currency: plan.currency,
    minimumFractionDigits: 0,
  })

  return (
    <div className={`subscription-plan-card ${isCurrent ? "subscription-plan-card--active" : ""}`}>
      <div className="help-subscriptions-plan-header">
        <h2 className="help-subscriptions-plan-name">{t.plans[plan.plan_code]?.name || plan.plan_name}</h2>
        {plan.processing_priority && (
          <span className={`help-subscriptions-priority-badge help-subscriptions-priority-badge--${plan.processing_priority}`}>
            {t.priority[plan.processing_priority]}
          </span>
        )}
      </div>
      <p className="help-subscriptions-plan-tagline">{t.plans[plan.plan_code]?.tagline}</p>

      <div className="help-subscriptions-price">
        <span className="help-subscriptions-price-amount">
          {priceFormatter.format(plan.monthly_price_cents / 100)}
        </span>
        <span className="help-subscriptions-price-period">
          {t.perMonth}
        </span>
      </div>

      <ul className="help-subscriptions-features-list">
        {planHighlights.map((highlight) => (
          <li
            key={`${plan.plan_code}-${highlight}`}
            className="help-subscriptions-feature-item help-subscriptions-feature-item--highlight"
          >
            <div className="help-subscriptions-feature-icon">
              <Check className="help-subscriptions-feature-icon--check" size={18} />
            </div>
            <div className="help-subscriptions-feature-details">
              <span className="help-subscriptions-feature-name">{highlight}</span>
            </div>
          </li>
        ))}
        {plan.features.map((feature: PlanFeature) => {
          // AC7: Ne pas exposer les tokens bruts pour basic et premium
          const isTokenFeature = feature.quotas.some(q => q.quota_key === "tokens");
          const shouldHideQuotas = isTokenFeature && (plan.plan_code === "basic" || plan.plan_code === "premium");

          return (
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
                {!shouldHideQuotas && feature.access_mode === "quota" && feature.quotas.map((q: PlanFeatureQuota) => (
                  <span
                    key={`${feature.feature_code}-${q.quota_key}-${q.period_unit}-${q.period_value}`}
                    className="help-subscriptions-feature-quota"
                  >
                    {formatQuota(q, t, locale)}
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
          );
        })}
      </ul>

      {isCurrent ? (
        <p className="help-subscriptions-current-plan">{t.currentPlan}</p>
      ) : (
        <Button
          as={Link}
          to="/settings/subscription"
          variant="primary"
          fullWidth
          className="help-subscriptions-cta"
        >
          {t.upgradeCta}
        </Button>
      )}
    </div>
  )
}

function formatQuota(
  quota: PlanFeatureQuota,
  t: SupportSubscriptionsTranslation,
  locale: string,
) {
  const amount = quota.quota_limit.toLocaleString(locale)

  if (quota.quota_key === "messages" && quota.period_unit === "week") {
    return t.quota.messages_per_week
  }

  if (quota.quota_key === "tokens") {
    if (quota.period_unit === "day") return t.quota.tokens_per_day.replace("{{n}}", amount)
    if (quota.period_unit === "week") return t.quota.tokens_per_week.replace("{{n}}", amount)
    if (quota.period_unit === "month") return t.quota.tokens_per_month.replace("{{n}}", amount)
  }

  if (quota.quota_key === "consultations" && quota.period_unit === "week") {
    return t.quota.consultations_per_week.replace("{{n}}", amount)
  }

  if (quota.period_unit === "lifetime") {
    return t.quota.interpretations_lifetime.replace("{{n}}", String(quota.quota_limit))
  }

  return amount
}

import { Link } from "react-router-dom"
import { Check, RefreshCcw, Sparkles, Telescope, X } from "lucide-react"
import { PageLayout } from "@layouts/PageLayout"
import { useTranslation, useAstrologyLabels } from "@i18n"
import {
  type PlanCatalog,
  type PlanFeature,
  type PlanFeatureQuota,
  useEntitlementsPlans,
  useBillingSubscription,
} from "@api/billing"
import { useEntitlementsSnapshot } from "@hooks/useEntitlementSnapshot"
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
  const { lang } = useAstrologyLabels()
  const locale = LOCALE_BY_LANG[lang]
  const { data: plans, isLoading, isError, refetch } = useEntitlementsPlans()
  const { data: entitlements } = useEntitlementsSnapshot()
  const { data: subscription } = useBillingSubscription()
  const currentPlanCode = entitlements?.plan_code === "none"
    ? subscription?.plan?.code
    : entitlements?.plan_code ?? subscription?.plan?.code
  const featuredPlanCode = currentPlanCode && currentPlanCode !== "none" ? currentPlanCode : "basic"
  const entryPlan = plans?.reduce<PlanCatalog | null>((lowest, plan) => {
    if (!lowest || plan.monthly_price_cents < lowest.monthly_price_cents) return plan
    return lowest
  }, null)

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
          <div className="help-subscriptions-hero-copy">
            <span className="help-subscriptions-hero-kicker">{t.hero.kicker}</span>
            <h1>{t.hero.title}</h1>
            <p className="help-subscriptions-hero-lead">{t.hero.lead}</p>
            <p>{t.hero.body}</p>
            <div className="help-subscriptions-hero-actions">
              <Button
                as={Link}
                to="/settings/subscription"
                variant="primary"
                className="help-subscriptions-hero-cta"
              >
                {t.hero.cta}
              </Button>
              <a href="#subscription-plans" className="help-subscriptions-hero-link">
                {t.hero.compareCta}
              </a>
            </div>
          </div>

          <div className="settings-card help-subscriptions-hero-panel">
            <div className="help-subscriptions-hero-panel-orbit" aria-hidden="true">
              <span className="help-subscriptions-hero-panel-orbit-core" />
              <span className="help-subscriptions-hero-panel-orbit-ring" />
            </div>
            <span className="help-subscriptions-hero-panel-badge">{t.hero.panelBadge}</span>
            <h2 className="help-subscriptions-hero-panel-title">
              {currentPlanCode && currentPlanCode !== "none"
                ? t.hero.currentPlanLabel.replace(
                    "{plan}",
                    t.plans[currentPlanCode]?.name ?? currentPlanCode,
                  )
                : t.hero.recommendedPlanLabel.replace(
                    "{plan}",
                    t.plans[featuredPlanCode]?.name ?? featuredPlanCode,
                  )}
            </h2>
            <p className="help-subscriptions-hero-panel-price">
              {t.hero.startingFrom.replace(
                "{price}",
                formatPrice(entryPlan?.monthly_price_cents ?? 0, entryPlan?.currency ?? "EUR", locale),
              )}
            </p>
            <ul className="help-subscriptions-hero-panel-list">
              {t.hero.panelPoints.map((point: string) => (
                <li key={point}>{point}</li>
              ))}
            </ul>
          </div>
        </section>

        <section id="subscription-plans" className="help-section help-subscriptions-grid">
          {plans.map((plan) => (
            <PlanCard
              key={plan.plan_code}
              plan={plan}
              isCurrent={plan.plan_code === currentPlanCode}
              isFeatured={plan.plan_code === featuredPlanCode}
              t={t}
            />
          ))}
        </section>

        <section className="help-section help-subscriptions-editorial">
          <EditorialSection section={t.editorial.howToChoose} />
          <EditorialSection
            section={{
              title: t.tokensExplainer.title,
              paragraphs: [t.tokensExplainer.body],
            }}
          />
          <EditorialSection section={t.editorial.flexibility} />
        </section>
      </div>
    </PageLayout>
  )
}

function PlanCard({
  plan,
  isCurrent,
  isFeatured,
  t,
}: {
  plan: PlanCatalog
  isCurrent: boolean
  isFeatured: boolean
  t: SupportSubscriptionsTranslation
}) {
  const { lang } = useAstrologyLabels()
  const locale = LOCALE_BY_LANG[lang]
  const planHighlights: string[] = t.planHighlights[plan.plan_code] ?? []
  const planDescription: string[] = t.plans[plan.plan_code]?.description ?? []
  const planName = t.plans[plan.plan_code]?.name || plan.plan_name
  const promise = planDescription[0] ?? ""
  const detailParagraphs = planDescription.slice(1)
  const visibleHighlights = planHighlights.slice(0, 3)
  const priceFormatter = new Intl.NumberFormat(locale, {
    style: "currency",
    currency: plan.currency,
    minimumFractionDigits: 0,
  })

  return (
    <div
      className={[
        "subscription-plan-card",
        isCurrent ? "subscription-plan-card--active" : "",
        isFeatured ? "subscription-plan-card--featured" : "",
        `subscription-plan-card--${plan.plan_code}`,
        plan.plan_code === "premium" ? "subscription-plan-card--premium" : "",
      ].filter(Boolean).join(" ")}
    >
      {isFeatured && !isCurrent ? (
        <span className="subscription-plan-card__badge">{t.popularBadge}</span>
      ) : null}

      <div className="help-subscriptions-plan-header">
        <div className="help-subscriptions-plan-title-block">
          <h2 className="help-subscriptions-plan-name">{planName}</h2>
          <p className="help-subscriptions-plan-tagline">{t.plans[plan.plan_code]?.tagline}</p>
          <div className="help-subscriptions-plan-badges">
            {plan.processing_priority && (
              <span className={`help-subscriptions-priority-badge help-subscriptions-priority-badge--${plan.processing_priority}`}>
                {t.priority[plan.processing_priority]}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="help-subscriptions-price">
        <span className="help-subscriptions-price-amount">
          {priceFormatter.format(plan.monthly_price_cents / 100)}
        </span>
        <span className="help-subscriptions-price-period">
          {t.perMonth}
        </span>
      </div>
      <p className="help-subscriptions-plan-positioning">{t.plans[plan.plan_code]?.positioning}</p>
      <p className="help-subscriptions-plan-promise">{promise}</p>

      <ul className="help-subscriptions-highlights-list">
        {visibleHighlights.map((highlight) => (
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
      </ul>

      <details className="help-subscriptions-details">
        <summary className="help-subscriptions-details-summary">{t.viewDetails}</summary>
        <div className="help-subscriptions-details-body">
          {detailParagraphs.length > 0 ? (
            <div className="help-subscriptions-details-section">
              <h3 className="help-subscriptions-details-title">{t.detailTitles.experience}</h3>
              {detailParagraphs.map((paragraph) => (
                <p key={`${plan.plan_code}-${paragraph}`} className="help-subscriptions-plan-description">
                  {paragraph}
                </p>
              ))}
            </div>
          ) : null}

          <div className="help-subscriptions-details-section">
            <h3 className="help-subscriptions-details-title">{t.detailTitles.features}</h3>
            <p className="help-subscriptions-details-intro">
              {t.includedTitle.replace("{plan}", planName)}
            </p>
            <ul className="help-subscriptions-features-list">
              {plan.features.map((feature: PlanFeature) => {
                const isTokenFeature = feature.quotas.some(q => q.quota_key === "tokens")
                const shouldHideQuotas = isTokenFeature && (plan.plan_code === "basic" || plan.plan_code === "premium")

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
                )
              })}
            </ul>
          </div>
        </div>
      </details>

      {isCurrent ? (
        <p className="help-subscriptions-current-plan">{t.currentPlan}</p>
      ) : (
        <Button
          as={Link}
          to="/settings/subscription"
          variant="primary"
          fullWidth
          className={[
            "help-subscriptions-cta",
            plan.plan_code === "premium" ? "help-subscriptions-cta--premium" : "",
          ].filter(Boolean).join(" ")}
        >
          {t.upgradeCta}
        </Button>
      )}
    </div>
  )
}

function EditorialSection({
  section,
}: {
  section: {
    title: string
    paragraphs: string[]
  }
}) {
  const icon = getEditorialIcon(section.title)

  return (
    <div className={`settings-card help-subscriptions-editorial-card help-subscriptions-editorial-card--${icon.tone}`}>
      <div className="help-subscriptions-editorial-head">
        <span className="help-subscriptions-editorial-icon" aria-hidden="true">
          <icon.Component size={18} />
        </span>
        <h2 className="help-subscriptions-editorial-title">{section.title}</h2>
      </div>
      {section.paragraphs.map((paragraph) => (
        <p key={`${section.title}-${paragraph}`} className="help-subscriptions-editorial-copy">
          {paragraph}
        </p>
      ))}
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

function formatPrice(amountCents: number, currency: string, locale: string) {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
  }).format(amountCents / 100)
}

function getEditorialIcon(title: string) {
  if (title.toLowerCase().includes("token")) {
    return { Component: Sparkles, tone: "insight" }
  }
  if (
    title.toLowerCase().includes("change")
    || title.toLowerCase().includes("changer")
    || title.toLowerCase().includes("cambiar")
  ) {
    return { Component: RefreshCcw, tone: "flex" }
  }

  return { Component: Telescope, tone: "choice" }
}

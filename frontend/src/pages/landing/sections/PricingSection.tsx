import { useEffect, useRef } from "react"
import { Link } from "react-router-dom"
import { Check, X } from "lucide-react"
import { Button } from "../../../components/ui/Button/Button"
import { getActivePlans, formatPrice } from "../../../config/pricingConfig"
import { useAnalytics } from "../../../hooks/useAnalytics"
import { useAstrologyLabels, useTranslation } from "../../../i18n"
import "./PricingSection.css"

export const PricingSection = () => {
  const t = useTranslation("landing")
  const { lang } = useAstrologyLabels()
  const { track } = useAnalytics()
  const sectionRef = useRef<HTMLElement>(null)
  const activePlans = getActivePlans()

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return
        track("pricing_view")
        observer.unobserve(entry.target)
      },
      { threshold: 0.35 },
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => observer.disconnect()
  }, [track])

  const planAudience: Record<string, string> = {
    free: t.pricing.audience.free,
    basic: t.pricing.audience.basic,
    premium: t.pricing.audience.premium,
  }

  return (
    <section id="pricing" className="pricing-section" ref={sectionRef} aria-labelledby="pricing-title">
      <div className="pricing-section__heading">
        <span className="pricing-section__eyebrow">{t.pricing.eyebrow}</span>
        <h2 id="pricing-title">{t.pricing.title}</h2>
        <p>{t.pricing.subtitle}</p>
      </div>

      <div className="pricing-reassurance-bar">{t.pricing.reassurance}</div>

      <div className="pricing-grid">
        {activePlans.map((plan) => {
          const planTranslation = (t.pricing.plans as Record<string, { name: string; desc: string }>)[
            plan.planCode
          ]

          return (
            <article
              key={plan.planCode}
              className={`pricing-card ${plan.isRecommended ? "pricing-card--recommended" : ""}`}
            >
              {plan.isRecommended && <div className="pricing-badge">{t.pricing.recommended}</div>}

              <div className="pricing-card-header">
                <span className="pricing-plan-audience">{planAudience[plan.planCode]}</span>
                <h3 className="pricing-plan-name">{planTranslation.name}</h3>
                <div className="pricing-price">
                  <span className="pricing-amount">
                    {plan.monthlyPriceCents === 0
                      ? t.pricing.freeLabel
                      : formatPrice(plan.monthlyPriceCents, plan.currency, lang)}
                  </span>
                  {plan.monthlyPriceCents !== 0 && (
                    <span className="pricing-period">{t.pricing.perMonth}</span>
                  )}
                </div>
                <p className="pricing-plan-desc">{planTranslation.desc}</p>
              </div>

              <ul className="pricing-features" aria-label={`${t.pricing.ariaFeatures} ${planTranslation.name}`}>
                {plan.features.map((feature) => (
                  <li
                    key={feature.id}
                    className={`pricing-feature-item ${
                      feature.enabled ? "" : "pricing-feature-item--disabled"
                    }`}
                  >
                    <div className="pricing-feature-icon" aria-hidden="true">
                      {feature.enabled ? <Check size={18} /> : <X size={18} />}
                    </div>
                    <span className="pricing-feature-text">
                      <span>{(t.pricing.features as Record<string, string>)[feature.id]}</span>
                      {feature.quota && <span className="pricing-feature-quota">{feature.quota}</span>}
                    </span>
                  </li>
                ))}
              </ul>

              <Button
                as={Link}
                to={`/register?plan=${plan.planCode}`}
                variant={plan.isRecommended ? "primary" : "secondary"}
                size="lg"
                fullWidth
                className={`pricing-cta ${plan.isRecommended ? "pricing-cta--recommended" : ""}`}
                onClick={() => track("pricing_plan_select", { plan_id: plan.planCode })}
              >
                {plan.planCode === "free" ? t.pricing.cta.free : t.pricing.cta.paid}
              </Button>
            </article>
          )
        })}
      </div>
    </section>
  )
}

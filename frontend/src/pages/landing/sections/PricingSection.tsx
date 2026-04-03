import { useEffect, useRef } from "react"
import { Link } from "react-router-dom"
import { Check, X } from "lucide-react"
import { Button } from "../../../components/ui/Button/Button"
import { useTranslation, useAstrologyLabels } from "../../../i18n"
import { useAnalytics } from "../../../hooks/useAnalytics"
import { getActivePlans, formatPrice } from "../../../config/pricingConfig"
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
        if (entry.isIntersecting) {
          track('pricing_view')
          observer.unobserve(entry.target)
        }
      },
      { threshold: 0.5 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => observer.disconnect()
  }, [track])

  return (
    <section id="pricing" className="pricing-section" ref={sectionRef}>
      <h2>{t.pricing.title}</h2>

      <div className="pricing-grid">
        {activePlans.map((plan) => {
          const planT = (t.pricing.plans as any)[plan.planCode]
          
          return (
            <div 
              key={plan.planCode} 
              className={`pricing-card ${plan.isRecommended ? "pricing-card--recommended" : ""}`}
            >
              {plan.isRecommended && (
                <div className="pricing-badge">{t.pricing.recommended}</div>
              )}

              <div className="pricing-card-header">
                <span className="pricing-plan-name">{planT.name}</span>
                <div className="pricing-price">
                  <span className="pricing-amount">
                    {formatPrice(plan.monthlyPriceCents, plan.currency, lang)}
                  </span>
                  {plan.monthlyPriceCents !== 0 && (
                    <span className="pricing-period">{t.pricing.perMonth}</span>
                  )}
                </div>
                <p className="pricing-plan-desc">{planT.desc}</p>
              </div>

              <ul className="pricing-features">
                {plan.features.map((feature) => (
                  <li 
                    key={feature.id} 
                    className={`pricing-feature-item ${!feature.enabled ? "pricing-feature-item--disabled" : ""}`}
                  >
                    <div className="pricing-feature-icon">
                      {feature.enabled ? <Check size={18} /> : <X size={18} />}
                    </div>
                    <span>
                      {(t.pricing.features as any)[feature.id]}
                      {feature.quota && (
                        <span className="pricing-feature-quota">({feature.quota})</span>
                      )}
                    </span>
                  </li>
                ))}
              </ul>

              <div className="pricing-actions">
                <Button
                  as={Link}
                  to={`/register?plan=${plan.planCode}`}
                  variant={plan.isRecommended ? "primary" : "secondary"}
                  fullWidth
                  size="lg"
                  onClick={() => track('pricing_plan_select', { plan_id: plan.planCode })}
                >
                  {plan.planCode === 'free' ? t.pricing.cta.free : t.pricing.cta.paid}
                </Button>
              </div>
            </div>
          )
        })}
      </div>

      <p className="pricing-reassurance">
        {t.pricing.reassurance}
      </p>
    </section>
  )
}

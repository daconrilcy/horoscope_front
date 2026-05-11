// Section hero de la landing, limitee au rendu et aux CTA analytics.
import { ArrowRight, Check, Clock3, MessageCircleMore, ShieldCheck, Sparkles, Star } from "lucide-react"
import { Link } from "react-router-dom"
import { Button } from "../../../components/ui/Button/Button"
import { useAnalytics } from "../../../hooks/useAnalytics"
import { useTranslation } from "../../../i18n"

/**
 * Rend le premier ecran marketing sans timer JavaScript.
 */
export const HeroSection = () => {
  const t = useTranslation("landing")
  const { track } = useAnalytics()

  return (
    <section className="hero-section" aria-labelledby="hero-title">
      <div className="hero-content">
        <div className="hero-eyebrow">
          <Sparkles size={14} aria-hidden="true" />
          {t.hero.eyebrow}
        </div>

        <h1 id="hero-title" aria-label={`${t.hero.titleLead} - ${t.hero.titleAccent}`}>
          <span className="hero-title__lead">{t.hero.titleLead}</span>
          <span className="hero-title__accent">{t.hero.titleAccent}</span>
        </h1>
        <p className="hero-subtitle">{t.hero.subtitle}</p>

        <ul className="hero-bullets">
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={18} aria-hidden="true" />
            <span>{t.hero.bullet1}</span>
          </li>
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={18} aria-hidden="true" />
            <span>{t.hero.bullet2}</span>
          </li>
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={18} aria-hidden="true" />
            <span>{t.hero.bullet3}</span>
          </li>
        </ul>

        <div className="hero-ctas">
          <Button
            as={Link}
            to="/register"
            variant="primary"
            size="lg"
            className="hero-cta-primary"
            onClick={() => track("hero_cta_click", { cta_label: t.hero.ctaPrimary })}
          >
            {t.hero.ctaPrimary}
            <ArrowRight size={18} className="hero-cta-icon-right" aria-hidden="true" />
          </Button>

          <a
            href="#how-it-works"
            className="hero-cta-secondary"
            onClick={() => track("secondary_cta_click", { cta_label: t.hero.ctaSecondary })}
          >
            <MessageCircleMore size={18} className="hero-cta-icon-left" aria-hidden="true" />
            {t.hero.ctaSecondary}
          </a>
        </div>

        <div className="hero-proof-strip" aria-label={t.socialProof.badges.swiss}>
          <ShieldCheck size={18} className="hero-proof-strip__icon" aria-hidden="true" />
          <strong>{t.socialProof.badges.swiss}</strong>
          <span>{t.socialProof.proofs.swiss}</span>
        </div>

        <div className="hero-reassurance">
          <div className="hero-reassurance-item">
            <span className="hero-reassurance-dot" aria-hidden="true"></span>
            {t.hero.micro1}
          </div>
          <div className="hero-reassurance-item">
            <span className="hero-reassurance-dot" aria-hidden="true"></span>
            {t.hero.micro2}
          </div>
          <div className="hero-reassurance-item">
            <span className="hero-reassurance-dot" aria-hidden="true"></span>
            {t.hero.micro3}
          </div>
        </div>
      </div>

      <div className="hero-visual" aria-label={t.hero.imageAlt}>
        <div className="hero-visual-shell">
          <div className="hero-device">
            <div className="hero-device__bar">
              <div className="hero-device__brand">
                <span className="hero-device__dot"></span>
                <span className="hero-device__dot"></span>
                <span className="hero-device__dot"></span>
                <span className="hero-device__brand-name">Astrorizon</span>
              </div>
              <span className="hero-device__status">{t.hero.caption1}</span>
            </div>

            <div className="hero-device__preview">
              <span className="hero-device__preview-label">{t.hero.previewLabel}</span>
            </div>

            <div className="hero-device__toolbar" aria-hidden="true">
              <span className="hero-device__tool hero-device__tool--active">
                <Clock3 size={13} />
                <span>{t.hero.dailyLabel}</span>
              </span>
              <span className="hero-device__tool">
                <MessageCircleMore size={13} />
                <span>{t.hero.chatLabel}</span>
              </span>
              <span className="hero-device__tool">
                <Star size={13} />
                <span>{t.hero.momentLabel}</span>
              </span>
            </div>

            <article className="hero-card hero-card--summary">
              <div className="hero-panel__meta">
                <span className="hero-panel__label">
                  <Clock3 size={14} aria-hidden="true" />
                  {t.hero.dailyLabel}
                </span>
                <span className="hero-panel__badge">{t.hero.caption2}</span>
              </div>
              <h2 className="hero-panel__title">{t.hero.dailyTitle}</h2>
              <div className="hero-card__trend-grid">
                {t.hero.dailyItems.map(({ label, value }, index) => (
                  <div
                    key={label}
                    className={`hero-card__trend-item ${
                      index === 0 ? "hero-card__trend-item--active" : ""
                    }`}
                  >
                    <span className="hero-card__trend-label">{label}</span>
                    <strong className="hero-card__trend-value">{value}</strong>
                  </div>
                ))}
              </div>

              <div className="hero-card__insight">
                <div className="hero-card__question">
                  <MessageCircleMore size={14} aria-hidden="true" />
                  <span>{t.hero.chatQuestion}</span>
                </div>
                <div className="hero-card__moment">
                  <Sparkles size={16} aria-hidden="true" />
                  <span>{t.solution.step3.benefit}</span>
                </div>
              </div>
            </article>
          </div>
        </div>
      </div>
    </section>
  )
}

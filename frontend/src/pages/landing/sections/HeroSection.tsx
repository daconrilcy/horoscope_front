import { Link } from "react-router-dom"
import { Check, ArrowRight, Play } from "lucide-react"
import { Button } from "../../../components/ui/Button/Button"
import { useTranslation } from "../../../i18n"
import { useAnalytics } from "../../../hooks/useAnalytics"
import logo from "../../../assets/logo.PNG"

export const HeroSection = () => {
  const t = useTranslation("landing")
  const { track } = useAnalytics()

  return (
    <section className="hero-section" aria-labelledby="hero-title">
      <div className="hero-content">
        <h1 id="hero-title">{t.hero.title}</h1>
        <p className="hero-subtitle">{t.hero.subtitle}</p>

        <ul className="hero-bullets">
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={20} aria-hidden="true" />
            <span>{t.hero.bullet1}</span>
          </li>
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={20} aria-hidden="true" />
            <span>{t.hero.bullet2}</span>
          </li>
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={20} aria-hidden="true" />
            <span>{t.hero.bullet3}</span>
          </li>
        </ul>

        <div className="hero-ctas">
          <Button 
            as={Link} 
            to="/register" 
            variant="primary" 
            size="lg"
            aria-label={t.hero.ctaPrimary}
            onClick={() => track('hero_cta_click', { cta_label: t.hero.ctaPrimary })}
          >
            {t.hero.ctaPrimary}
            <ArrowRight size={20} style={{ marginLeft: '8px' }} aria-hidden="true" />
          </Button>

          <a 
            href="#how-it-works" 
            className="hero-cta-secondary"
            aria-label={t.hero.ctaSecondary}
            onClick={() => track('secondary_cta_click')}
          >
            <Play size={18} style={{ marginRight: '10px', fill: 'currentColor' }} aria-hidden="true" />
            {t.hero.ctaSecondary}
          </a>
        </div>

        <div className="hero-reassurance">
          <div className="hero-reassurance-item">
            <span className="hero-reassurance-dot"></span>
            {t.hero.micro1}
          </div>
          <div className="hero-reassurance-item">
            <span className="hero-reassurance-dot"></span>
            {t.hero.micro2}
          </div>
          <div className="hero-reassurance-item">
            <span className="hero-reassurance-dot"></span>
            {t.hero.micro3}
          </div>
        </div>
      </div>

      <div className="hero-visual">
        {/* AC2: Reserve fixed space. Using a placeholder for now as real screenshot might not be in assets yet */}
        <div className="hero-visual-placeholder" style={{ aspectRatio: '4/3' }}>
          <img 
            src={logo} 
            alt={t.hero.imageAlt} 
            width="120"
            height="120"
            loading="eager"
            fetchPriority="high"
            style={{ width: '120px', height: '120px', marginBottom: '20px', opacity: 0.5 }}
          />
          <p style={{ maxWidth: '240px' }}>{t.hero.imageAlt}</p>
        </div>
        
        <div className="hero-visual-caption hero-visual-caption--1">
          {t.hero.caption1}
        </div>
        <div className="hero-visual-caption hero-visual-caption--2">
          {t.hero.caption2}
        </div>
      </div>
    </section>
  )
}

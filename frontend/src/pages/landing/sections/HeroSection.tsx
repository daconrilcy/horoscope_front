import { Link } from "react-router-dom"
import { Check, ArrowRight, Play } from "lucide-react"
import { Button } from "../../../components/ui/Button/Button"
import { useTranslation } from "../../../i18n"

export const HeroSection = () => {
  const t = useTranslation("landing")

  return (
    <section className="hero-section">
      <div className="hero-content">
        <h1>{t.hero.title}</h1>
        <p className="hero-subtitle">{t.hero.subtitle}</p>
        
        <ul className="hero-bullets">
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={20} />
            <span>{t.hero.bullet1}</span>
          </li>
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={20} />
            <span>{t.hero.bullet2}</span>
          </li>
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={20} />
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
          >
            {t.hero.ctaPrimary}
            <ArrowRight size={20} style={{ marginLeft: '8px' }} />
          </Button>
          
          <a 
            href="#how-it-works" 
            className="hero-cta-secondary"
            aria-label={t.hero.ctaSecondary}
          >
            <Play size={18} style={{ marginRight: '10px', fill: 'currentColor' }} />
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
        <div className="hero-visual-placeholder">
          <img 
            src="/src/assets/logo.PNG" 
            alt={t.hero.imageAlt} 
            style={{ width: '120px', marginBottom: '20px', opacity: 0.5 }}
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

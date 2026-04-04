import { useState } from "react"
import { ChevronDown } from "lucide-react"
import { Link } from "react-router-dom"
import { Button } from "../../../components/ui/Button/Button"
import { useAstrologyLabels, useTranslation } from "../../../i18n"
import "./FaqSection.css"

const FAQ_LOCAL_COPY = {
  fr: {
    eyebrow: "Objections",
    decision: "Décision",
    subtitle: "Les questions les plus fréquentes avant de commencer.",
    ctaTitle: "Commencez votre thème natal en quelques minutes",
    ctaBody: "Essayez Astrorizon gratuitement dès aujourd'hui et voyez immédiatement comment la guidance s'applique à votre situation.",
  },
  en: {
    eyebrow: "Objections",
    decision: "Decision",
    subtitle: "The most common questions before getting started.",
    ctaTitle: "Start your birth chart in just a few minutes",
    ctaBody: "Try Astrorizon for free today and immediately see how the guidance applies to your situation.",
  },
  es: {
    eyebrow: "Objeciones",
    decision: "Decisión",
    subtitle: "Las preguntas más frecuentes antes de empezar.",
    ctaTitle: "Empieza tu carta natal en solo unos minutos",
    ctaBody: "Prueba Astrorizon gratis hoy y comprueba de inmediato cómo la guía se aplica a tu situación.",
  },
} as const

export const FaqSection = () => {
  const t = useTranslation("landing")
  const { lang } = useAstrologyLabels()
  const localCopy = FAQ_LOCAL_COPY[lang]
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  return (
    <section id="faq" className="faq-section" aria-labelledby="faq-title">
      <div className="faq-section__heading">
        <span className="faq-section__eyebrow">{localCopy.eyebrow}</span>
        <h2 id="faq-title">{t.faq.title}</h2>
        <p>{localCopy.subtitle}</p>
      </div>

      <div className="faq-accordion">
        {t.faq.items.map((item, index) => (
          <details
            key={item.q}
            className="faq-item"
            name="landing-faq"
            open={openIndex === index}
            onToggle={(event) => {
              const current = event.currentTarget
              if (current.open) {
                setOpenIndex(index)
              } else if (openIndex === index) {
                setOpenIndex(null)
              }
            }}
          >
            <summary
              className="faq-summary"
              aria-expanded={openIndex === index}
              aria-controls={`faq-content-${index}`}
              id={`faq-summary-${index}`}
            >
              <span>{item.q}</span>
              <ChevronDown className="faq-chevron" size={20} aria-hidden="true" />
            </summary>
            <div
              className="faq-content"
              id={`faq-content-${index}`}
              role="region"
              aria-labelledby={`faq-summary-${index}`}
            >
              <p>{item.a}</p>
            </div>
          </details>
        ))}
      </div>

      <div className="final-cta-section" aria-labelledby="final-cta-title">
        <div className="final-cta-content">
          <span className="final-cta-eyebrow">{localCopy.decision}</span>
          <h2 id="final-cta-title">{localCopy.ctaTitle}</h2>
          <p>{localCopy.ctaBody}</p>
        </div>

        <div className="final-cta-actions">
          <Button as={Link} to="/register" variant="primary" size="lg" className="final-cta-button">
            {t.finalCta.button}
          </Button>
          <div className="final-cta-reassurance">
            <span>{t.finalCta.micro1}</span>
            <span>{t.finalCta.micro2}</span>
          </div>
        </div>
      </div>
    </section>
  )
}

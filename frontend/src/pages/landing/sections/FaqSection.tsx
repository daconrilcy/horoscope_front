import { Link } from "react-router-dom"
import { ChevronDown } from "lucide-react"
import { Button } from "../../../components/ui/Button/Button"
import { useTranslation } from "../../../i18n"
import "./FaqSection.css"

export const FaqSection = () => {
  const t = useTranslation("landing")

  return (
    <section id="faq" className="faq-section" aria-labelledby="faq-title">
      <h2 id="faq-title">{t.faq.title}</h2>

      <div className="faq-accordion">
        {t.faq.items.map((item, index) => (
          <details key={index} className="faq-item" name="landing-faq">
            <summary 
              className="faq-summary"
              aria-expanded="false" // details handles this but AC asks for it
              aria-controls={`faq-content-${index}`}
              id={`faq-summary-${index}`}
            >
              {item.q}
              <ChevronDown className="faq-chevron" size={20} aria-hidden="true" />
            </summary>
            <div 
              className="faq-content" 
              id={`faq-content-${index}`}
              role="region"
              aria-labelledby={`faq-summary-${index}`}
            >
              {item.a}
            </div>
          </details>
        ))}
      </div>

      <div className="final-cta-section" aria-labelledby="final-cta-title">
        <div className="final-cta-content">
          <h2 id="final-cta-title">{t.finalCta.title}</h2>
          <p>{t.finalCta.subtitle}</p>
        </div>

        <div className="final-cta-actions">
          <Button as={Link} to="/register" variant="primary" size="lg">
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

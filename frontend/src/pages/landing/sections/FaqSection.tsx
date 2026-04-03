import { Link } from "react-router-dom"
import { ChevronDown } from "lucide-react"
import { Button } from "../../../components/ui/Button/Button"
import { useTranslation } from "../../../i18n"
import "./FaqSection.css"

export const FaqSection = () => {
  const t = useTranslation("landing")

  return (
    <section id="faq" className="faq-section">
      <h2>{t.faq.title}</h2>

      <div className="faq-accordion">
        {t.faq.items.map((item, index) => (
          <details key={index} className="faq-item" name="landing-faq">
            <summary className="faq-summary">
              {item.q}
              <ChevronDown className="faq-chevron" size={20} />
            </summary>
            <div className="faq-content">
              {item.a}
            </div>
          </details>
        ))}
      </div>

      <div className="final-cta-section">
        <div className="final-cta-content">
          <h2>{t.finalCta.title}</h2>
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

import { Lock, Star, RotateCcw, ShieldCheck } from "lucide-react"
import { useTranslation } from "../../../i18n"
import "./TestimonialsSection.css"

export const TestimonialsSection = () => {
  const t = useTranslation("landing")
  
  // AC1.3: Feature flag
  const showTestimonials = import.meta.env.VITE_SHOW_TESTIMONIALS === "true"

  if (!showTestimonials) {
    return null
  }

  return (
    <section id="testimonials" className="testimonials-section" aria-labelledby="testimonials-title">
      <div className="testimonials-header">
        <h2 id="testimonials-title">{t.testimonials.title}</h2>
        <p>{t.testimonials.subtitle}</p>
      </div>

      <div className="testimonials-grid">
        {t.testimonials.items.map((item, index) => (
          <div key={index} className="testimonial-card">
            <div className="testimonial-quote">
              “{item.quote}”
            </div>
            <div className="testimonial-footer">
              <div className="testimonial-avatar" aria-hidden="true">
                {item.author.charAt(0)}
              </div>
              <div className="testimonial-info">
                <span className="testimonial-author">{item.author}</span>
                <span className="testimonial-context">{item.context}</span>
              </div>
              {item.rating && (
                <div 
                  style={{ marginLeft: 'auto', display: 'flex', color: '#f1c40f' }}
                  aria-label={`Note : ${item.rating} sur 5 étoiles`}
                >
                  {[...Array(item.rating)].map((_, i) => (
                    <Star key={i} size={14} fill="currentColor" aria-hidden="true" />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="case-study" aria-labelledby="case-study-title">
        <div className="case-study-header">
          <span className="case-study-badge" aria-hidden="true">{t.testimonials.caseStudy.badge}</span>
          <h3 id="case-study-title">{t.testimonials.caseStudy.title}</h3>
        </div>

        <div className="case-study-grid">
          <div className="case-study-column case-study-column--before">
            <span className="case-study-label">{t.testimonials.caseStudy.before.label}</span>
            <p className="case-study-text">{t.testimonials.caseStudy.before.text}</p>
          </div>
          <div className="case-study-column case-study-column--after">
            <span className="case-study-label">{t.testimonials.caseStudy.after.label}</span>
            <p className="case-study-text">{t.testimonials.caseStudy.after.text}</p>
          </div>
          <div className="case-study-column case-study-column--action">
            <span className="case-study-label">{t.testimonials.caseStudy.action.label}</span>
            <p className="case-study-text">{t.testimonials.caseStudy.action.text}</p>
          </div>
        </div>
      </div>

      <div className="reassurance-badges">
        <div className="reassurance-badge">
          <Lock className="reassurance-badge-icon" size={20} aria-hidden="true" />
          {t.testimonials.reassurance.data}
        </div>
        <div className="reassurance-badge">
          <ShieldCheck className="reassurance-badge-icon" size={20} aria-hidden="true" />
          {t.testimonials.reassurance.swiss}
        </div>
        <div className="reassurance-badge">
          <RotateCcw className="reassurance-badge-icon" size={20} aria-hidden="true" />
          {t.testimonials.reassurance.cancel}
        </div>
      </div>
    </section>
  )
}

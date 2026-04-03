import { useEffect, useRef, useState } from "react"
import { ShieldCheck, Zap, Globe } from "lucide-react"
import { useTranslation } from "../../../i18n"
import "./SocialProofSection.css"

export const SocialProofSection = () => {
  const t = useTranslation("landing")
  const sectionRef = useRef<HTMLElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  // AC1.4: Feature flag for variant
  const variant = import.meta.env.VITE_SOCIAL_PROOF_VARIANT || "badges"

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.unobserve(entry.target)
        }
      },
      { threshold: 0.1 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  return (
    <section 
      id="social-proof" 
      ref={sectionRef}
      className={`social-proof-section ${isVisible ? "social-proof-section--visible" : ""}`}
    >
      <div className="social-proof__container">
        {variant === "badges" ? (
          <>
            <div className="social-proof__item">
              <div className="social-proof__icon">
                <Globe size={24} />
              </div>
              <div className="social-proof__content">
                <span className="social-proof__value">{t.socialProof.badges.swiss}</span>
              </div>
            </div>
            
            <div className="social-proof__item">
              <div className="social-proof__icon">
                <ShieldCheck size={24} />
              </div>
              <div className="social-proof__content">
                <span className="social-proof__value">{t.socialProof.badges.rgpd}</span>
              </div>
            </div>

            <div className="social-proof__item">
              <div className="social-proof__icon">
                <Zap size={24} />
              </div>
              <div className="social-proof__content">
                <span className="social-proof__value">{t.socialProof.badges.available}</span>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* AC1.1: Metrics are now coming from i18n */}
            <div className="social-proof__item">
              <div className="social-proof__icon">
                <Globe size={24} />
              </div>
              <div className="social-proof__content">
                <span className="social-proof__value">{t.socialProof.metrics.usersValue}</span>
                <span className="social-proof__label">{t.socialProof.metrics.users}</span>
              </div>
            </div>
            
            <div className="social-proof__item">
              <div className="social-proof__icon">
                <ShieldCheck size={24} />
              </div>
              <div className="social-proof__content">
                <span className="social-proof__value">{t.socialProof.metrics.ratingValue}</span>
                <span className="social-proof__label">{t.socialProof.metrics.rating}</span>
              </div>
            </div>

            <div className="social-proof__item">
              <div className="social-proof__icon">
                <Zap size={24} />
              </div>
              <div className="social-proof__content">
                <span className="social-proof__value">{t.socialProof.metrics.consultationsValue}</span>
                <span className="social-proof__label">{t.socialProof.metrics.consultations}</span>
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  )
}

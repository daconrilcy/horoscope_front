import { Globe, ShieldCheck, Zap } from "lucide-react"
import { useAstrologyLabels, useTranslation } from "../../../i18n"
import "./SocialProofSection.css"

const SOCIAL_PROOF_LOCAL_COPY = {
  fr: {
    eyebrow: "Confiance",
    title: "Une expérience utile, cadrée et crédible dès la première visite.",
    swissProof: "Positions planétaires calculées avec un moteur de référence.",
    rgpdProof: "Naissance, échanges et compte utilisateur traités de façon sécurisée.",
    availableProof: "Réponses immédiates, sans attente ni prise de rendez-vous.",
  },
  en: {
    eyebrow: "Trust",
    title: "A useful, credible experience from the very first visit.",
    swissProof: "Planetary positions calculated with a reference-grade engine.",
    rgpdProof: "Birth data, conversations, and account data are handled securely.",
    availableProof: "Immediate answers, without waiting or booking a consultation.",
  },
  es: {
    eyebrow: "Confianza",
    title: "Una experiencia útil, clara y creíble desde la primera visita.",
    swissProof: "Posiciones planetarias calculadas con un motor de referencia.",
    rgpdProof: "Nacimiento, conversaciones y cuenta tratados de forma segura.",
    availableProof: "Respuestas inmediatas, sin espera ni cita previa.",
  },
} as const

export const SocialProofSection = () => {
  const t = useTranslation("landing")
  const { lang } = useAstrologyLabels()
  const localCopy = SOCIAL_PROOF_LOCAL_COPY[lang]

  const items = [
    {
      key: "swiss",
      icon: <Globe size={22} aria-hidden="true" />,
      title: t.socialProof.badges.swiss,
      proof: localCopy.swissProof,
    },
    {
      key: "rgpd",
      icon: <ShieldCheck size={22} aria-hidden="true" />,
      title: t.socialProof.badges.rgpd,
      proof: localCopy.rgpdProof,
    },
    {
      key: "available",
      icon: <Zap size={22} aria-hidden="true" />,
      title: t.socialProof.badges.available,
      proof: localCopy.availableProof,
    },
  ]

  return (
    <section id="social-proof" className="social-proof-section" aria-labelledby="social-proof-title">
      <div className="social-proof__container">
        <div className="social-proof__intro">
          <span className="social-proof__eyebrow">{localCopy.eyebrow}</span>
          <h2 id="social-proof-title">{localCopy.title}</h2>
        </div>

        <div className="social-proof__grid">
          {items.map((item) => (
            <article key={item.key} className="social-proof__item">
              <div className="social-proof__icon">{item.icon}</div>
              <div className="social-proof__content">
                <h3 className="social-proof__value">{item.title}</h3>
                <p className="social-proof__label">{item.proof}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

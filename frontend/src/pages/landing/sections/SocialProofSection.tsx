import { Globe, ShieldCheck, Zap } from "lucide-react"
import { useTranslation } from "../../../i18n"
import "./SocialProofSection.css"

export const SocialProofSection = () => {
  const t = useTranslation("landing")

  const items = [
    {
      key: "swiss",
      icon: <Globe size={22} aria-hidden="true" />,
      title: t.socialProof.badges.swiss,
      proof: t.socialProof.proofs.swiss,
    },
    {
      key: "rgpd",
      icon: <ShieldCheck size={22} aria-hidden="true" />,
      title: t.socialProof.badges.rgpd,
      proof: t.socialProof.proofs.rgpd,
    },
    {
      key: "available",
      icon: <Zap size={22} aria-hidden="true" />,
      title: t.socialProof.badges.available,
      proof: t.socialProof.proofs.available,
    },
  ]

  return (
    <section id="social-proof" className="social-proof-section" aria-labelledby="social-proof-title">
      <div className="social-proof__container">
        <div className="social-proof__intro">
          <span className="social-proof__eyebrow">{t.socialProof.eyebrow}</span>
          <h2 id="social-proof-title">{t.socialProof.title}</h2>
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

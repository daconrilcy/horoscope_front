import { AlertCircle, CheckCircle2, Sparkles, XCircle } from "lucide-react"
import { useAstrologyLabels, useTranslation } from "../../../i18n"
import "./ProblemSection.css"

const INTRO_BY_LANG = {
  fr: "Vous cherchez une guidance personnelle, pas des généralités.",
  en: "You are looking for personal guidance, not generic content.",
  es: "Buscas una guía personal, no generalidades.",
} as const

const EYEBROW_BY_LANG = {
  fr: "Transformation",
  en: "Transformation",
  es: "Transformación",
} as const

export const ProblemSection = () => {
  const t = useTranslation("landing")
  const { lang } = useAstrologyLabels()

  const beforeItems = [
    { id: "before-1", text: t.problem.before.item1, icon: <XCircle size={20} /> },
    { id: "before-2", text: t.problem.before.item2, icon: <XCircle size={20} /> },
    { id: "before-3", text: t.problem.before.item3, icon: <XCircle size={20} /> },
  ]

  const afterItems = [
    { id: "after-1", text: t.problem.after.item1, icon: <CheckCircle2 size={20} /> },
    { id: "after-2", text: t.problem.after.item2, icon: <CheckCircle2 size={20} /> },
    { id: "after-3", text: t.problem.after.item3, icon: <CheckCircle2 size={20} /> },
  ]

  return (
    <section id="problem" className="problem-section" aria-labelledby="problem-title">
      <div className="problem-section__heading">
        <span className="problem-section__eyebrow">{EYEBROW_BY_LANG[lang]}</span>
        <h2 id="problem-title">{t.problem.title}</h2>
        <p>{INTRO_BY_LANG[lang]}</p>
      </div>

      <div className="problem-container">
        <article className="problem-column problem-column--before">
          <h3 className="problem-column-title">
            <AlertCircle size={22} aria-hidden="true" />
            {t.problem.before.title}
          </h3>
          <ul className="problem-list">
            {beforeItems.map((item) => (
              <li key={item.id} className="problem-item">
                <div className="problem-item-icon" aria-hidden="true">
                  {item.icon}
                </div>
                <div className="problem-item-text">{item.text}</div>
              </li>
            ))}
          </ul>
        </article>

        <article className="problem-column problem-column--after">
          <h3 className="problem-column-title">
            <Sparkles size={22} aria-hidden="true" />
            {t.problem.after.title}
          </h3>
          <ul className="problem-list">
            {afterItems.map((item) => (
              <li key={item.id} className="problem-item">
                <div className="problem-item-icon" aria-hidden="true">
                  {item.icon}
                </div>
                <div className="problem-item-text">{item.text}</div>
              </li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  )
}

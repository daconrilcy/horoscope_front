import { Calendar, MessageCircle, Sparkles } from "lucide-react"
import { useAstrologyLabels, useTranslation } from "../../../i18n"
import "./SolutionSection.css"

const SOLUTION_LOCAL_COPY = {
  fr: {
    eyebrow: "Fonctionnement",
    subtitle: "Trois étapes simples pour passer de l'intuition à une guidance exploitable.",
    step1Example: "Date, heure, lieu de naissance",
    step2Example: "“Est-ce le bon moment pour relancer cette conversation ?”",
    step3Example: "Fenêtre favorable, ton du jour, conseil concret",
  },
  en: {
    eyebrow: "How it works",
    subtitle: "Three simple steps to move from intuition to usable guidance.",
    step1Example: "Date, time, place of birth",
    step2Example: "“Is this the right time to restart this conversation?”",
    step3Example: "Best window, tone of the day, concrete advice",
  },
  es: {
    eyebrow: "Funcionamiento",
    subtitle: "Tres pasos simples para pasar de la intuición a una guía accionable.",
    step1Example: "Fecha, hora y lugar de nacimiento",
    step2Example: "“¿Es el momento adecuado para retomar esta conversación?”",
    step3Example: "Ventana favorable, tono del día y consejo concreto",
  },
} as const

export const SolutionSection = () => {
  const t = useTranslation("landing")
  const { lang } = useAstrologyLabels()
  const localCopy = SOLUTION_LOCAL_COPY[lang]

  const steps = [
    {
      id: "01",
      icon: <Calendar size={22} aria-hidden="true" />,
      title: t.solution.step1.title,
      desc: t.solution.step1.desc,
      benefit: t.solution.step1.benefit,
      example: localCopy.step1Example,
    },
    {
      id: "02",
      icon: <MessageCircle size={22} aria-hidden="true" />,
      title: t.solution.step2.title,
      desc: t.solution.step2.desc,
      benefit: t.solution.step2.benefit,
      example: localCopy.step2Example,
    },
    {
      id: "03",
      icon: <Sparkles size={22} aria-hidden="true" />,
      title: t.solution.step3.title,
      desc: t.solution.step3.desc,
      benefit: t.solution.step3.benefit,
      example: localCopy.step3Example,
    },
  ]

  return (
    <section id="how-it-works" className="solution-section" aria-labelledby="solution-title">
      <div className="solution-section__heading">
        <span className="solution-section__eyebrow">{localCopy.eyebrow}</span>
        <h2 id="solution-title">{t.solution.title}</h2>
        <p>{localCopy.subtitle}</p>
      </div>

      <div className="solution-container">
        {steps.map((step) => (
          <article key={step.id} className="solution-card">
            <div className="solution-card__top">
              <span className="solution-step-number">{step.id}</span>
              <div className="solution-card-icon">{step.icon}</div>
            </div>

            <div className="solution-card-content">
              <h3>{step.title}</h3>
              <p>{step.desc}</p>
            </div>

            <div className="solution-card-example">{step.example}</div>
            <div className="solution-benefit-badge">{step.benefit}</div>
          </article>
        ))}
      </div>
    </section>
  )
}

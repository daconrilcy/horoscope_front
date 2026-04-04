import { Calendar, MessageCircle, Sparkles } from "lucide-react"
import { useTranslation } from "../../../i18n"
import "./SolutionSection.css"

export const SolutionSection = () => {
  const t = useTranslation("landing")

  const steps = [
    {
      id: "01",
      icon: <Calendar size={22} aria-hidden="true" />,
      title: t.solution.step1.title,
      desc: t.solution.step1.desc,
      benefit: t.solution.step1.benefit,
      example: t.solution.step1.example,
    },
    {
      id: "02",
      icon: <MessageCircle size={22} aria-hidden="true" />,
      title: t.solution.step2.title,
      desc: t.solution.step2.desc,
      benefit: t.solution.step2.benefit,
      example: t.solution.step2.example,
    },
    {
      id: "03",
      icon: <Sparkles size={22} aria-hidden="true" />,
      title: t.solution.step3.title,
      desc: t.solution.step3.desc,
      benefit: t.solution.step3.benefit,
      example: t.solution.step3.example,
    },
  ]

  return (
    <section id="how-it-works" className="solution-section" aria-labelledby="solution-title">
      <div className="solution-section__heading">
        <span className="solution-section__eyebrow">{t.solution.eyebrow}</span>
        <h2 id="solution-title">{t.solution.title}</h2>
        <p>{t.solution.subtitle}</p>
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

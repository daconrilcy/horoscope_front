import { useEffect, useRef, useState } from "react"
import { Calendar, MessageCircle, Sparkles } from "lucide-react"
import { useTranslation } from "../../../i18n"
import "./SolutionSection.css"

export const SolutionSection = () => {
  const t = useTranslation("landing")
  const containerRef = useRef<HTMLDivElement>(null)
  const [visibleSteps, setVisibleItems] = useState<Set<number>>(new Set())

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const stepId = Number(entry.target.getAttribute("data-step-id"))
            if (!isNaN(stepId)) {
              setVisibleItems((prev) => new Set([...prev, stepId]))
              observer.unobserve(entry.target)
            }
          }
        })
      },
      { threshold: 0.2 }
    )

    const cards = containerRef.current?.querySelectorAll(".solution-card")
    cards?.forEach((card) => observer.observe(card))

    return () => observer.disconnect()
  }, [])

  const steps = [
    {
      id: 1,
      number: "01",
      icon: <Calendar size={24} />,
      title: t.solution.step1.title,
      desc: t.solution.step1.desc,
      benefit: t.solution.step1.benefit,
      delay: "0ms"
    },
    {
      id: 2,
      number: "02",
      icon: <MessageCircle size={24} />,
      title: t.solution.step2.title,
      desc: t.solution.step2.desc,
      benefit: t.solution.step2.benefit,
      delay: "150ms"
    },
    {
      id: 3,
      number: "03",
      icon: <Sparkles size={24} />,
      title: t.solution.step3.title,
      desc: t.solution.step3.desc,
      benefit: t.solution.step3.benefit,
      delay: "300ms"
    }
  ]

  return (
    <section id="how-it-works" className="solution-section">
      <h2>{t.solution.title}</h2>

      <div className="solution-container" ref={containerRef}>
        <div className="solution-connector solution-connector--1"></div>
        <div className="solution-connector solution-connector--2"></div>

        {steps.map((step) => (
          <div 
            key={step.id}
            data-step-id={step.id}
            className={`solution-card ${visibleSteps.has(step.id) ? "solution-card--visible" : ""}`}
            style={{ transitionDelay: visibleSteps.has(step.id) ? step.delay : "0ms" }}
          >
            <div className="solution-step-number">{step.number}</div>
            <div className="solution-card-icon">{step.icon}</div>
            
            <div className="solution-card-content">
              <h3>{step.title}</h3>
              <p>{step.desc}</p>
            </div>

            <div className="solution-benefit-badge">
              {step.benefit}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

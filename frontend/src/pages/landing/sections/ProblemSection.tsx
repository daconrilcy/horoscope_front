import { useEffect, useRef, useState } from "react"
import { XCircle, CheckCircle2, AlertCircle, Sparkles } from "lucide-react"
import { useTranslation } from "../../../i18n"
import "./ProblemSection.css"

export const ProblemSection = () => {
  const t = useTranslation("landing")
  const containerRef = useRef<HTMLDivElement>(null)
  const [visibleItems, setVisibleItems] = useState<Set<string>>(new Set())

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const itemId = entry.target.getAttribute("data-item-id")
            if (itemId) {
              // Add a small delay based on index if we wanted, 
              // but here we observe each item individually for true cascading on scroll
              setVisibleItems((prev) => new Set([...prev, itemId]))
              observer.unobserve(entry.target)
            }
          }
        })
      },
      { threshold: 0.2, rootMargin: "0px 0px -50px 0px" }
    )

    const items = containerRef.current?.querySelectorAll(".problem-item")
    items?.forEach((item) => observer.observe(item))

    return () => observer.disconnect()
  }, [])

  const beforeItems = [
    { id: "before-1", text: t.problem.before.item1, icon: <XCircle size={22} /> },
    { id: "before-2", text: t.problem.before.item2, icon: <XCircle size={22} /> },
    { id: "before-3", text: t.problem.before.item3, icon: <XCircle size={22} /> },
  ]

  const afterItems = [
    { id: "after-1", text: t.problem.after.item1, icon: <CheckCircle2 size={22} /> },
    { id: "after-2", text: t.problem.after.item2, icon: <CheckCircle2 size={22} /> },
    { id: "after-3", text: t.problem.after.item3, icon: <CheckCircle2 size={22} /> },
  ]

  return (
    <section id="problem" className="problem-section" aria-labelledby="problem-title">
      <h2 id="problem-title">{t.problem.title}</h2>

      <div className="problem-container" ref={containerRef}>
        {/* Before Column */}
        <div className="problem-column problem-column--before">
          <h3 className="problem-column-title">
            <AlertCircle size={24} aria-hidden="true" />
            {t.problem.before.title}
          </h3>
          
          <ul className="problem-list">
            {beforeItems.map((item) => (
              <li 
                key={item.id} 
                data-item-id={item.id}
                className={`problem-item ${visibleItems.has(item.id) ? "problem-item--visible" : ""}`}
              >
                <div className="problem-item-icon" aria-hidden="true">{item.icon}</div>
                <div className="problem-item-text">{item.text}</div>
              </li>
            ))}
          </ul>
        </div>

        {/* After Column */}
        <div className="problem-column problem-column--after">
          <h3 className="problem-column-title">
            <Sparkles size={24} aria-hidden="true" />
            {t.problem.after.title}
          </h3>

          <ul className="problem-list">
            {afterItems.map((item) => (
              <li 
                key={item.id} 
                data-item-id={item.id}
                className={`problem-item ${visibleItems.has(item.id) ? "problem-item--visible" : ""}`}
              >
                <div className="problem-item-icon" aria-hidden="true">{item.icon}</div>
                <div className="problem-item-text">{item.text}</div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}

// Composant de guide natal replié avec le même patron d'interaction que les lectures.
import { useId, useState } from "react"

import type { AstrologyLang } from "../i18n/astrology"
import { getGuideTranslations } from "../i18n/natalChart"

interface NatalChartGuideProps {
  lang: AstrologyLang
  missingBirthTime: boolean
}

/** Affiche le guide de lecture du thème natal dans un panneau accessible et contrôlé. */
export function NatalChartGuide({ lang, missingBirthTime }: NatalChartGuideProps) {
  const g = getGuideTranslations(lang)
  const contentId = useId()
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <section className="app-card natal-chart-guide" aria-labelledby={`${contentId}-title`}>
      <div className="natal-chart-guide__header">
        <h2 className="natal-chart-guide__title" id={`${contentId}-title`}>
          {g.title}
        </h2>
        <button
          aria-controls={contentId}
          aria-expanded={isExpanded}
          className="natal-reading__chapter-toggle natal-chart-guide__toggle"
          type="button"
          onClick={() => setIsExpanded((current) => !current)}
        >
          {isExpanded ? "Réduire le guide" : "Lire le guide"}
        </button>
      </div>
      <div
        aria-hidden={!isExpanded}
        className={[
          "natal-chart-guide__content",
          isExpanded ? "natal-chart-guide__content--expanded" : "natal-chart-guide__content--collapsed",
        ].join(" ")}
        hidden={!isExpanded}
        id={contentId}
      >
        <p className="natal-chart-guide__intro">{g.intro}</p>

        <section className="natal-chart-guide__section">
          <h3>{g.signsTitle}</h3>
          <p>{g.signsDesc}</p>
          <p>
            <code>{g.signExample}</code>
          </p>
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.planetsTitle}</h3>
          <p>{g.planetsDesc}</p>
          <p>{g.planetsRetrogradeTip}</p>
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.housesTitle}</h3>
          <p>
            <strong>{g.housesIntervalTitle}</strong>
          </p>
          <p>{g.housesIntervalDesc}</p>
          <p>
            <strong>{g.wrapTitle}</strong>
          </p>
          <p>{g.wrapDesc}</p>
          <p>
            <code>{g.wrapExample}</code>
          </p>
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.anglesTitle}</h3>
          <p>{g.anglesDesc}</p>
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.sunAscendantTitle}</h3>
          <p>{g.sunAscendantDesc}</p>
          {missingBirthTime && (
            <p className="natal-chart-guide__missing-time" role="note">
              {g.ascendantMissing}
            </p>
          )}
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.aspectsTitle}</h3>
          <p>{g.aspectsDesc}</p>
        </section>

        <section className="natal-chart-guide__section natal-chart-guide__faq">
          <h3>{g.faqTitle}</h3>
          <dl>
            {g.faq.map((item, idx) => (
              <div key={`${idx}-${item.question}`} className="natal-chart-guide__faq-item">
                <dt>{item.question}</dt>
                <dd>{item.answer}</dd>
              </div>
            ))}
          </dl>
        </section>
      </div>
    </section>
  )
}

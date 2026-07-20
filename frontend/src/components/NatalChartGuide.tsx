// Composant de guide natal replié avec le même patron d'interaction que les lectures.
import { useEffect, useId, useState } from "react"

import { EditorialText } from "./ui/EditorialText/EditorialText"
import type { AstrologyLang } from "../i18n/astrology"
import { getGuideTranslations, type NatalChartGuideTranslations } from "../i18n/natalChart"
import "./NatalChartGuide.css"

interface NatalChartGuideProps {
  expandRequestId?: number
  lang: AstrologyLang
  partialReading: boolean
}

interface NatalGuideCardGridProps {
  cards: NatalChartGuideTranslations["formulaCards"]
  variant: "formula" | "interpretation"
}

/** Rend une grille de cartes pédagogiques avec une structure éditoriale unique. */
function NatalGuideCardGrid({ cards, variant }: NatalGuideCardGridProps) {
  return (
    <div className={`natal-chart-guide__card-grid natal-chart-guide__card-grid--${variant}`}>
      {cards.map((card) => (
        <article className="natal-chart-guide__card" key={`${card.cue}-${card.title}`}>
          <span className="natal-chart-guide__cue">{card.cue}</span>
          <h4>{card.title}</h4>
          <p>
            <EditorialText text={card.description} />
          </p>
          <p className="natal-chart-guide__example">
            <EditorialText text={card.example} />
          </p>
        </article>
      ))}
    </div>
  )
}

/** Affiche le guide de lecture du thème natal dans un panneau accessible et contrôlé. */
export function NatalChartGuide({ expandRequestId = 0, lang, partialReading }: NatalChartGuideProps) {
  const g = getGuideTranslations(lang)
  const contentId = useId()
  const [isExpanded, setIsExpanded] = useState(false)

  useEffect(() => {
    if (expandRequestId > 0) setIsExpanded(true)
  }, [expandRequestId])

  return (
    <section className="app-card natal-chart-guide" aria-labelledby={`${contentId}-title`}>
      <div className="natal-chart-guide__header">
        <h2 className="natal-chart-guide__title" id={`${contentId}-title`}>
          {g.title}
        </h2>
        <button
          aria-controls={contentId}
          aria-expanded={isExpanded}
          className="natal-chart-guide__toggle"
          type="button"
          onClick={() => setIsExpanded((current) => !current)}
        >
          {isExpanded ? g.closeLabel : g.openLabel}
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
        <p className="natal-chart-guide__intro">
          <EditorialText text={g.intro} />
        </p>

        <aside className="natal-chart-guide__takeaway">
          <span className="natal-chart-guide__eyebrow">{g.takeawayLabel}</span>
          <p>
            <EditorialText text={g.takeaway} />
          </p>
        </aside>

        <section className="natal-chart-guide__section" aria-labelledby={`${contentId}-formula-title`}>
          <div className="natal-chart-guide__section-heading">
            <h3 id={`${contentId}-formula-title`}>{g.formulaTitle}</h3>
            <p>
              <EditorialText text={g.formulaIntro} />
            </p>
          </div>
          <NatalGuideCardGrid cards={g.formulaCards} variant="formula" />
        </section>

        <section className="natal-chart-guide__markers" aria-labelledby={`${contentId}-markers-title`}>
          <div className="natal-chart-guide__markers-symbols" aria-hidden="true">
            <span>☉</span>
            <span>☾</span>
            <span>ASC</span>
          </div>
          <div>
            <h3 id={`${contentId}-markers-title`}>{g.firstMarkersTitle}</h3>
            <p>
              <EditorialText text={g.firstMarkersDescription} />
            </p>
          </div>
          {partialReading && (
            <p className="natal-chart-guide__missing-time" role="note">
              <EditorialText text={g.partialReadingNote} />
            </p>
          )}
        </section>

        <section className="natal-chart-guide__section" aria-labelledby={`${contentId}-path-title`}>
          <h3 id={`${contentId}-path-title`}>{g.readingPathTitle}</h3>
          <ol className="natal-chart-guide__path">
            {g.readingPath.map((step, index) => (
              <li key={step.title}>
                <span className="natal-chart-guide__step-index" aria-hidden="true">
                  {index + 1}
                </span>
                <div>
                  <h4>{step.title}</h4>
                  <p>
                    <EditorialText text={step.description} />
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section className="natal-chart-guide__section" aria-labelledby={`${contentId}-interpretation-title`}>
          <h3 id={`${contentId}-interpretation-title`}>{g.interpretationTitle}</h3>
          <NatalGuideCardGrid cards={g.interpretationCards} variant="interpretation" />
        </section>

        <div className="natal-chart-guide__insights">
          <section className="natal-chart-guide__insight" aria-labelledby={`${contentId}-aspects-title`}>
            <h3 id={`${contentId}-aspects-title`}>{g.aspectsTitle}</h3>
            <p>
              <EditorialText text={g.aspectsDescription} />
            </p>
            <p className="natal-chart-guide__example">
              <EditorialText text={g.aspectsExample} />
            </p>
          </section>
          <section className="natal-chart-guide__insight" aria-labelledby={`${contentId}-confidence-title`}>
            <h3 id={`${contentId}-confidence-title`}>{g.confidenceTitle}</h3>
            <p>
              <EditorialText text={g.confidenceDescription} />
            </p>
          </section>
        </div>

        <section
          className="natal-chart-guide__section natal-chart-guide__glossary"
          aria-labelledby={`${contentId}-glossary-title`}
        >
          <h3 id={`${contentId}-glossary-title`}>{g.glossaryTitle}</h3>
          <dl>
            {g.glossary.map((item) => (
              <div key={item.term} className="natal-chart-guide__glossary-item">
                <dt>{item.term}</dt>
                <dd>
                  <EditorialText text={item.definition} />
                </dd>
              </div>
            ))}
          </dl>
        </section>

        <p className="natal-chart-guide__closing-tip">
          <EditorialText text={g.closingTip} />
        </p>
      </div>
    </section>
  )
}

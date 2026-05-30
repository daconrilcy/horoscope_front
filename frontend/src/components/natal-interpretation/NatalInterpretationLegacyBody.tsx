// Corps d'interpretation legacy (sections, points cles, conseils) hors contrat narratif v1.
import { useState } from "react"
import { ChevronDown, Star } from "lucide-react"

import { natalChartTranslations } from "../../i18n/natalChart"
import { EvidenceTags } from "./NatalInterpretationEvidence"
import type { NatalInterpretationLocale, NatalInterpretationViewData } from "./NatalInterpretationTypes"

type Props = {
  interpretation: NatalInterpretationViewData["interpretation"]
  lang: NatalInterpretationLocale
}

function hasLegacyBodyContent(interpretation: NatalInterpretationViewData["interpretation"]): boolean {
  return (
    (interpretation.sections?.length ?? 0) > 0 ||
    (interpretation.highlights?.length ?? 0) > 0 ||
    (interpretation.advice?.length ?? 0) > 0
  )
}

export function hasRenderableLegacyInterpretationBody(
  interpretation: NatalInterpretationViewData["interpretation"],
): boolean {
  return hasLegacyBodyContent(interpretation)
}

export function NatalInterpretationLegacyBody({ interpretation, lang }: Props) {
  const t = natalChartTranslations[lang].interpretation
  const sections = interpretation.sections ?? []
  const highlights = interpretation.highlights ?? []
  const advice = interpretation.advice ?? []
  const evidence = interpretation.evidence ?? []
  const [openSectionKey, setOpenSectionKey] = useState<string | null>(
    sections.length === 1 ? sections[0].key : null,
  )

  if (!hasLegacyBodyContent(interpretation)) {
    return null
  }

  return (
    <>
      {sections.length > 0 && (
        <div className="ni-accordion" role="region" aria-label={t.title}>
          {sections.map((section) => {
            const isOpen = openSectionKey === section.key
            return (
              <div key={section.key} className="ni-accordion-item">
                <button
                  type="button"
                  className="ni-accordion-header"
                  aria-expanded={isOpen}
                  onClick={() =>
                    setOpenSectionKey((current) => (current === section.key ? null : section.key))
                  }
                >
                  <span className="ni-accordion-title">{section.heading || section.key}</span>
                  <ChevronDown
                    size={18}
                    className={`ni-accordion-icon${isOpen ? " ni-accordion-icon--open" : " ni-accordion-icon--closed"}`}
                  />
                </button>
                {isOpen && (
                  <div className="ni-accordion-body">
                    <p className="ni-accordion-text">{section.content}</p>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {highlights.length > 0 && (
        <section aria-labelledby="ni-highlights-title">
          <h4 id="ni-highlights-title" className="ni-section-label ni-section-label--card">
            {t.highlightsTitle}
          </h4>
          <div className="ni-highlights">
            {highlights.map((highlight, index) => (
              <article key={`${highlight}-${index}`} className="ni-highlight-chip">
                <span className="ni-highlight-icon" aria-hidden="true">
                  <Star size={16} className="ni-highlight-star" />
                </span>
                <p className="ni-highlight-text">{highlight}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {advice.length > 0 && (
        <section className="ni-advice-block" aria-labelledby="ni-advice-title">
          <h4 id="ni-advice-title" className="ni-advice-title">
            {t.adviceTitle}
          </h4>
          <ul className="ni-advice-list">
            {advice.map((item, index) => (
              <li key={`${item}-${index}`} className="ni-advice-item">
                <span className="ni-advice-icon" aria-hidden="true">
                  <Star size={12} className="ni-advice-star" />
                </span>
                <p className="ni-advice-text">{item}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {evidence.length > 0 && (
        <EvidenceTags evidence={evidence} title={t.evidenceTitle} t={t} />
      )}
    </>
  )
}

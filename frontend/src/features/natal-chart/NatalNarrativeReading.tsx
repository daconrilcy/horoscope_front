// Lecture narrative publique: cinq chapitres en accordeons accessibles (narrative_natal_reading_v1).
import { useId, useState } from "react"
import { ChevronDown } from "lucide-react"

import type { NarrativeNatalReadingV1 } from "../../api/natal-chart"
import type { PublicCopyLang } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"
import "./NatalNarrativeReading.css"

type NatalNarrativeReadingProps = {
  reading: NarrativeNatalReadingV1
  lang: PublicCopyLang
}

function chapterPreview(narrative: string, maxLength = 140): string {
  const collapsed = narrative.replace(/\s+/g, " ").trim()
  if (collapsed.length <= maxLength) {
    return collapsed
  }
  return `${collapsed.slice(0, maxLength).trimEnd()}…`
}

/** Affiche les cinq chapitres narratifs avec divulgation progressive accessible. */
export function NatalNarrativeReading({ reading, lang }: NatalNarrativeReadingProps) {
  const copy = getNatalPublicCopy(lang).narrativeReading
  const chapters = [...reading.chapters].sort(
    (left, right) =>
      copy.chapterOrder.indexOf(left.key) - copy.chapterOrder.indexOf(right.key),
  )
  const [expandedKeys, setExpandedKeys] = useState<Set<string>>(() => {
    const firstKey = chapters[0]?.key
    return firstKey ? new Set([firstKey]) : new Set()
  })
  const sectionId = useId()

  const toggleChapter = (chapterKey: string) => {
    setExpandedKeys((current) => {
      const next = new Set(current)
      if (next.has(chapterKey)) {
        next.delete(chapterKey)
      } else {
        next.add(chapterKey)
      }
      return next
    })
  }

  return (
    <section className="natal-narrative-reading" aria-labelledby="natal-narrative-reading-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.eyebrow}</span>
        <h2 id="natal-narrative-reading-title">{copy.title}</h2>
      </div>
      <ol className="natal-narrative-reading__chapters">
        {chapters.map((chapter) => {
          const isExpanded = expandedKeys.has(chapter.key)
          const buttonId = `${sectionId}-${chapter.key}-toggle`
          const panelId = `${sectionId}-${chapter.key}-panel`
          return (
            <li key={chapter.key} className="natal-narrative-reading__chapter">
              <article
                className={
                  isExpanded
                    ? "natal-narrative-reading__card is-expanded"
                    : "natal-narrative-reading__card"
                }
              >
                <h3 className="natal-narrative-reading__chapter-heading">
                  <button
                    id={buttonId}
                    type="button"
                    className="natal-narrative-reading__toggle"
                    aria-expanded={isExpanded}
                    aria-controls={panelId}
                    onClick={() => toggleChapter(chapter.key)}
                  >
                    <span className="natal-narrative-reading__toggle-label">
                      <span className="natal-narrative-reading__toggle-title">{chapter.title}</span>
                      {!isExpanded ? (
                        <span className="natal-narrative-reading__preview">
                          {chapterPreview(chapter.narrative)}
                        </span>
                      ) : null}
                    </span>
                    <ChevronDown
                      size={18}
                      className={
                        isExpanded
                          ? "natal-narrative-reading__chevron is-open"
                          : "natal-narrative-reading__chevron"
                      }
                      aria-hidden="true"
                    />
                  </button>
                </h3>
                <div
                  id={panelId}
                  role="region"
                  aria-labelledby={buttonId}
                  className={
                    isExpanded
                      ? "natal-narrative-reading__panel"
                      : "natal-narrative-reading__panel is-collapsed"
                  }
                  hidden={!isExpanded}
                >
                  <p className="natal-narrative-reading__body">{chapter.narrative}</p>
                  {chapter.key_points.length > 0 ? (
                    <ul className="natal-narrative-reading__points">
                      {chapter.key_points.map((point) => (
                        <li key={point}>{point}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              </article>
            </li>
          )
        })}
      </ol>
    </section>
  )
}

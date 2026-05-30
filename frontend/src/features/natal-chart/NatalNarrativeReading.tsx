// Lecture narrative publique: cinq chapitres du contrat narrative_natal_reading_v1.
import type { NarrativeNatalReadingV1 } from "../../api/natal-chart"
import type { PublicCopyLang } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"
import "./NatalNarrativeReading.css"

type NatalNarrativeReadingProps = {
  reading: NarrativeNatalReadingV1
  lang: PublicCopyLang
}

/** Affiche les cinq chapitres narratifs dans l'ordre produit attendu. */
export function NatalNarrativeReading({ reading, lang }: NatalNarrativeReadingProps) {
  const copy = getNatalPublicCopy(lang).narrativeReading
  const chapters = [...reading.chapters].sort(
    (left, right) =>
      copy.chapterOrder.indexOf(left.key) - copy.chapterOrder.indexOf(right.key),
  )

  return (
    <section className="natal-narrative-reading" aria-labelledby="natal-narrative-reading-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.eyebrow}</span>
        <h2 id="natal-narrative-reading-title">{copy.title}</h2>
      </div>
      <ol className="natal-narrative-reading__chapters">
        {chapters.map((chapter) => (
          <li key={chapter.key} className="natal-narrative-reading__chapter">
            <article className="natal-narrative-reading__card">
              <h3>{chapter.title}</h3>
              <p className="natal-narrative-reading__body">{chapter.narrative}</p>
              {chapter.key_points.length > 0 ? (
                <ul className="natal-narrative-reading__points">
                  {chapter.key_points.map((point) => (
                    <li key={point}>{point}</li>
                  ))}
                </ul>
              ) : null}
            </article>
          </li>
        ))}
      </ol>
    </section>
  )
}

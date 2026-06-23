// Composant public d'affichage de l'interpretation natale Astral normalisee.
import { Link } from "react-router-dom"

import type { NatalInterpretationViewModel } from "./natalAstralReadingViewModel"

type NatalAstralReadingProps = {
  reading: NatalInterpretationViewModel
}

function renderStatusMeta(reading: NatalInterpretationViewModel): string {
  const meta = [reading.label]
  if (reading.completeness === "partial") meta.push("completude partielle")
  return meta.join(" - ")
}

/** Affiche la lecture Astral sans exposer les champs techniques du moteur externe. */
export function NatalAstralReading({ reading }: NatalAstralReadingProps) {
  if (reading.status === "failed" || reading.status === "safety_rejected") {
    return (
      <article className="natal-reading natal-reading--error" aria-label="Erreur de lecture Astral">
        <header className="natal-reading__header">
          <span className="natal-section-eyebrow">{reading.label}</span>
          <h2>{reading.title}</h2>
        </header>
        <div className="chat-error natal-card__error" role="alert">
          <p>{reading.error?.message ?? "La lecture Astral n'a pas pu etre generee."}</p>
          {reading.error?.code ? <p>Code: {reading.error.code}</p> : null}
          {reading.error?.ruleId ? <p>Regle: {reading.error.ruleId}</p> : null}
          <Link to="/profile" className="btn-link natal-card__secondary-link">
            Verifier mon profil de naissance
          </Link>
        </div>
      </article>
    )
  }

  return (
    <article className="natal-reading" aria-label="Lecture Astral du theme natal">
      <header className="natal-reading__header">
        <span className="natal-section-eyebrow">Lecture Astral</span>
        <div className="natal-reading__summary">
          <h2>{reading.title}</h2>
          <span className="natal-reading__badge">{renderStatusMeta(reading)}</span>
        </div>
        {reading.shortText ? <p>{reading.shortText}</p> : null}
      </header>

      {reading.isPartial ? (
        <p className="natal-reading__precision-note" role="status">
          Lecture indicative : sans heure de naissance fiable, l'ascendant, les maisons et certains angles peuvent etre
          absents.
        </p>
      ) : null}

      {reading.chapters.length > 0 ? (
        <div className="natal-reading__chapters">
          {reading.chapters.map((chapter, index) => (
            <section className="natal-reading__chapter" key={`${chapter.code ?? chapter.title}-${index}`}>
              <div className="natal-reading__chapter-head">
                <h3>{chapter.title}</h3>
                {chapter.confidenceLabel ? <span>{chapter.confidenceLabel}</span> : null}
              </div>
              {chapter.paragraphs.length > 0 ? (
                <div className="natal-reading__chapter-body">
                  {chapter.paragraphs.map((paragraph, paragraphIndex) => (
                    <p key={`${chapter.code ?? chapter.title}-paragraph-${paragraphIndex}`}>{paragraph}</p>
                  ))}
                </div>
              ) : null}
              {chapter.astroBasis.length > 0 ? (
                <div className="natal-reading__basis" aria-label={`Reperes utilises pour ${chapter.title}`}>
                  <span>Reperes utilises</span>
                  <ul>
                    {chapter.astroBasis.map((basis, basisIndex) => (
                      <li key={`${chapter.code ?? chapter.title}-basis-${basisIndex}`}>{basis}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {chapter.safetyFlags.length > 0 ? (
                <p className="natal-reading__safety">Note de prudence : {chapter.safetyFlags.join(", ")}</p>
              ) : null}
            </section>
          ))}
        </div>
      ) : (
        <p className="natal-card__lead">La lecture est disponible mais ne contient pas encore de chapitres publics.</p>
      )}

      {reading.disclaimer ? <p className="natal-reading__disclaimer">{reading.disclaimer}</p> : null}
    </article>
  )
}

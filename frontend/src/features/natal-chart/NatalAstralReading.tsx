// Composant public d'affichage de l'interprétation natale Astral normalisée.
import { Link } from "react-router-dom"

import type {
  NatalCalculationFactsViewModel,
  NatalInterpretationViewModel,
} from "./natalAstralReadingViewModel"

type NatalAstralReadingProps = {
  reading: NatalInterpretationViewModel
}

const PUBLIC_READING_ERROR_MESSAGE =
  "La lecture Astral n'a pas pu être générée pour le moment. Veuillez réessayer plus tard."

const GROUP_MARKERS: Record<string, string> = {
  "Repères principaux": "☉",
  Maisons: "⌂",
  "Planètes notables": "✦",
  "Aspects notables": "△",
}

function markerForGroup(title: string): string {
  return GROUP_MARKERS[title] ?? "✧"
}

function NatalCalculationFacts({ facts }: { facts: NatalCalculationFactsViewModel }) {
  return (
    <section className="natal-reading-facts" aria-labelledby="natal-reading-facts-title">
      <div className="natal-reading-facts__header">
        <h2 id="natal-reading-facts-title">Base du calcul natal</h2>
      </div>
      <div className="natal-reading-facts__grid">
        {facts.groups.map((group) => (
          <section className="natal-reading-facts__group" key={group.title} aria-label={group.title}>
            <div className="natal-reading-facts__group-head">
              <span className="natal-reading-facts__marker" aria-hidden="true">
                {markerForGroup(group.title)}
              </span>
              <h3>{group.title}</h3>
            </div>
            <dl className="natal-reading-facts__list">
              {group.items.map((item) => (
                <div className="natal-reading-facts__item" key={`${group.title}-${item.label}-${item.value}`}>
                  <dt>{item.label}</dt>
                  <dd>
                    <span className="natal-chip natal-chip--value">
                      <strong>{item.value}</strong>
                    </span>
                    {item.detail ? <span className="natal-chip natal-chip--detail">{item.detail}</span> : null}
                  </dd>
                </div>
              ))}
            </dl>
          </section>
        ))}
      </div>
    </section>
  )
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
          <p>{PUBLIC_READING_ERROR_MESSAGE}</p>
          <Link to="/profile" className="btn-link natal-card__secondary-link">
            Vérifier mon profil de naissance
          </Link>
        </div>
      </article>
    )
  }

  return (
    <article className="natal-reading" aria-label="Interprétation de votre thème natal">
      {reading.calculationFacts ? <NatalCalculationFacts facts={reading.calculationFacts} /> : null}

      <header className="natal-reading__header">
        <span className="natal-section-eyebrow">Interprétation de votre thème natal</span>
        <div className="natal-reading__summary">
          <h2>{reading.title}</h2>
          <span className="natal-reading__badge">{reading.label}</span>
        </div>
        {reading.shortText ? <p>{reading.shortText}</p> : null}
      </header>

      {reading.isPartial ? (
        <p className="natal-reading__precision-note natal-reading__partial-alert" role="alert">
          Thème partiel : certaines données de naissance manquent ou ne sont pas assez fiables. L'ascendant, les
          maisons et certains angles peuvent être absents ou limités.
        </p>
      ) : null}

      {reading.chapters.length > 0 ? (
        <div className="natal-reading__chapters">
          {reading.chapters.map((chapter, index) => (
            <section className="natal-reading__chapter" key={`${chapter.code ?? chapter.title}-${index}`}>
              <div className="natal-reading__chapter-head">
                <h3>{chapter.title}</h3>
                {chapter.confidenceLabel ? (
                  <span className="natal-reading__confidence">{chapter.confidenceLabel}</span>
                ) : null}
              </div>
              {chapter.paragraphs.length > 0 ? (
                <div className="natal-reading__chapter-body">
                  {chapter.paragraphs.map((paragraph, paragraphIndex) => (
                    <p key={`${chapter.code ?? chapter.title}-paragraph-${paragraphIndex}`}>{paragraph}</p>
                  ))}
                </div>
              ) : null}
              {chapter.astroBasis.length > 0 ? (
                <div className="natal-reading__basis" aria-label={`Repères utilisés pour ${chapter.title}`}>
                  <span>Repères utilisés</span>
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

// Composant public d'affichage de l'interprétation natale Astral normalisée.
import { Link } from "react-router-dom"

import type {
  NatalCalculationFactsViewModel,
  NatalInterpretationViewModel,
  NatalReadingChapterViewModel,
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
        <span className="natal-section-eyebrow">{facts.sourceLabel}</span>
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

function NatalChapterCard({ chapter, itemKey }: { chapter: NatalReadingChapterViewModel; itemKey: string }) {
  return (
    <section className="natal-reading__chapter">
      <div className="natal-reading__chapter-head">
        <h3>{chapter.title}</h3>
        {chapter.confidenceLabel ? (
          <span className="natal-reading__confidence">{chapter.confidenceLabel}</span>
        ) : null}
      </div>
      {chapter.paragraphs.length > 0 ? (
        <div className="natal-reading__chapter-body">
          {chapter.paragraphs.map((paragraph, paragraphIndex) => (
            <p key={`${itemKey}-paragraph-${paragraphIndex}`}>{paragraph}</p>
          ))}
        </div>
      ) : null}
      {chapter.astroBasis.length > 0 ? (
        <div className="natal-reading__basis" aria-label={`Repères utilisés pour ${chapter.title}`}>
          <span>Repères utilisés</span>
          <ul>
            {chapter.astroBasis.map((basis, basisIndex) => (
              <li className="natal-chip natal-chip--basis natal-chip--compact" key={`${itemKey}-basis-${basisIndex}`}>
                {basis}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {chapter.safetyFlags.length > 0 ? (
        <p className="natal-reading__safety">Note de prudence : {chapter.safetyFlags.join(", ")}</p>
      ) : null}
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
            <NatalChapterCard
              chapter={chapter}
              itemKey={`chapter-${chapter.code ?? chapter.title}-${index}`}
              key={`${chapter.code ?? chapter.title}-${index}`}
            />
          ))}
        </div>
      ) : reading.explanations.length === 0 ? (
        <p className="natal-card__lead">La lecture est disponible mais ne contient pas encore de chapitres publics.</p>
      ) : null}

      {reading.explanations.length > 0 ? (
        <section className="natal-reading-explanations" aria-labelledby="natal-reading-explanations-title">
          <div className="natal-reading-explanations__header">
            <span className="natal-section-eyebrow">Repères calculés</span>
            <h2 id="natal-reading-explanations-title">Explications du moteur Astral</h2>
          </div>
          <div className="natal-reading-explanations__grid">
            {reading.explanations.map((chapter, index) => (
              <NatalChapterCard
                chapter={chapter}
                itemKey={`explanation-${chapter.code ?? chapter.title}-${index}`}
                key={`explanation-${chapter.code ?? chapter.title}-${index}`}
              />
            ))}
          </div>
        </section>
      ) : null}

      {reading.disclaimer ? <p className="natal-reading__disclaimer">{reading.disclaimer}</p> : null}
    </article>
  )
}

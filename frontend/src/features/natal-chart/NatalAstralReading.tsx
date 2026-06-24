// Composant public d'affichage de l'interpretation natale Astral normalisee.
import { Link } from "react-router-dom"

import type {
  NatalCalculationReadingViewModel,
  NatalReadingAspectViewModel,
  NatalReadingAxisViewModel,
  NatalReadingLifeAreaViewModel,
  NatalReadingOtherForceViewModel,
  NatalReadingPillarViewModel,
  NatalReadingSummaryCardViewModel,
  NatalInterpretationViewModel,
} from "./natalAstralReadingViewModel"

type NatalAstralReadingProps = {
  reading: NatalInterpretationViewModel
}

const PUBLIC_READING_ERROR_MESSAGE =
  "La lecture Astral n'a pas pu etre generee pour le moment. Veuillez reessayer plus tard."

function NatalSummary({ cards }: { cards: NatalReadingSummaryCardViewModel[] }) {
  if (cards.length === 0) return null
  return (
    <section className="natal-summary" aria-labelledby="natal-summary-title">
      <p className="natal-section-eyebrow">Synthese rapide</p>
      <h2 id="natal-summary-title">Les grands reperes de votre carte</h2>
      <div className="natal-summary__cards">
        {cards.map((card) => (
          <article className="natal-summary-card" key={`${card.label}-${card.title}`}>
            <span className="natal-summary-card__label">{card.label}</span>
            <strong>{card.title}</strong>
            <p>{card.description}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

function NatalPillars({ pillars }: { pillars: NatalReadingPillarViewModel[] }) {
  if (pillars.length === 0) return null
  return (
    <section className="natal-reading-block" aria-labelledby="natal-pillars-title">
      <h3 id="natal-pillars-title">Vos 3 grands piliers astrologiques</h3>
      <p className="natal-reading-block__intro">
        Ces trois elements donnent une premiere lecture simple de votre theme : identite, vie interieure et maniere
        d'entrer en relation avec l'exterieur.
      </p>
      <div className="natal-pillars">
        {pillars.map((pillar) => (
          <article className="natal-pillar" key={pillar.code}>
            <span className="natal-pillar__icon">{pillar.icon}</span>
            <div>
              <h4>{pillar.title}</h4>
              <p>{pillar.description}</p>
              {pillar.lifeArea ? <p>{pillar.lifeArea}</p> : null}
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

function NatalAxes({ axes }: { axes: NatalReadingAxisViewModel[] }) {
  if (axes.length === 0) return null
  return (
    <section className="natal-reading-block" aria-labelledby="natal-axes-title">
      <h3 id="natal-axes-title">Les grands axes de votre vie</h3>
      <p className="natal-reading-block__intro">
        Ces quatre reperes decrivent l'equilibre entre vie personnelle, relations, foyer et direction professionnelle.
      </p>
      <div className="natal-axis-grid">
        {axes.map((axis) => (
          <article className="natal-axis-card" key={axis.code}>
            <span className="natal-axis-card__label">{axis.label}</span>
            <h4>{axis.title}</h4>
            <p>{axis.description}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

function NatalLifeAreas({ lifeAreas }: { lifeAreas: NatalReadingLifeAreaViewModel[] }) {
  if (lifeAreas.length === 0) return null
  return (
    <section className="natal-reading-block" aria-labelledby="natal-life-areas-title">
      <h3 id="natal-life-areas-title">Domaines de vie les plus marques</h3>
      <p className="natal-reading-block__intro">
        Les maisons montrent les zones de vie ou les energies du theme s'expriment le plus fortement.
      </p>
      <div className="natal-life-area-list">
        {lifeAreas.map((area) => (
          <article className="natal-life-area-card" key={`${area.rank}-${area.title}`}>
            <div className="natal-life-area-card__header">
              <span className="natal-life-area-card__badge">{area.rank}</span>
              <h4>{area.title}</h4>
            </div>
            <p>{area.description}</p>
            {area.details.length > 0 ? (
              <div className="natal-tags">
                {area.details.map((detail) => (
                  <span key={detail}>{detail}</span>
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  )
}

function NatalOtherForces({ otherForces }: { otherForces: NatalReadingOtherForceViewModel[] }) {
  if (otherForces.length === 0) return null
  return (
    <section className="natal-reading-block" aria-labelledby="natal-other-forces-title">
      <h3 id="natal-other-forces-title">Autres forces importantes du theme</h3>
      <p className="natal-reading-block__intro">
        Ces planetes ajoutent des nuances importantes a la personnalite et aux comportements.
      </p>
      <div className="natal-planet-list">
        {otherForces.map((force) => (
          <article className="natal-planet-card" key={force.title}>
            <h4>{force.title}</h4>
            <p>
              <strong>{force.functionLabel} :</strong> {force.description}
            </p>
            {force.lifeArea ? <p>Expression principale : {force.lifeArea}</p> : null}
          </article>
        ))}
      </div>
    </section>
  )
}

function NatalAspectDynamics({ aspects }: { aspects: NatalReadingAspectViewModel[] }) {
  if (aspects.length === 0) return null
  return (
    <section className="natal-reading-block" aria-labelledby="natal-aspects-title">
      <h3 id="natal-aspects-title">Dynamiques fortes entre les planetes</h3>
      <p className="natal-reading-block__intro">
        Les aspects decrivent les relations entre les planetes : certaines creent de la fluidite, d'autres de la
        tension ou de l'intensite.
      </p>
      <div className="natal-aspect-card-list">
        {aspects.map((aspect) => (
          <article className="natal-aspect-card" key={`${aspect.badge}-${aspect.title}`}>
            <div className="natal-aspect-card__header">
              <span className="natal-aspect-card__badge">{aspect.badge}</span>
              <h4>{aspect.title}</h4>
            </div>
            <p>{aspect.description}</p>
            <details className="natal-technical-details">
              <summary>Details techniques</summary>
              <dl>
                {aspect.details.map((detail) => (
                  <div key={`${aspect.title}-${detail.label}`}>
                    <dt>{detail.label}</dt>
                    <dd>{detail.value}</dd>
                  </div>
                ))}
              </dl>
            </details>
          </article>
        ))}
      </div>
    </section>
  )
}

function NatalRawCalculationDetails({ reading }: { reading: NatalCalculationReadingViewModel }) {
  if (reading.technicalGroups.length === 0) return null
  return (
    <details className="natal-raw-data">
      <summary>Details techniques du calcul</summary>
      <div className="natal-reading-facts__grid">
        {reading.technicalGroups.map((group) => (
          <section className="natal-reading-facts__group" key={group.title} aria-label={group.title}>
            <h4>{group.title}</h4>
            <dl className="natal-reading-facts__list">
              {group.items.map((item) => (
                <div className="natal-reading-facts__item" key={`${group.title}-${item.label}-${item.value}`}>
                  <dt>{item.label}</dt>
                  <dd>
                    <strong>{item.value}</strong>
                    {item.detail ? <span>{item.detail}</span> : null}
                  </dd>
                </div>
              ))}
            </dl>
          </section>
        ))}
      </div>
    </details>
  )
}

function NatalCalculationReading({ reading }: { reading: NatalCalculationReadingViewModel }) {
  return (
    <div className="natal-reading-pedagogy">
      <NatalSummary cards={reading.summaryCards} />
      <NatalPillars pillars={reading.pillars} />
      <NatalAxes axes={reading.axes} />
      <NatalLifeAreas lifeAreas={reading.lifeAreas} />
      <NatalOtherForces otherForces={reading.otherForces} />
      <NatalAspectDynamics aspects={reading.aspects} />
      <NatalRawCalculationDetails reading={reading} />
    </div>
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
            Verifier mon profil de naissance
          </Link>
        </div>
      </article>
    )
  }

  return (
    <article className="natal-reading" aria-label="Interprétation de votre thème natal">
      {reading.calculationReading ? <NatalCalculationReading reading={reading.calculationReading} /> : null}

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
          Theme partiel : certaines donnees de naissance manquent ou ne sont pas assez fiables. L'ascendant, les
          maisons et certains angles peuvent etre absents ou limites.
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

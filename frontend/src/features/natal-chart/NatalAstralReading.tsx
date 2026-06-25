// Composant public d'affichage de l'interpretation natale Astral normalisee.
import { Link } from "react-router-dom"

import type {
  NatalCalculationFactGroupViewModel,
  NatalCalculationFactItemViewModel,
  NatalCalculationReadingViewModel,
  NatalReadingAspectViewModel,
  NatalReadingAxisViewModel,
  NatalReadingExplanationViewModel,
  NatalReadingLifeAreaViewModel,
  NatalReadingOtherForceViewModel,
  NatalReadingPillarViewModel,
  NatalReadingSummaryViewModel,
  NatalInterpretationViewModel,
} from "./natalAstralReadingViewModel"

type NatalAstralReadingProps = {
  reading: NatalInterpretationViewModel
}

const PUBLIC_READING_ERROR_MESSAGE =
  "La lecture Astral n'a pas pu etre generee pour le moment. Veuillez reessayer plus tard."
const PRIMARY_TECHNICAL_FACT_LABELS = new Set(["Soleil", "Lune", "Ascendant"])
const AXIS_TECHNICAL_FACT_LABELS = new Set(["Descendant", "Milieu du Ciel", "Fond du Ciel"])
const TECHNICAL_FACT_SYMBOLS: Record<string, string> = {
  Soleil: "☉",
  Lune: "☽",
  Ascendant: "ASC",
}
const TECHNICAL_GROUP_TITLES = {
  main: "Repères principaux",
  houses: "Maisons",
  planets: "Planètes notables",
  aspects: "Aspects notables",
} as const

function NatalSummary({ summary }: { summary: NatalReadingSummaryViewModel }) {
  return (
    <section className="natal-summary" aria-labelledby="natal-summary-title">
      <p className="natal-section-eyebrow">Vue d'ensemble</p>
      <h2 id="natal-summary-title">Ce qui ressort globalement</h2>
      {summary.text ? <p className="natal-summary__text">{summary.text}</p> : null}
      <div className="natal-summary__highlights">
        {summary.highlights.map((highlight) => (
          <span key={highlight}>{highlight}</span>
        ))}
      </div>
    </section>
  )
}

function NatalExplanations({ explanations }: { explanations: NatalReadingExplanationViewModel[] }) {
  if (explanations.length === 0) return null
  return (
    <section className="natal-reading-block" aria-labelledby="natal-explanations-title">
      <div>
        <h3 id="natal-explanations-title">Explications du calcul</h3>
        <p className="natal-reading-block__intro">
          Les elements ci-dessous reprennent les explications publiques du moteur Astral, sans les identifiants
          techniques internes.
        </p>
      </div>
      <div className="natal-explanation-list">
        {explanations.map((item) => (
          <article className="natal-explanation-card" key={`${item.kindLabel}-${item.title}`}>
            <span className="natal-explanation-card__kind">{item.kindLabel}</span>
            <h4>{item.title}</h4>
            <p>{item.explanation}</p>
            {item.expressionPrimary ? (
              <p className="natal-muted">Expression principale : {item.expressionPrimary}</p>
            ) : null}
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
      <h3 id="natal-pillars-title">Les 3 reperes essentiels</h3>
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
      <h3 id="natal-axes-title">Les grands equilibres du theme</h3>
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
      <h3 id="natal-life-areas-title">Le domaine de vie dominant</h3>
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
      <h3 id="natal-other-forces-title">Forces complementaires</h3>
      <div className="natal-planet-list">
        {otherForces.map((force) => (
          <article className="natal-planet-card" key={force.title}>
            <h4>{force.title}</h4>
            <p>
              <strong>{force.functionLabel} :</strong> {force.description}
            </p>
            {force.lifeArea ? <p className="natal-muted">Expression principale : {force.lifeArea}</p> : null}
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
      <h3 id="natal-aspects-title">Dynamique principale</h3>
      <div className="natal-aspect-card-list">
        {aspects.map((aspect) => (
          <article className="natal-aspect-card" key={`${aspect.badge}-${aspect.title}`}>
            <div className="natal-aspect-card__header">
              <span className="natal-aspect-card__badge">{aspect.badge}</span>
              <h4>{aspect.title}</h4>
            </div>
            <p>{aspect.description}</p>
            {aspect.details.length > 0 ? (
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
            ) : null}
          </article>
        ))}
      </div>
    </section>
  )
}

function findTechnicalGroup(
  groups: NatalCalculationFactGroupViewModel[],
  title: string,
): NatalCalculationFactGroupViewModel | null {
  return groups.find((group) => group.title === title) ?? null
}

function extractHouseRank(label: string): string {
  return label.match(/Maison\s+([IVX]+)/i)?.[1] ?? label
}

function classifyAspectTone(detail: string | null): "flow" | "tension" | "intensity" | "neutral" {
  const normalizedDetail = detail?.toLowerCase() ?? ""
  if (normalizedDetail.includes("fluid")) return "flow"
  if (normalizedDetail.includes("tension")) return "tension"
  if (normalizedDetail.includes("intens")) return "intensity"
  return "neutral"
}

function labelAspectTone(detail: string | null): string {
  const tone = classifyAspectTone(detail)
  if (tone === "flow") return "Ressource"
  if (tone === "tension") return "Tension"
  if (tone === "intensity") return "Intensité"
  return "Relation"
}

function NatalRawCalculationDetails({ reading }: { reading: NatalCalculationReadingViewModel }) {
  if (reading.technicalGroups.length === 0) return null
  const mainGroup = findTechnicalGroup(reading.technicalGroups, TECHNICAL_GROUP_TITLES.main)
  const houseGroup = findTechnicalGroup(reading.technicalGroups, TECHNICAL_GROUP_TITLES.houses)
  const planetGroup = findTechnicalGroup(reading.technicalGroups, TECHNICAL_GROUP_TITLES.planets)
  const aspectGroup = findTechnicalGroup(reading.technicalGroups, TECHNICAL_GROUP_TITLES.aspects)
  const primaryFacts = mainGroup?.items.filter((item) => PRIMARY_TECHNICAL_FACT_LABELS.has(item.label)) ?? []
  const axisFacts = mainGroup?.items.filter((item) => AXIS_TECHNICAL_FACT_LABELS.has(item.label)) ?? []
  const complementaryMainFacts =
    mainGroup?.items.filter(
      (item) => !PRIMARY_TECHNICAL_FACT_LABELS.has(item.label) && !AXIS_TECHNICAL_FACT_LABELS.has(item.label),
    ) ?? []

  return (
    <details className="natal-raw-data" open>
      <summary className="natal-raw-data__summary">
        <span className="natal-raw-data__summary-icon" aria-hidden="true">
          ▾
        </span>
        <span>
          <strong>Détails techniques du calcul</strong>
          <small>Les positions, maisons et aspects utilisés pour produire cette lecture.</small>
        </span>
      </summary>

      <div className="natal-raw-data__body">
        {mainGroup ? (
          <section className="natal-technical-block natal-technical-block--main" aria-label={mainGroup.title}>
            <header className="natal-technical-block__header">
              <div>
                <h4>{mainGroup.title}</h4>
                <p>Les points structurants du thème natal.</p>
              </div>
              <span className="natal-raw-badge natal-raw-badge--primary">Base du calcul</span>
            </header>

            <div className="natal-raw-fact-list">
              {primaryFacts.map((item) => (
                <article className="natal-raw-fact natal-raw-fact--important" key={`${mainGroup.title}-${item.label}`}>
                  <div className="natal-raw-fact__symbol">{TECHNICAL_FACT_SYMBOLS[item.label]}</div>
                  <div className="natal-raw-fact__content">
                    <span className="natal-raw-fact__label">{item.label}</span>
                    <strong>{item.value}</strong>
                    {item.detail ? <small>{item.detail}</small> : null}
                  </div>
                </article>
              ))}
            </div>

            {axisFacts.length > 0 ? (
              <div className="natal-raw-axis-list" aria-label="Axes principaux">
                {axisFacts.map((item) => (
                  <article className="natal-raw-axis" key={`${mainGroup.title}-${item.label}-${item.value}`}>
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                    {item.detail ? <small>{item.detail}</small> : null}
                  </article>
                ))}
              </div>
            ) : null}

            {complementaryMainFacts.length > 0 ? (
              <div className="natal-raw-axis-list" aria-label="Repères complémentaires">
                {complementaryMainFacts.map((item) => (
                  <article className="natal-raw-axis" key={`${mainGroup.title}-${item.label}-${item.value}`}>
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                    {item.detail ? <small>{item.detail}</small> : null}
                  </article>
                ))}
              </div>
            ) : null}
          </section>
        ) : null}

        {houseGroup ? (
          <section className="natal-technical-block natal-technical-block--dominance" aria-label={houseGroup.title}>
            <header className="natal-technical-block__header">
              <div>
                <h4>Dominante du thème</h4>
                <p>Zone de vie la plus représentée dans les facteurs calculés.</p>
              </div>
              {houseGroup.items[0]?.detail ? (
                <span className="natal-raw-badge natal-raw-badge--strong">{houseGroup.items[0].detail}</span>
              ) : null}
            </header>

            <div className="natal-raw-dominance-list">
              {houseGroup.items.map((item) => (
                <article className="natal-raw-dominance-card" key={`${houseGroup.title}-${item.label}-${item.value}`}>
                  <div className="natal-raw-dominance-card__number">{extractHouseRank(item.label)}</div>
                  <div>
                    <strong>{item.label}</strong>
                    <p>{item.value}</p>
                    {item.detail ? <small>{item.detail}</small> : null}
                  </div>
                </article>
              ))}
            </div>
          </section>
        ) : null}

        {planetGroup ? (
          <section className="natal-technical-block" aria-label={planetGroup.title}>
            <header className="natal-technical-block__header">
              <div>
                <h4>{planetGroup.title}</h4>
                <p>Éléments complémentaires qui renforcent ou nuancent les repères principaux.</p>
              </div>
            </header>

            <div className="natal-raw-mini-grid">
              {planetGroup.items.map((item) => (
                <article className="natal-raw-mini-fact" key={`${planetGroup.title}-${item.label}-${item.value}`}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                  {item.detail ? <small>{item.detail}</small> : null}
                </article>
              ))}
            </div>
          </section>
        ) : null}

        {aspectGroup ? (
          <section className="natal-technical-block natal-technical-block--aspects" aria-label={aspectGroup.title}>
            <header className="natal-technical-block__header">
              <div>
                <h4>{aspectGroup.title}</h4>
                <p>Relations géométriques fortes entre deux points du thème.</p>
              </div>
            </header>

            <div className="natal-raw-aspect-list">
              {aspectGroup.items.map((item: NatalCalculationFactItemViewModel) => {
                const tone = classifyAspectTone(item.detail)
                return (
                  <article
                    className={`natal-raw-aspect-card natal-raw-aspect-card--${tone}`}
                    key={`${aspectGroup.title}-${item.label}-${item.value}`}
                  >
                    <div className="natal-raw-aspect-card__type">
                      <span className="natal-raw-aspect-icon" aria-hidden="true">
                        {tone === "flow" ? "△" : tone === "tension" ? "□" : "☌"}
                      </span>
                      <strong>{item.label}</strong>
                    </div>
                    <div className="natal-raw-aspect-card__content">
                      <strong>{item.value}</strong>
                      {item.detail ? <small>{item.detail}</small> : null}
                    </div>
                    <span className={`natal-raw-badge natal-raw-badge--${tone}`}>{labelAspectTone(item.detail)}</span>
                  </article>
                )
              })}
            </div>
          </section>
        ) : null}
      </div>
    </details>
  )
}

function NatalCalculationReading({ reading }: { reading: NatalCalculationReadingViewModel }) {
  const hasPublicSections =
    reading.summary !== null ||
    reading.explanations.length > 0 ||
    reading.pillars.length > 0 ||
    reading.axes.length > 0 ||
    reading.lifeAreas.length > 0 ||
    reading.otherForces.length > 0 ||
    reading.aspects.length > 0

  if (!hasPublicSections) return null

  return (
    <div className="natal-reading-pedagogy">
      {reading.summary ? <NatalSummary summary={reading.summary} /> : null}
      <NatalExplanations explanations={reading.explanations} />
      <NatalPillars pillars={reading.pillars} />
      <NatalAxes axes={reading.axes} />
      <NatalLifeAreas lifeAreas={reading.lifeAreas} />
      <NatalOtherForces otherForces={reading.otherForces} />
      <NatalAspectDynamics aspects={reading.aspects} />
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
      {reading.calculationReading ? <NatalRawCalculationDetails reading={reading.calculationReading} /> : null}
    </article>
  )
}

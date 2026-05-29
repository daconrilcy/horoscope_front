// Aspects majeurs publics: le composant affiche le ranking fourni par le payload.
import type { AspectResult, DominantAspect } from "../../api/natalChart"
import { resolveMajorAspects } from "./natalPublicFacts"

type NatalMajorAspectsProps = {
  dominantAspects: DominantAspect[] | undefined
  aspects: AspectResult[] | undefined
  translatePlanet: (code: string) => string
  translateAspect: (code: string) => string
}

function getImpactLabel(rank: number | undefined): string {
  if (typeof rank === "number" && rank <= 3) return "Impact majeur"
  if (typeof rank === "number" && rank <= 7) return "Impact fort"
  return "Impact secondaire"
}

/** Affiche au maximum dix aspects classes par le backend, sans orbe ni score brut. */
export function NatalMajorAspects({
  dominantAspects,
  aspects,
  translatePlanet,
  translateAspect,
}: NatalMajorAspectsProps) {
  const publicAspects = resolveMajorAspects(dominantAspects, aspects, 10)

  return (
    <section className="natal-public-section" aria-labelledby="natal-major-aspects-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">Aspects majeurs</span>
        <h2 id="natal-major-aspects-title">Aspects majeurs</h2>
      </div>
      {publicAspects.length === 0 ? (
        <p className="natal-public-empty">Aucun classement d'aspects dominant n'est disponible dans ce payload.</p>
      ) : (
        <div className="natal-insight-grid">
          {publicAspects.map((aspect, index) => (
            <article
              key={`${aspect.aspect_code}-${aspect.planet_a}-${aspect.planet_b}-${index}`}
              className="natal-insight-card"
            >
              <span className="natal-impact-badge">{getImpactLabel(aspect.rank)}</span>
              <h3>
                {translateAspect(aspect.aspect_code)} · {translatePlanet(aspect.planet_a)}
                {" / "}
                {translatePlanet(aspect.planet_b)}
              </h3>
              {[aspect.meaning, aspect.manifestation, aspect.positive_expression, aspect.attention_point]
                .filter((line): line is string => Boolean(line))
                .map((line) => (
                  <p key={line}>{line}</p>
                ))}
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

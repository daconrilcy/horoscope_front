// Aspects majeurs publics: le composant affiche le ranking fourni par le payload.
import type { AspectResult, DominantAspect } from "../../api/natalChart"
import { resolveMajorAspects, type PublicCopyLang } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalMajorAspectsProps = {
  dominantAspects: DominantAspect[] | undefined
  aspects: AspectResult[] | undefined
  translatePlanet: (code: string) => string
  translateAspect: (code: string) => string
  lang?: PublicCopyLang
}

function getImpactLabel(rank: number | undefined, impacts: ReturnType<typeof getNatalPublicCopy>["majorAspects"]["impacts"]): string {
  if (typeof rank === "number" && rank <= 3) return impacts.major
  if (typeof rank === "number" && rank <= 7) return impacts.strong
  return impacts.secondary
}

/** Affiche au maximum dix aspects classes par le backend, sans orbe ni score brut. */
export function NatalMajorAspects({
  dominantAspects,
  aspects,
  translatePlanet,
  translateAspect,
  lang,
}: NatalMajorAspectsProps) {
  const copy = getNatalPublicCopy(lang).majorAspects
  const publicAspects = resolveMajorAspects(dominantAspects, aspects, 10)

  return (
    <section className="natal-public-section" aria-labelledby="natal-major-aspects-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.title}</span>
        <h2 id="natal-major-aspects-title">{copy.title}</h2>
      </div>
      {publicAspects.length === 0 ? (
        <p className="natal-public-empty">{copy.empty}</p>
      ) : (
        <div className="natal-insight-grid">
          {publicAspects.map((aspect, index) => (
            <article
              key={`${aspect.aspect_code}-${aspect.planet_a}-${aspect.planet_b}-${index}`}
              className="natal-insight-card"
            >
              <span className="natal-impact-badge">{getImpactLabel(aspect.rank, copy.impacts)}</span>
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

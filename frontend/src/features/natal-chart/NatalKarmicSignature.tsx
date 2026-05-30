// Signature karmique publique: elle assemble uniquement les points et planetes deja projetes.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { formatPlacement, getAstralPoint, getPlanetPosition } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalKarmicSignatureProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang?: PublicCopyLang
}

/** Rend la trajectoire d'evolution avec noeuds, Saturne et Pluton issus du payload public. */
export function NatalKarmicSignature({ chart, labels, lang }: NatalKarmicSignatureProps) {
  const publicCopy = getNatalPublicCopy(lang)
  const copy = publicCopy.karmic
  const unavailable = publicCopy.dna.unavailable
  const northNode = getAstralPoint(chart.result.astral_points, ["NORTH_NODE", "TRUE_NODE", "north_node"])
  const southNode = getAstralPoint(chart.result.astral_points, ["SOUTH_NODE", "south_node"])
  const saturn = getPlanetPosition(chart.result.planet_positions, "SATURN")
  const pluto = getPlanetPosition(chart.result.planet_positions, "PLUTO")

  return (
    <section className="natal-public-section" aria-labelledby="natal-karmic-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.eyebrow}</span>
        <h2 id="natal-karmic-title">{copy.title}</h2>
      </div>
      <div className="natal-insight-grid">
        <article className="natal-insight-card">
          <h3>{copy.northNode}</h3>
          <p>{formatPlacement(northNode, labels, unavailable)}</p>
        </article>
        <article className="natal-insight-card">
          <h3>{copy.southNode}</h3>
          <p>{formatPlacement(southNode, labels, unavailable)}</p>
        </article>
        <article className="natal-insight-card">
          <h3>{copy.saturn}</h3>
          <p>{formatPlacement(saturn, labels, unavailable)}</p>
        </article>
        <article className="natal-insight-card">
          <h3>{copy.pluto}</h3>
          <p>{formatPlacement(pluto, labels, unavailable)}</p>
        </article>
      </div>
    </section>
  )
}

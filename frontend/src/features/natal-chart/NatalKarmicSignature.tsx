// Signature karmique publique: elle assemble uniquement les points et planetes deja projetes.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers } from "./natalPublicFacts"
import { formatPlacement, getAstralPoint, getPlanetPosition } from "./natalPublicFacts"

type NatalKarmicSignatureProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
}

/** Rend la trajectoire d'evolution avec noeuds, Saturne et Pluton issus du payload public. */
export function NatalKarmicSignature({ chart, labels }: NatalKarmicSignatureProps) {
  const northNode = getAstralPoint(chart.result.astral_points, ["NORTH_NODE", "TRUE_NODE", "north_node"])
  const southNode = getAstralPoint(chart.result.astral_points, ["SOUTH_NODE", "south_node"])
  const saturn = getPlanetPosition(chart.result.planet_positions, "SATURN")
  const pluto = getPlanetPosition(chart.result.planet_positions, "PLUTO")

  return (
    <section className="natal-public-section" aria-labelledby="natal-karmic-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">Signature karmique</span>
        <h2 id="natal-karmic-title">Votre trajectoire d'evolution</h2>
      </div>
      <div className="natal-insight-grid">
        <article className="natal-insight-card">
          <h3>Noeud Nord</h3>
          <p>{formatPlacement(northNode, labels, "Noeud Nord indisponible")}</p>
        </article>
        <article className="natal-insight-card">
          <h3>Noeud Sud</h3>
          <p>{formatPlacement(southNode, labels, "Noeud Sud indisponible")}</p>
        </article>
        <article className="natal-insight-card">
          <h3>Saturne</h3>
          <p>{formatPlacement(saturn, labels, "Saturne indisponible")}</p>
        </article>
        <article className="natal-insight-card">
          <h3>Pluton</h3>
          <p>{formatPlacement(pluto, labels, "Pluton indisponible")}</p>
        </article>
      </div>
    </section>
  )
}

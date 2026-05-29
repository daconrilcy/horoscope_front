// Potentiel relationnel: la section lit Venus et la maison VII depuis le payload.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers } from "./natalPublicFacts"
import { formatPlacement, getAdapterTexts, getHouse, getPlanetPosition } from "./natalPublicFacts"

type NatalRelationshipPotentialProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
}

/** Affiche le potentiel relationnel sans produire de texte astrologique local autonome. */
export function NatalRelationshipPotential({ chart, labels }: NatalRelationshipPotentialProps) {
  const items = [
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "VENUS"), labels, "Venus indisponible"),
    formatPlacement(getHouse(chart.result.houses, 7), labels, "Maison VII indisponible"),
    ...getAdapterTexts(chart.result.interpretation_adapter, "relationships"),
  ].slice(0, 3)

  return (
    <section className="natal-public-section" aria-labelledby="natal-relationship-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">Lien</span>
        <h2 id="natal-relationship-title">Potentiel relationnel</h2>
      </div>
      <ul className="natal-public-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

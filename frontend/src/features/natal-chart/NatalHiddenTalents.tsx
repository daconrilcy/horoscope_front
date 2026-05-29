// Potentiels caches: les items sont derives de placements publics et de signaux acceptes.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers } from "./natalPublicFacts"
import { formatPlacement, getAdapterTexts, getHouse, getPlanetPosition } from "./natalPublicFacts"

type NatalHiddenTalentsProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
}

/** Affiche les talents caches a partir de la maison XII, Neptune et des signaux publics. */
export function NatalHiddenTalents({ chart, labels }: NatalHiddenTalentsProps) {
  const items = [
    ...getAdapterTexts(chart.result.interpretation_adapter, "inner_life"),
    formatPlacement(getHouse(chart.result.houses, 12), labels, "Maison XII indisponible"),
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "NEPTUNE"), labels, "Neptune indisponible"),
  ].slice(0, 3)

  return (
    <section className="natal-public-section" aria-labelledby="natal-hidden-talents-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">Potentiels</span>
        <h2 id="natal-hidden-talents-title">Talents caches</h2>
      </div>
      <ul className="natal-public-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

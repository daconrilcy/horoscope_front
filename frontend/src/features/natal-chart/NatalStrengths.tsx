// Forces natales publiques: les items restent ancrés dans les signaux du payload.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers } from "./natalPublicFacts"
import { formatPlacement, getAdapterTexts, getPlanetPosition } from "./natalPublicFacts"

type NatalStrengthsProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
}

/** Affiche au moins trois forces fondees sur les signaux publics ou placements majeurs. */
export function NatalStrengths({ chart, labels }: NatalStrengthsProps) {
  const adapterTexts = getAdapterTexts(chart.result.interpretation_adapter, "support").slice(0, 3)
  const fallback = [
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "SUN"), labels, "Soleil indisponible"),
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "JUPITER"), labels, "Jupiter indisponible"),
    chart.result.dominant_planets?.top_planet_code
      ? `Dominante ${labels.translatePlanet(chart.result.dominant_planets.top_planet_code)}`
      : "Dominante indisponible",
  ]
  const items = [...adapterTexts, ...fallback].slice(0, 3)

  return (
    <section className="natal-public-section" aria-labelledby="natal-strengths-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">Appuis</span>
        <h2 id="natal-strengths-title">Forces</h2>
      </div>
      <ul className="natal-public-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

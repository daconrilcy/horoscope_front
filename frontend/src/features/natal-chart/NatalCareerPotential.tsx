// Potentiel professionnel: la section cite le MC, la maison X et les dominantes publiques.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers } from "./natalPublicFacts"
import { formatPlacement, getAdapterTexts, getHouse } from "./natalPublicFacts"

type NatalCareerPotentialProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
}

/** Affiche le potentiel professionnel depuis les reperes publics du theme. */
export function NatalCareerPotential({ chart, labels }: NatalCareerPotentialProps) {
  const mostElevated = chart.result.dominant_planets?.most_elevated_planet_code
  const items = [
    formatPlacement(getHouse(chart.result.houses, 10), labels, "MC / Maison X indisponible"),
    mostElevated ? `Planete culminante: ${labels.translatePlanet(mostElevated)}` : "Planete culminante indisponible",
    ...getAdapterTexts(chart.result.interpretation_adapter, "career"),
  ].slice(0, 3)

  return (
    <section className="natal-public-section" aria-labelledby="natal-career-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">Vocation</span>
        <h2 id="natal-career-title">Potentiel professionnel</h2>
      </div>
      <ul className="natal-public-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

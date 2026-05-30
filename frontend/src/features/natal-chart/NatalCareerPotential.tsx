// Potentiel professionnel: la section cite le MC, la maison X et les dominantes publiques.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { formatPlacement, getAdapterTexts, getHouse } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalCareerPotentialProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang?: PublicCopyLang
}

/** Affiche le potentiel professionnel depuis les reperes publics du theme. */
export function NatalCareerPotential({ chart, labels, lang }: NatalCareerPotentialProps) {
  const copy = getNatalPublicCopy(lang).career
  const unavailable = getNatalPublicCopy(lang).dna.unavailable
  const mostElevated = chart.result.dominant_planets?.most_elevated_planet_code
  const items = [
    formatPlacement(getHouse(chart.result.houses, 10), labels, `${labels.translateHouse(10)} ${unavailable}`),
    mostElevated ? `${copy.elevatedPlanet}: ${labels.translatePlanet(mostElevated)}` : copy.unavailable,
    ...getAdapterTexts(chart.result.interpretation_adapter, "career"),
  ].slice(0, 3)

  return (
    <section className="natal-public-section" aria-labelledby="natal-career-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.eyebrow}</span>
        <h2 id="natal-career-title">{copy.title}</h2>
      </div>
      <ul className="natal-public-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

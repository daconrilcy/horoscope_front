// Potentiels caches: les items sont derives de placements publics et de signaux acceptes.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { formatPlacement, getAdapterTexts, getHouse, getPlanetPosition } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalHiddenTalentsProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang?: PublicCopyLang
}

/** Affiche les talents caches a partir de la maison XII, Neptune et des signaux publics. */
export function NatalHiddenTalents({ chart, labels, lang }: NatalHiddenTalentsProps) {
  const copy = getNatalPublicCopy(lang).hiddenTalents
  const unavailable = getNatalPublicCopy(lang).dna.unavailable
  const items = [
    ...getAdapterTexts(chart.result.interpretation_adapter, "inner_life"),
    formatPlacement(getHouse(chart.result.houses, 12), labels, `${labels.translateHouse(12)} ${unavailable}`),
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "NEPTUNE"), labels, `${labels.translatePlanet("NEPTUNE")} ${unavailable}`),
  ].slice(0, 3)

  return (
    <section className="natal-public-section" aria-labelledby="natal-hidden-talents-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.eyebrow}</span>
        <h2 id="natal-hidden-talents-title">{copy.title}</h2>
      </div>
      <ul className="natal-public-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

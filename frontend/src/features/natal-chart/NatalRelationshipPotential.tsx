// Potentiel relationnel: la section lit Venus et la maison VII depuis le payload.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { formatPlacement, getAdapterTexts, getHouse, getPlanetPosition } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalRelationshipPotentialProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang?: PublicCopyLang
}

/** Affiche le potentiel relationnel sans produire de texte astrologique local autonome. */
export function NatalRelationshipPotential({ chart, labels, lang }: NatalRelationshipPotentialProps) {
  const copy = getNatalPublicCopy(lang).relationship
  const unavailable = getNatalPublicCopy(lang).dna.unavailable
  const items = [
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "VENUS"), labels, `${labels.translatePlanet("VENUS")} ${unavailable}`),
    formatPlacement(getHouse(chart.result.houses, 7), labels, `${labels.translateHouse(7)} ${unavailable}`),
    ...getAdapterTexts(chart.result.interpretation_adapter, "relationships"),
  ].slice(0, 3)

  return (
    <section className="natal-public-section" aria-labelledby="natal-relationship-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.eyebrow}</span>
        <h2 id="natal-relationship-title">{copy.title}</h2>
      </div>
      <ul className="natal-public-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

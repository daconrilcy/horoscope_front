// Forces natales publiques: les items restent ancrés dans les signaux du payload.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { formatPlacement, getAdapterTexts, getPlanetPosition } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalStrengthsProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang?: PublicCopyLang
}

/** Affiche au moins trois forces fondees sur les signaux publics ou placements majeurs. */
export function NatalStrengths({ chart, labels, lang }: NatalStrengthsProps) {
  const copy = getNatalPublicCopy(lang).strengths
  const unavailable = getNatalPublicCopy(lang).dna.unavailable
  const adapterTexts = getAdapterTexts(chart.result.interpretation_adapter, "support").slice(0, 3)
  const fallback = [
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "SUN"), labels, `${labels.translatePlanet("SUN")} ${unavailable}`),
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "JUPITER"), labels, `${labels.translatePlanet("JUPITER")} ${unavailable}`),
    chart.result.dominant_planets?.top_planet_code
      ? `${copy.dominant} ${labels.translatePlanet(chart.result.dominant_planets.top_planet_code)}`
      : copy.unavailable,
  ]
  const items = [...adapterTexts, ...fallback].slice(0, 3)

  return (
    <section className="natal-public-section" aria-labelledby="natal-strengths-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.eyebrow}</span>
        <h2 id="natal-strengths-title">{copy.title}</h2>
      </div>
      <ul className="natal-public-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

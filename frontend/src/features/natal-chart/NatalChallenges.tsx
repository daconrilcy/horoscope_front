// Defis natals publics: la section exploite les tensions deja exposees par l'API.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { formatPlacement, getAdapterTexts, getPlanetPosition } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalChallengesProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang?: PublicCopyLang
}

/** Affiche au moins trois defis relies a des tensions publiques ou placements existants. */
export function NatalChallenges({ chart, labels, lang }: NatalChallengesProps) {
  const copy = getNatalPublicCopy(lang).challenges
  const unavailable = getNatalPublicCopy(lang).dna.unavailable
  const adapterTexts = [
    ...getAdapterTexts(chart.result.interpretation_adapter, "tension"),
    ...(chart.result.interpretation_adapter?.tension_patterns ?? []),
    ...(chart.result.interpretation_adapter?.critical_patterns ?? []),
  ].slice(0, 3)
  const fallback = [
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "SATURN"), labels, `${labels.translatePlanet("SATURN")} ${unavailable}`),
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "MARS"), labels, `${labels.translatePlanet("MARS")} ${unavailable}`),
    formatPlacement(getPlanetPosition(chart.result.planet_positions, "PLUTO"), labels, `${labels.translatePlanet("PLUTO")} ${unavailable}`),
  ]
  const items = [...adapterTexts, ...fallback].slice(0, 3)

  return (
    <section className="natal-public-section" aria-labelledby="natal-challenges-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.eyebrow}</span>
        <h2 id="natal-challenges-title">{copy.title}</h2>
      </div>
      <ul className="natal-public-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

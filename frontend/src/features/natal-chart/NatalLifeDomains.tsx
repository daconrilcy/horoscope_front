// Domaines de vie publics: les cartes citent les placements existants sans inferer de nouveaux scores.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { formatPlacement, getHouse, getPlanetPosition } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalLifeDomainsProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang?: PublicCopyLang
}

/** Rend les six domaines de vie demandes par la refonte de la page natale. */
export function NatalLifeDomains({ chart, labels, lang }: NatalLifeDomainsProps) {
  const publicCopy = getNatalPublicCopy(lang)
  const copy = publicCopy.lifeDomains
  const unavailable = publicCopy.dna.unavailable
  const domains = [
    { title: copy.items[0], anchor: formatPlacement(getPlanetPosition(chart.result.planet_positions, "SUN"), labels, unavailable) },
    { title: copy.items[1], anchor: formatPlacement(getPlanetPosition(chart.result.planet_positions, "MOON"), labels, unavailable) },
    { title: copy.items[2], anchor: formatPlacement(getHouse(chart.result.houses, 7), labels, unavailable) },
    { title: copy.items[3], anchor: formatPlacement(getHouse(chart.result.houses, 10), labels, unavailable) },
    { title: copy.items[4], anchor: formatPlacement(getHouse(chart.result.houses, 2), labels, unavailable) },
    { title: copy.items[5], anchor: formatPlacement(getHouse(chart.result.houses, 12), labels, unavailable) },
  ]

  return (
    <section className="natal-public-section" aria-labelledby="natal-life-domains-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.eyebrow}</span>
        <h2 id="natal-life-domains-title">{copy.title}</h2>
      </div>
      <div className="natal-insight-grid">
        {domains.map((domain) => (
          <article key={domain.title} className="natal-insight-card">
            <h3>{domain.title}</h3>
            <p>{domain.anchor}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

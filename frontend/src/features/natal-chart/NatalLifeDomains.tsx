// Domaines de vie publics: les cartes citent les placements existants sans inferer de nouveaux scores.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers } from "./natalPublicFacts"
import { formatPlacement, getHouse, getPlanetPosition } from "./natalPublicFacts"

type NatalLifeDomainsProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
}

/** Rend les six domaines de vie demandes par la refonte de la page natale. */
export function NatalLifeDomains({ chart, labels }: NatalLifeDomainsProps) {
  const domains = [
    { title: "Personnalite", anchor: formatPlacement(getPlanetPosition(chart.result.planet_positions, "SUN"), labels, "Soleil indisponible") },
    { title: "Emotions", anchor: formatPlacement(getPlanetPosition(chart.result.planet_positions, "MOON"), labels, "Lune indisponible") },
    { title: "Relations", anchor: formatPlacement(getHouse(chart.result.houses, 7), labels, "Maison VII indisponible") },
    { title: "Carriere", anchor: formatPlacement(getHouse(chart.result.houses, 10), labels, "Maison X indisponible") },
    { title: "Argent", anchor: formatPlacement(getHouse(chart.result.houses, 2), labels, "Maison II indisponible") },
    { title: "Spiritualite", anchor: formatPlacement(getHouse(chart.result.houses, 12), labels, "Maison XII indisponible") },
  ]

  return (
    <section className="natal-public-section" aria-labelledby="natal-life-domains-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">Domaines de vie</span>
        <h2 id="natal-life-domains-title">Les grands domaines de vie</h2>
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

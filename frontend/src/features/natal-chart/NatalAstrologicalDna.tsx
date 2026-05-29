// Cartes ADN astrologique: elles projettent seulement les faits publics deja calcules.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers } from "./natalPublicFacts"

type NatalAstrologicalDnaProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
}

function formatPlanet(code: string | null | undefined, labels: AstrologyLabelers): string {
  return code ? labels.translatePlanet(code) : "Indisponible"
}

function formatSignature(value: string | null | undefined): string {
  return value ? value.replace(/_/g, " ") : "Indisponible"
}

function formatWhy(facts: string[] | null | undefined, fallback: string): string {
  return facts && facts.length > 0 ? facts.join(" · ") : fallback
}

/** Affiche les dominantes, le maitre du theme et la signature globale du payload public. */
export function NatalAstrologicalDna({ chart, labels }: NatalAstrologicalDnaProps) {
  const dominantPlanets = chart.result.dominant_planets
  const signature = chart.result.chart_signature
  const cards = [
    {
      title: "Dominante planetaire",
      value: formatPlanet(dominantPlanets?.top_planet_code, labels),
      why: formatWhy(dominantPlanets?.planets?.[0]?.explanation_facts, "Dominante fournie par les signaux publics."),
    },
    {
      title: "Maitre du theme",
      value: formatPlanet(dominantPlanets?.chart_ruler_code, labels),
      why: formatWhy(dominantPlanets?.planets?.find((planet) => planet.planet_code === dominantPlanets?.chart_ruler_code)?.explanation_facts, "Repere fourni par les signaux publics."),
    },
    {
      title: "Planete culminante",
      value: formatPlanet(dominantPlanets?.most_elevated_planet_code, labels),
      why: formatWhy(dominantPlanets?.planets?.find((planet) => planet.planet_code === dominantPlanets?.most_elevated_planet_code)?.explanation_facts, "Repere fourni par les signaux publics."),
    },
    {
      title: "Element dominant",
      value: formatSignature(signature?.primary_element),
      why: "Equilibre global fourni par le payload public.",
    },
    {
      title: "Modalite dominante",
      value: formatSignature(signature?.primary_modality),
      why: "Equilibre global fourni par le payload public.",
    },
    {
      title: "Polarite dominante",
      value: formatSignature(signature?.primary_polarity),
      why: "Equilibre global fourni par le payload public.",
    },
  ]

  return (
    <section className="natal-public-section" aria-labelledby="natal-dna-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">ADN astrologique</span>
        <h2 id="natal-dna-title">ADN astrologique</h2>
      </div>
      <div className="natal-insight-grid">
        {cards.map((card) => (
          <article key={card.title} className="natal-insight-card">
            <h3>{card.title}</h3>
            <p className="natal-insight-card__value">{card.value}</p>
            <p className="natal-insight-card__why">
              <strong>Pourquoi ?</strong> {card.why}
            </p>
          </article>
        ))}
      </div>
    </section>
  )
}

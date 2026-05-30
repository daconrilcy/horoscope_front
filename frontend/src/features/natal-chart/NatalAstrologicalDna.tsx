// Cartes ADN astrologique: elles projettent seulement les faits publics deja calcules.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalAstrologicalDnaProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang?: PublicCopyLang
}

function formatPlanet(code: string | null | undefined, labels: AstrologyLabelers, unavailable: string): string {
  return code ? labels.translatePlanet(code) : unavailable
}

function formatSignature(value: string | null | undefined, unavailable: string): string {
  return value ? value.replace(/_/g, " ") : unavailable
}

function formatWhy(facts: string[] | null | undefined, fallback: string): string {
  return facts && facts.length > 0 ? facts.join(" · ") : fallback
}

/** Affiche les dominantes, le maitre du theme et la signature globale du payload public. */
export function NatalAstrologicalDna({ chart, labels, lang }: NatalAstrologicalDnaProps) {
  const copy = getNatalPublicCopy(lang).dna
  const dominantPlanets = chart.result.dominant_planets
  const signature = chart.result.chart_signature
  const cards = [
    {
      title: copy.cards.dominantPlanet,
      value: formatPlanet(dominantPlanets?.top_planet_code, labels, copy.unavailable),
      why: formatWhy(dominantPlanets?.planets?.[0]?.explanation_facts, copy.publicSignals),
    },
    {
      title: copy.cards.chartRuler,
      value: formatPlanet(dominantPlanets?.chart_ruler_code, labels, copy.unavailable),
      why: formatWhy(dominantPlanets?.planets?.find((planet) => planet.planet_code === dominantPlanets?.chart_ruler_code)?.explanation_facts, copy.publicSignals),
    },
    {
      title: copy.cards.elevatedPlanet,
      value: formatPlanet(dominantPlanets?.most_elevated_planet_code, labels, copy.unavailable),
      why: formatWhy(dominantPlanets?.planets?.find((planet) => planet.planet_code === dominantPlanets?.most_elevated_planet_code)?.explanation_facts, copy.publicSignals),
    },
    {
      title: copy.cards.element, value: formatSignature(signature?.primary_element, copy.unavailable), why: copy.publicBalance,
    },
    {
      title: copy.cards.modality, value: formatSignature(signature?.primary_modality, copy.unavailable), why: copy.publicBalance,
    },
    {
      title: copy.cards.polarity, value: formatSignature(signature?.primary_polarity, copy.unavailable), why: copy.publicBalance,
    },
  ]

  return (
    <section className="natal-public-section" aria-labelledby="natal-dna-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">{copy.title}</span>
        <h2 id="natal-dna-title">{copy.title}</h2>
      </div>
      <div className="natal-insight-grid">
        {cards.map((card) => (
          <article key={card.title} className="natal-insight-card">
            <h3>{card.title}</h3>
            <p className="natal-insight-card__value">{card.value}</p>
            <p className="natal-insight-card__why">
              <strong>{copy.why}</strong> {card.why}
            </p>
          </article>
        ))}
      </div>
    </section>
  )
}

// Tests de la couche ADN astrologique publique de la refonte natale.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { NatalAstrologicalDna } from "../features/natal-chart/NatalAstrologicalDna"
import type { LatestNatalChart } from "../api/natalChart"

const labels = {
  translatePlanet: (code: string) => ({ SUN: "Soleil", MOON: "Lune" })[code] ?? code,
  translateSign: (code: string) => code,
  translateHouse: (house: number) => `Maison ${house}`,
}

function chart(): LatestNatalChart {
  return {
    chart_id: "chart-1",
    created_at: "2026-05-29T10:00:00Z",
    metadata: { reference_version: "v1", ruleset_version: "v1", engine: "test", house_system: "equal" },
    result: {
      reference_version: "v1",
      ruleset_version: "v1",
      prepared_input: {
        birth_datetime_local: "1990-01-01T10:00:00",
        birth_datetime_utc: "1990-01-01T09:00:00Z",
        timestamp_utc: 1,
        julian_day: 1,
        birth_timezone: "Europe/Paris",
        jd_ut: 1,
        timezone_used: "Europe/Paris",
      },
      planet_positions: [],
      houses: [],
      aspects: [],
      dominant_planets: {
        top_planet_code: "SUN",
        chart_ruler_code: "MOON",
        most_elevated_planet_code: "SUN",
        planets: [{ planet_code: "SUN", rank: 1, score: 0.9, explanation_facts: ["fact public"] }],
      },
      chart_signature: { primary_element: "fire", primary_modality: "fixed", primary_polarity: "positive" },
    },
  }
}

describe("NatalAstrologicalDna", () => {
  it("affiche les cartes ADN depuis les dominantes et la signature publiques", () => {
    render(<NatalAstrologicalDna chart={chart()} labels={labels} />)

    expect(screen.getByRole("heading", { name: "ADN astrologique" })).toBeInTheDocument()
    expect(screen.getAllByText("Soleil")).toHaveLength(2)
    expect(screen.getByText("Lune")).toBeInTheDocument()
    expect(screen.getByText("fire")).toBeInTheDocument()
    expect(screen.getAllByText(/fact public/)).toHaveLength(2)
  })
})

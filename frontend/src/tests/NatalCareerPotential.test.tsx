// Tests du potentiel professionnel public de la page natale.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { LatestNatalChart } from "../api/natalChart"
import { NatalCareerPotential } from "../features/natal-chart/NatalCareerPotential"

const labels = {
  translatePlanet: (code: string) => ({ SUN: "Soleil" })[code] ?? code,
  translateSign: (code: string) => code,
  translateHouse: (house: number) => `Maison ${house}`,
}

const chart = {
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
    houses: [{ number: 10, cusp_longitude: 280 }],
    aspects: [],
    dominant_planets: { top_planet_code: "SUN", most_elevated_planet_code: "SUN" },
    interpretation_adapter: {
      signals: [{ semantic_category: "career", explanation_fact: "Cadre professionnel structure et visible" }],
    },
  },
} satisfies LatestNatalChart

describe("NatalCareerPotential", () => {
  it("cite maison X, planete culminante et signal metier public", () => {
    render(<NatalCareerPotential chart={chart} labels={labels} />)

    expect(screen.getByRole("heading", { name: "Potentiel professionnel" })).toBeInTheDocument()
    expect(screen.getByText("Maison 10")).toBeInTheDocument()
    expect(screen.getByText("Planete culminante: Soleil")).toBeInTheDocument()
    expect(screen.getByText("Cadre professionnel structure et visible")).toBeInTheDocument()
  })
})

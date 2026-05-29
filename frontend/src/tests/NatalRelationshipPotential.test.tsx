// Tests du potentiel relationnel public de la page natale.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { LatestNatalChart } from "../api/natalChart"
import { NatalRelationshipPotential } from "../features/natal-chart/NatalRelationshipPotential"

const labels = {
  translatePlanet: (code: string) => ({ VENUS: "Venus" })[code] ?? code,
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
    planet_positions: [{ planet_code: "VENUS", sign_code: "TAURUS", longitude: 45, house_number: 5 }],
    houses: [{ number: 7, cusp_longitude: 180 }],
    aspects: [],
    interpretation_adapter: {
      signals: [{ semantic_category: "relationships", explanation_fact: "Besoin relationnel stable et explicite" }],
    },
  },
} satisfies LatestNatalChart

describe("NatalRelationshipPotential", () => {
  it("cite Venus, maison VII et signal relationnel public", () => {
    render(<NatalRelationshipPotential chart={chart} labels={labels} />)

    expect(screen.getByRole("heading", { name: "Potentiel relationnel" })).toBeInTheDocument()
    expect(screen.getByText(/Venus en TAURUS/)).toBeInTheDocument()
    expect(screen.getByText("Maison 7")).toBeInTheDocument()
    expect(screen.getByText("Besoin relationnel stable et explicite")).toBeInTheDocument()
  })
})

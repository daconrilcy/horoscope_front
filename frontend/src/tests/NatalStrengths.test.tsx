// Tests des forces publiques de la page natale.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { LatestNatalChart } from "../api/natalChart"
import { NatalStrengths } from "../features/natal-chart/NatalStrengths"

const labels = {
  translatePlanet: (code: string) => ({ SUN: "Soleil", JUPITER: "Jupiter" })[code] ?? code,
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
    planet_positions: [
      { planet_code: "SUN", sign_code: "LEO", longitude: 130, house_number: 1 },
      { planet_code: "JUPITER", sign_code: "SAGITTARIUS", longitude: 250, house_number: 5 },
    ],
    houses: [],
    aspects: [],
    dominant_planets: { top_planet_code: "SUN" },
    interpretation_adapter: {
      signals: [
        { semantic_category: "support", explanation_fact: "Elan clair" },
        { semantic_category: "support", explanation_fact: "Confiance disponible" },
      ],
    },
  },
} satisfies LatestNatalChart

describe("NatalStrengths", () => {
  it("rend au moins trois appuis issus du payload", () => {
    render(<NatalStrengths chart={chart} labels={labels} />)

    expect(screen.getByRole("heading", { name: "Forces" })).toBeInTheDocument()
    expect(screen.getByText("Elan clair")).toBeInTheDocument()
    expect(screen.getByText("Confiance disponible")).toBeInTheDocument()
    expect(screen.getByText(/Soleil en LEO/)).toBeInTheDocument()
  })
})

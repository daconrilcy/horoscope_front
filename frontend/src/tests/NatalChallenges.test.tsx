// Tests des defis publics de la page natale.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { LatestNatalChart } from "../api/natalChart"
import { NatalChallenges } from "../features/natal-chart/NatalChallenges"

const labels = {
  translatePlanet: (code: string) => ({ SATURN: "Saturne", MARS: "Mars", PLUTO: "Pluton" })[code] ?? code,
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
      { planet_code: "SATURN", sign_code: "CAPRICORN", longitude: 280, house_number: 10 },
      { planet_code: "MARS", sign_code: "ARIES", longitude: 10, house_number: 1 },
      { planet_code: "PLUTO", sign_code: "SCORPIO", longitude: 220, house_number: 8 },
    ],
    houses: [],
    aspects: [],
    interpretation_adapter: {
      signals: [{ semantic_category: "tension", explanation_fact: "Tension a nommer" }],
      tension_patterns: ["Pattern public"],
    },
  },
} satisfies LatestNatalChart

describe("NatalChallenges", () => {
  it("rend au moins trois defis issus du payload", () => {
    render(<NatalChallenges chart={chart} labels={labels} />)

    expect(screen.getByRole("heading", { name: "Defis" })).toBeInTheDocument()
    expect(screen.getByText("Tension a nommer")).toBeInTheDocument()
    expect(screen.getByText("Pattern public")).toBeInTheDocument()
    expect(screen.getByText(/Saturne en CAPRICORN/)).toBeInTheDocument()
  })
})

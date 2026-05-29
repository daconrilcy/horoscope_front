// Tests des talents caches publics de la page natale.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { LatestNatalChart } from "../api/natalChart"
import { NatalHiddenTalents } from "../features/natal-chart/NatalHiddenTalents"

const labels = {
  translatePlanet: (code: string) => ({ NEPTUNE: "Neptune" })[code] ?? code,
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
    planet_positions: [{ planet_code: "NEPTUNE", sign_code: "PISCES", longitude: 330, house_number: 12 }],
    houses: [{ number: 12, cusp_longitude: 330 }],
    aspects: [],
    interpretation_adapter: {
      signals: [{ semantic_category: "inner_life", explanation_fact: "Imaginaire nourri par la vie interieure" }],
    },
  },
} satisfies LatestNatalChart

describe("NatalHiddenTalents", () => {
  it("cite les signaux caches sans texte technique", () => {
    render(<NatalHiddenTalents chart={chart} labels={labels} />)

    expect(screen.getByRole("heading", { name: "Talents caches" })).toBeInTheDocument()
    expect(screen.getByText("Imaginaire nourri par la vie interieure")).toBeInTheDocument()
    expect(screen.getByText("Maison 12")).toBeInTheDocument()
    expect(screen.getByText(/Neptune en PISCES/)).toBeInTheDocument()
  })
})

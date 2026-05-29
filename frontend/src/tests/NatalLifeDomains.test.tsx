// Tests des domaines de vie publics de la page natale.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { NatalLifeDomains } from "../features/natal-chart/NatalLifeDomains"
import type { LatestNatalChart } from "../api/natalChart"

const labels = {
  translatePlanet: (code: string) => ({ SUN: "Soleil", MOON: "Lune" })[code] ?? code,
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
      { planet_code: "SUN", sign_code: "LEO", longitude: 130, house_number: 10 },
      { planet_code: "MOON", sign_code: "CANCER", longitude: 100, house_number: 4 },
    ],
    houses: Array.from({ length: 12 }, (_, index) => ({ number: index + 1, cusp_longitude: index * 30 })),
    aspects: [],
  },
} satisfies LatestNatalChart

describe("NatalLifeDomains", () => {
  it("affiche les six domaines canoniques avec leurs ancrages payload", () => {
    render(<NatalLifeDomains chart={chart} labels={labels} />)

    for (const title of ["Personnalite", "Emotions", "Relations", "Carriere", "Argent", "Spiritualite"]) {
      expect(screen.getByRole("heading", { name: title })).toBeInTheDocument()
    }
    expect(screen.getByText(/Soleil en LEO/)).toBeInTheDocument()
    expect(screen.getByText(/Maison 7/)).toBeInTheDocument()
  })
})

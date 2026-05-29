// Tests de la signature karmique publique de la page natale.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { NatalKarmicSignature } from "../features/natal-chart/NatalKarmicSignature"
import type { LatestNatalChart } from "../api/natalChart"

const labels = {
  translatePlanet: (code: string) =>
    ({
      SATURN: "Saturne",
      PLUTO: "Pluton",
      NORTH_NODE: "Nœud Nord",
      SOUTH_NODE: "Nœud Sud",
    })[code] ?? code,
  translateSign: (code: string) => code,
  translateHouse: (house: number) => `Maison ${house}`,
  placementIn: " en ",
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
      { planet_code: "PLUTO", sign_code: "SCORPIO", longitude: 220, house_number: 8 },
    ],
    houses: [],
    aspects: [],
    astral_points: [
      { code: "north_node", sign: "aries", house: 1 },
      { code: "south_node", sign: "libra", house: 7 },
    ],
  },
} satisfies LatestNatalChart

describe("NatalKarmicSignature", () => {
  it("cite noeuds, Saturne et Pluton depuis le payload public backend", () => {
    render(<NatalKarmicSignature chart={chart} labels={labels} />)

    expect(screen.getByRole("heading", { name: "Votre trajectoire d'evolution" })).toBeInTheDocument()
    expect(screen.getByText(/Nœud Nord en ARIES, Maison 1/)).toBeInTheDocument()
    expect(screen.getByText(/Nœud Sud en LIBRA, Maison 7/)).toBeInTheDocument()
    expect(screen.getByText(/Saturne en CAPRICORN/)).toBeInTheDocument()
    expect(screen.getByText(/Pluton en SCORPIO/)).toBeInTheDocument()
  })
})

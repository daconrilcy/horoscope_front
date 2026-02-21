import { cleanup, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { NatalChartPage } from "../pages/NatalChartPage"

const mockUseLatestNatalChart = vi.fn()

vi.mock("../api/natalChart", () => ({
  ApiError: class extends Error {
    code: string
    status: number

    constructor(code: string, message: string, status: number) {
      super(message)
      this.code = code
      this.status = status
    }
  },
  useLatestNatalChart: () => mockUseLatestNatalChart(),
}))

afterEach(() => {
  cleanup()
  mockUseLatestNatalChart.mockReset()
})

describe("NatalChartPage", () => {
  it("renders loading state", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: true,
      isError: false,
    })
    render(<NatalChartPage />)
    expect(screen.getByText("Chargement de votre dernier theme natal...")).toBeInTheDocument()
  })

  it("renders empty state", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: { code: "natal_chart_not_found", message: "not found" },
    })
    render(<NatalChartPage />)
    expect(screen.getByText("Aucun theme natal disponible pour le moment.")).toBeInTheDocument()
  })

  it("renders error state with retry", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: { code: "natal_engine_unavailable", message: "service down" },
      refetch: vi.fn(),
    })
    render(<NatalChartPage />)
    expect(screen.getByText("Une erreur est survenue: service down")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Reessayer" })).toBeInTheDocument()
  })

  it("renders success state sections", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        chart_id: "c1",
        created_at: "2026-02-18T10:00:00Z",
        metadata: { reference_version: "1.0.0", ruleset_version: "1.0.0" },
        result: {
          reference_version: "1.0.0",
          ruleset_version: "1.0.0",
          prepared_input: {
            birth_datetime_local: "1990-06-15T10:30:00+02:00",
            birth_datetime_utc: "1990-06-15T08:30:00+00:00",
            timestamp_utc: 645438600,
            julian_day: 2448057.854,
            birth_timezone: "Europe/Paris",
          },
          planet_positions: [
            { planet_code: "SUN", longitude: 83.2, sign_code: "GEMINI", house_number: 10 },
          ],
          houses: [{ number: 1, cusp_longitude: 15.2 }],
          aspects: [{ aspect_code: "TRINE", planet_a: "SUN", planet_b: "MOON", angle: 120, orb: 1.4 }],
        },
      },
    })
    render(<NatalChartPage />)
    expect(screen.getByRole("heading", { name: "Theme natal" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Planetes" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Maisons" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Aspects majeurs" })).toBeInTheDocument()
  })
})

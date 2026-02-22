import { cleanup, render, screen } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { NatalChartPage } from "../pages/NatalChartPage"
import { ApiError, useLatestNatalChart } from "../api/natalChart"

vi.mock("../api/natalChart", () => ({
  ApiError: class extends Error {
    code: string
    status: number
    requestId?: string
    constructor(code: string, message: string, status: number, requestId?: string) {
      super(message)
      this.code = code
      this.status = status
      this.requestId = requestId
    }
  },
  useLatestNatalChart: vi.fn(),
}))

const mockUseLatestNatalChart = vi.mocked(useLatestNatalChart)

beforeEach(() => {
  vi.stubGlobal("navigator", { language: "fr-FR" })
  localStorage.clear()
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  vi.unstubAllGlobals()
})

describe("NatalChartPage", () => {
  it("renders loading state", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: true,
      isError: false,
      data: null,
    })
    render(<NatalChartPage />)
    expect(screen.getByText("Chargement de votre dernier thème natal...")).toBeInTheDocument()
  })

  it("renders empty state", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("natal_chart_not_found", "not found", 404),
    })
    render(<NatalChartPage />)
    expect(screen.getByText("Aucun thème natal disponible pour le moment.")).toBeInTheDocument()
  })

  it("renders error state with retry", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("natal_engine_unavailable", "service down", 503),
      refetch: vi.fn(),
    })
    render(<NatalChartPage />)
    expect(screen.getByText("Une erreur est survenue: service down")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Réessayer" })).toBeInTheDocument()
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
            birth_datetime_local: "1990-01-15T10:30:00",
            birth_datetime_utc: "1990-01-15T09:30:00Z",
            timestamp_utc: 632572200,
            julian_day: 2447908.9,
            birth_timezone: "Europe/Paris",
          },
          planet_positions: [{ planet_code: "SUN", sign_code: "GEMINI", longitude: 83.2, house_number: 10 }],
          houses: [{ number: 1, cusp_longitude: 15.2 }],
          aspects: [{ aspect_code: "TRINE", planet_a: "SUN", planet_b: "MOON", angle: 120.0, orb: 1.4 }],
        },
      },
    })

    render(<NatalChartPage />)
    expect(screen.getByRole("heading", { name: "Thème natal" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Planètes" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Maisons" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Aspects majeurs" })).toBeInTheDocument()

    // Sample data check — now translated to French
    expect(screen.getAllByText(/Soleil/).length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText(/Gémeaux/)).toBeInTheDocument()
    expect(screen.getByText(/Trigone/)).toBeInTheDocument()
    expect(screen.getByText(/Lune/)).toBeInTheDocument()
  })

  const CHART_BASE = {
    chart_id: "abc",
    created_at: "2026-02-22T10:00:00Z",
    metadata: { reference_version: "1.0", ruleset_version: "1.0" },
    result: {
      reference_version: "1.0",
      ruleset_version: "1.0",
      prepared_input: {
        birth_datetime_local: "1990-01-15T10:30:00",
        birth_datetime_utc: "1990-01-15T09:30:00Z",
        timestamp_utc: 632400600,
        julian_day: 2447907.896,
        birth_timezone: "Europe/Paris",
      },
      planet_positions: [],
      houses: [],
      aspects: [],
    },
  }

  it("affiche le bandeau lieu quand degraded_mode = no_location (AC1)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE, metadata: { ...CHART_BASE.metadata, degraded_mode: "no_location" } },
    })
    render(<NatalChartPage />)
    expect(screen.getByText(/Thème calculé en maisons égales/i)).toBeInTheDocument()
    expect(screen.queryByText(/Thème calculé en thème solaire/i)).not.toBeInTheDocument()
  })

  it("affiche le bandeau heure quand degraded_mode = no_time (AC2)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE, metadata: { ...CHART_BASE.metadata, degraded_mode: "no_time" } },
    })
    render(<NatalChartPage />)
    expect(screen.getByText(/Thème calculé en thème solaire/i)).toBeInTheDocument()
    expect(screen.queryByText(/Thème calculé en maisons égales/i)).not.toBeInTheDocument()
  })

  it("affiche les deux bandeaux quand degraded_mode = no_location_no_time (AC3)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE, metadata: { ...CHART_BASE.metadata, degraded_mode: "no_location_no_time" } },
    })
    render(<NatalChartPage />)
    expect(screen.getByText(/Thème calculé en maisons égales/i)).toBeInTheDocument()
    expect(screen.getByText(/Thème calculé en thème solaire/i)).toBeInTheDocument()
  })

  it("n'affiche aucun bandeau quand degraded_mode est absent (nominal)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE },
    })
    render(<NatalChartPage />)
    expect(screen.queryByText(/Thème calculé en maisons égales/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/Thème calculé en thème solaire/i)).not.toBeInTheDocument()
  })

  it("n'affiche aucun bandeau quand degraded_mode est explicitement null", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE, metadata: { ...CHART_BASE.metadata, degraded_mode: null } },
    })
    render(<NatalChartPage />)
    expect(screen.queryByText(/Thème calculé en maisons égales/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/Thème calculé en thème solaire/i)).not.toBeInTheDocument()
  })

  it("affiche les planètes en français (AC1 i18n)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          planet_positions: [{ planet_code: "SUN", sign_code: "ARIES", longitude: 15.0, house_number: 1 }],
        },
      },
    })
    render(<NatalChartPage />)
    expect(screen.getByText(/Soleil/)).toBeInTheDocument()
    expect(screen.queryByText(/SUN/)).not.toBeInTheDocument()
  })

  it("affiche les signes en français (AC1 i18n)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          planet_positions: [{ planet_code: "MOON", sign_code: "GEMINI", longitude: 25.0, house_number: 3 }],
        },
      },
    })
    render(<NatalChartPage />)
    expect(screen.getByText(/Gémeaux/)).toBeInTheDocument()
    expect(screen.queryByText(/GEMINI/)).not.toBeInTheDocument()
  })

  it("affiche les maisons avec nom symbolique en français (AC1 i18n)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          houses: [{ number: 1, cusp_longitude: 10.0 }],
        },
      },
    })
    render(<NatalChartPage />)
    expect(screen.getByText(/Maison I — Identité/)).toBeInTheDocument()
  })

  it("affiche les aspects en français (AC1 i18n)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          aspects: [{ aspect_code: "TRINE", planet_a: "SUN", planet_b: "MOON", angle: 120.0, orb: 1.5 }],
        },
      },
    })
    render(<NatalChartPage />)
    expect(screen.getByText(/Trigone/)).toBeInTheDocument()
    expect(screen.queryByText(/TRINE/)).not.toBeInTheDocument()
  })
})

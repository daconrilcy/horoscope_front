import { cleanup, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { NatalChartPage } from "../pages/NatalChartPage"
/**
 * ApiError est importé pour créer des instances dans les tests (new ApiError(...)).
 * vi.mock remplace la classe réelle par notre mock défini ci-dessous.
 */
import { ApiError, useLatestNatalChart } from "../api/natalChart"

/**
 * Mock de ApiError pour les tests.
 * Note: La définition doit être inline car vi.mock est hoisted au top du fichier.
 */
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

const mockUseLatestNatalChart: ReturnType<typeof vi.mocked<typeof useLatestNatalChart>> = vi.mocked(useLatestNatalChart)

const TEST_REFERENCE_VERSION = "1.0"
const TEST_RULESET_VERSION = "1.0"

/**
 * Fixture de base pour un chart natal valide, utilisée dans plusieurs tests.
 * Les arrays planet_positions, houses et aspects sont intentionnellement vides
 * pour permettre aux tests individuels de les override avec des données spécifiques.
 */
const CHART_BASE = {
  chart_id: "abc",
  created_at: "2024-02-22T10:00:00Z",
  metadata: { reference_version: TEST_REFERENCE_VERSION, ruleset_version: TEST_RULESET_VERSION },
  result: {
    reference_version: TEST_REFERENCE_VERSION,
    ruleset_version: TEST_RULESET_VERSION,
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

beforeEach(() => {
  vi.stubGlobal("navigator", { ...navigator, language: "fr-FR" })
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
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Chargement de votre dernier thème natal/i)).toBeInTheDocument()
  })

  it("renders empty state", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("natal_chart_not_found", "not found", 404),
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Aucun thème natal disponible pour le moment/i)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Compléter mon profil/i })).toBeInTheDocument()
  })

  it("renders error state with retry and calls refetch on click", async () => {
    const refetchMock = vi.fn()
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("natal_engine_unavailable", "service down", 503),
      refetch: refetchMock,
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Une erreur est survenue\. Veuillez réessayer/i)).toBeInTheDocument()
    const retryButton = screen.getByRole("button", { name: /Réessayer/i })
    expect(retryButton).toBeInTheDocument()

    retryButton.click()

    expect(refetchMock).toHaveBeenCalledTimes(1)
  })

  it("renders generic error state when error is not ApiError", () => {
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new Error("Network failure"),
      refetch: vi.fn(),
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Une erreur est survenue\. Veuillez réessayer/i)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Réessayer/i })).toBeInTheDocument()
    expect(consoleErrorSpy).not.toHaveBeenCalledWith(expect.stringContaining("[Support] Request ID"))
    consoleErrorSpy.mockRestore()
  })

  it("renders incomplete birth data alert when birth_profile_not_found (AC1)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("birth_profile_not_found", "profile not found", 404),
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Vos données de naissance sont incomplètes/i)).toBeInTheDocument()
    expect(screen.getByText(/Complétez votre profil pour générer votre thème natal/i)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Compléter mon profil/i })).toHaveAttribute("href", "/profile")
  })

  it("renders incomplete birth data alert when unprocessable_entity 422 (AC1)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("unprocessable_entity", "invalid data", 422),
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Vos données de naissance sont incomplètes/i)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Compléter mon profil" })).toBeInTheDocument()
  })

  it("logs requestId to console but does not display it to user (AC8)", () => {
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("birth_profile_not_found", "not found", 404, "req-test-123"),
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(consoleErrorSpy).toHaveBeenCalledWith("[Support] Request ID: req-test-123")
    expect(screen.queryByText(/req-test-123/)).not.toBeInTheDocument()
    consoleErrorSpy.mockRestore()
  })

  it("does not log requestId when ApiError has no requestId", () => {
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("natal_engine_unavailable", "service down", 503),
      refetch: vi.fn(),
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(consoleErrorSpy).not.toHaveBeenCalledWith(expect.stringContaining("[Support] Request ID"))
    consoleErrorSpy.mockRestore()
  })

  it("does not log requestId when no error occurs", () => {
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE },
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(consoleErrorSpy).not.toHaveBeenCalledWith(expect.stringContaining("[Support] Request ID"))
    consoleErrorSpy.mockRestore()
  })

  it("renders success state sections", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          planet_positions: [{ planet_code: "SUN", sign_code: "GEMINI", longitude: 83.2, house_number: 10 }],
          houses: [{ number: 1, cusp_longitude: 15.2 }],
          aspects: [{ aspect_code: "TRINE", planet_a: "SUN", planet_b: "MOON", angle: 120.0, orb: 1.4 }],
        },
      },
    })

    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByRole("heading", { name: /Thème natal/i })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Planètes/i })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Maisons/i })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Aspects majeurs/i })).toBeInTheDocument()
    // Verify i18n metadata labels are rendered
    expect(screen.getByText(/Généré le/i)).toBeInTheDocument()

    // Sample data check — now translated to French
    expect(screen.getAllByText(/Soleil/).length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText(/Gémeaux/)).toBeInTheDocument()
    expect(screen.getByText(/Trigone/)).toBeInTheDocument()
    expect(screen.getByText(/Lune/)).toBeInTheDocument()
  })

  it("affiche le bandeau lieu quand degraded_mode = no_location (AC1)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE, metadata: { ...CHART_BASE.metadata, degraded_mode: "no_location" } },
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Thème calculé en maisons égales/i)).toBeInTheDocument()
    expect(screen.queryByText(/Thème calculé en thème solaire/i)).not.toBeInTheDocument()
  })

  it("affiche le bandeau heure quand degraded_mode = no_time (AC2)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE, metadata: { ...CHART_BASE.metadata, degraded_mode: "no_time" } },
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Thème calculé en thème solaire/i)).toBeInTheDocument()
    expect(screen.queryByText(/Thème calculé en maisons égales/i)).not.toBeInTheDocument()
  })

  it("affiche les deux bandeaux quand degraded_mode = no_location_no_time (AC3)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE, metadata: { ...CHART_BASE.metadata, degraded_mode: "no_location_no_time" } },
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Thème calculé en maisons égales/i)).toBeInTheDocument()
    expect(screen.getByText(/Thème calculé en thème solaire/i)).toBeInTheDocument()
  })

  it("n'affiche aucun bandeau quand degraded_mode est absent (nominal)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE },
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.queryByText(/Thème calculé en maisons égales/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/Thème calculé en thème solaire/i)).not.toBeInTheDocument()
  })

  it("n'affiche aucun bandeau quand degraded_mode est explicitement null", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { ...CHART_BASE, metadata: { ...CHART_BASE.metadata, degraded_mode: null } },
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
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
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
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
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
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
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
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
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByText(/Trigone/)).toBeInTheDocument()
    expect(screen.queryByText(/TRINE/)).not.toBeInTheDocument()
  })

  it("handles undefined planet_positions, houses, and aspects gracefully", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          planet_positions: undefined,
          houses: undefined,
          aspects: undefined,
        },
      },
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(screen.getByRole("heading", { name: /Thème natal/i })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Planètes/i })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Maisons/i })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Aspects majeurs/i })).toBeInTheDocument()
    expect(screen.getByText(/Aucun aspect majeur détecté/i)).toBeInTheDocument()

    // Vérifier que les listes planètes et maisons sont vides (aucun <li>)
    const lists = screen.getAllByRole("list")
    const planetsAndHousesLists = lists.filter((ul) => ul.querySelectorAll("li").length === 0)
    expect(planetsAndHousesLists.length).toBe(2)
  })
})

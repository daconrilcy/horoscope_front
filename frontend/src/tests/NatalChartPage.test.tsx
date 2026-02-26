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
  metadata: {
    reference_version: TEST_REFERENCE_VERSION,
    ruleset_version: TEST_RULESET_VERSION,
    house_system: "equal",
  },
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

  it("does not log requestId for functional 4xx errors (birth_profile_not_found)", () => {
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
    expect(consoleErrorSpy).not.toHaveBeenCalledWith("[Support] Request ID: req-test-123")
    expect(screen.queryByText(/req-test-123/)).not.toBeInTheDocument()
    consoleErrorSpy.mockRestore()
  })

  it("logs requestId for technical 5xx errors", () => {
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("natal_engine_unavailable", "service down", 503, "req-503-1"),
      refetch: vi.fn(),
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(consoleErrorSpy).toHaveBeenCalledWith("[Support] Request ID: req-503-1")
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

  it("does not log requestId when error is natal_chart_not_found (expected empty state)", () => {
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new ApiError("natal_chart_not_found", "not found", 404, "req-not-found-1"),
    })
    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )
    expect(consoleErrorSpy).not.toHaveBeenCalledWith("[Support] Request ID: req-not-found-1")
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
    expect(screen.getByRole("heading", { name: "Planètes" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Maisons" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Aspects majeurs/i })).toBeInTheDocument()
    // Verify i18n metadata labels are rendered
    expect(screen.getByText(/Généré le/i)).toBeInTheDocument()
    expect(screen.getByText(/Système de maisons Maisons égales/i)).toBeInTheDocument()

    // Sample data check — now translated to French
    // Note: getAllByText used for terms that also appear in the pedagogical guide
    expect(screen.getAllByText(/Soleil/).length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText(/Gémeaux/).length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText(/Trigone/)).toBeInTheDocument()
    expect(screen.getByText(/Lune/)).toBeInTheDocument()
  })

  it("affiche le degré dans le signe et l'intervalle de maison pour chaque planète", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          planet_positions: [
            { planet_code: "SUN", sign_code: "TAURUS", longitude: 34.08, house_number: 1 },
          ],
          houses: Array.from({ length: 12 }).map((_, idx) => ({
            number: idx + 1,
            cusp_longitude: (18.46 + idx * 30) % 360,
          })),
          aspects: [],
        },
      },
    })

    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )

    expect(screen.getByText(/Taureau 4°05′ \(34\.08°\)/)).toBeInTheDocument()
    expect(screen.getByText(/Maison I.+18\.46° -> 48\.46°/)).toBeInTheDocument()
  })

  it("borne le degré dans le signe à 29°59′ au lieu de 30°00′ sur frontière d'arrondi", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          planet_positions: [
            { planet_code: "SUN", sign_code: "ARIES", longitude: 29.9999, house_number: 1 },
          ],
          houses: Array.from({ length: 12 }).map((_, idx) => ({
            number: idx + 1,
            cusp_longitude: (18.46 + idx * 30) % 360,
          })),
          aspects: [],
        },
      },
    })

    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )

    expect(screen.getByText(/Bélier 29°59′ \(30\.00°\)/)).toBeInTheDocument()
    expect(screen.queryByText(/30°00′/)).not.toBeInTheDocument()
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
    // "Soleil" also appears in the pedagogical guide sign example — use getAllByText
    expect(screen.getAllByText(/Soleil/).length).toBeGreaterThanOrEqual(1)
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
    // "Gémeaux" also appears in the pedagogical guide signs description — use getAllByText
    expect(screen.getAllByText(/Gémeaux/).length).toBeGreaterThanOrEqual(1)
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

  describe("AC-18-3: Bloc résumé astro_profile", () => {
    it("affiche le profil astrologique avec signe solaire et ascendant", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          astro_profile: {
            sun_sign_code: "leo",
            ascendant_sign_code: "scorpio",
            missing_birth_time: false,
          },
        },
      })
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      expect(screen.getByRole("heading", { name: /Profil astrologique/i })).toBeInTheDocument()
      expect(screen.getByText("Lion")).toBeInTheDocument()
      expect(screen.getByText("Scorpion")).toBeInTheDocument()
    })

    it("affiche '— (heure de naissance manquante)' quand missing_birth_time=true et pas d'ascendant", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          astro_profile: {
            sun_sign_code: "leo",
            ascendant_sign_code: null,
            missing_birth_time: true,
          },
        },
      })
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      expect(screen.getByText(/heure de naissance manquante/i)).toBeInTheDocument()
    })

    it("affiche '—' pour l'ascendant quand missing_birth_time=false et pas d'ascendant", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          astro_profile: {
            sun_sign_code: "leo",
            ascendant_sign_code: null,
            missing_birth_time: false,
          },
        },
      })
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      // "—" should appear as the ascendant value
      expect(screen.getAllByText("—").length).toBeGreaterThanOrEqual(1)
      expect(screen.queryByText(/heure de naissance manquante/i)).not.toBeInTheDocument()
    })

    it("n'affiche pas le bloc profil astrologique quand astro_profile est absent", () => {
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
      expect(screen.queryByRole("heading", { name: /Profil astrologique/i })).not.toBeInTheDocument()
    })
  })

  describe("AC-19-1: Bloc pédagogique NatalChartGuide", () => {
    it("affiche le guide pédagogique avec les 3 sections (signes, maisons, planètes) (AC 1)", () => {
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
      // Le summary doit être visible (section réduite par défaut)
      expect(screen.getByText(/Comment lire ton thème natal/i)).toBeInTheDocument()
    })

    it("affiche le résumé du guide sans le développer (AC 1)", () => {
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
      // Le titre summary est toujours visible même sans open
      const summary = screen.getByText(/Comment lire ton thème natal/i)
      expect(summary.tagName.toLowerCase()).toBe("summary")
    })

    it("affiche l'exemple de conversion longitude → signe (AC 2)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: { ...CHART_BASE },
      })
      const { container } = render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      // Ouvrir le details pour voir le contenu
      const details = container.querySelector("details.natal-chart-guide")
      expect(details).toBeInTheDocument()
      details!.setAttribute("open", "")
      expect(screen.getByText(/Soleil 34,08° → Taureau 4°05′/)).toBeInTheDocument()
    })

    it("affiche la convention d'intervalle semi-ouvert [début, fin) (AC 3)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: { ...CHART_BASE },
      })
      const { container } = render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      const details = container.querySelector("details.natal-chart-guide")
      details!.setAttribute("open", "")
      expect(screen.getByText(/\[début, fin\)/i)).toBeInTheDocument()
    })

    it("affiche un exemple de wrap 360->0 (AC 4)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: { ...CHART_BASE },
      })
      const { container } = render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      const details = container.querySelector("details.natal-chart-guide")
      details!.setAttribute("open", "")
      expect(screen.getByText(/348,46° → 360° puis 0° → 18,46°/)).toBeInTheDocument()
    })

    it("affiche le message ascendant non calculé quand missing_birth_time=true (AC 5)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          astro_profile: {
            sun_sign_code: "leo",
            ascendant_sign_code: null,
            missing_birth_time: true,
          },
        },
      })
      const { container } = render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      const details = container.querySelector("details.natal-chart-guide")
      details!.setAttribute("open", "")
      expect(
        screen.getByText(/L'heure de naissance n'est pas renseignée.*l'ascendant n'est pas calculé/i)
      ).toBeInTheDocument()
    })

    it("n'affiche pas le message ascendant non calculé quand missing_birth_time=false (AC 5)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          astro_profile: {
            sun_sign_code: "leo",
            ascendant_sign_code: "scorpio",
            missing_birth_time: false,
          },
        },
      })
      const { container } = render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      const details = container.querySelector("details.natal-chart-guide")
      details!.setAttribute("open", "")
      expect(screen.queryByText(/l'ascendant n'est pas calculé/i)).not.toBeInTheDocument()
    })

    it("affiche le guide même quand astro_profile est absent (AC 1)", () => {
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
      expect(screen.getByText(/Comment lire ton thème natal/i)).toBeInTheDocument()
    })
  })

  describe("AC-19-1: Wrap 360->0 dans l'intervalle de maison (AC 4, AC 7)", () => {
    it("affiche l'intervalle de wrap 360->0 pour la maison 12 (AC 4)", () => {
      // House 12: cusp 348.46°, House 1: cusp 18.46° (wrap case)
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          result: {
            ...CHART_BASE.result,
            planet_positions: [
              { planet_code: "SUN", sign_code: "PISCES", longitude: 355.0, house_number: 12 },
            ],
            houses: Array.from({ length: 12 }).map((_, idx) => ({
              number: idx + 1,
              cusp_longitude: idx === 0 ? 18.46 : (18.46 + idx * 30) % 360,
            })),
            aspects: [],
          },
        },
      })

      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      // House 12 interval: 348.46° -> 360° puis 0° -> 18.46°
      expect(screen.getByText(/348\.46° -> 360° puis 0° -> 18\.46°/)).toBeInTheDocument()
    })

    it("affiche l'intervalle normal pour une maison sans wrap (AC 7)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          result: {
            ...CHART_BASE.result,
            planet_positions: [
              { planet_code: "SUN", sign_code: "TAURUS", longitude: 34.08, house_number: 1 },
            ],
            houses: Array.from({ length: 12 }).map((_, idx) => ({
              number: idx + 1,
              cusp_longitude: (18.46 + idx * 30) % 360,
            })),
            aspects: [],
          },
        },
      })

      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      // House 1: 18.46° -> 48.46° (normal format, no wrap)
      const planetLi = screen.getByText(/Maison I.+18\.46° -> 48\.46°/)
      expect(planetLi).toBeInTheDocument()
      // The planet list item itself should NOT contain the wrap notation "puis 0°"
      expect(planetLi.textContent).not.toContain("puis 0°")
    })
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
    expect(screen.getByRole("heading", { name: "Planètes" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Maisons" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Aspects majeurs/i })).toBeInTheDocument()
    expect(screen.getByText(/Aucun aspect majeur détecté/i)).toBeInTheDocument()

    // Vérifier que les listes planètes et maisons sont vides (aucun <li>)
    const lists = screen.getAllByRole("list")
    const planetsAndHousesLists = lists.filter((ul) => ul.querySelectorAll("li").length === 0)
    expect(planetsAndHousesLists.length).toBe(2)
  })
})

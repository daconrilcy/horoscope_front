import { cleanup, render, screen, within } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { NatalChartPage } from "../pages/NatalChartPage"
import { NatalChartGuide } from "../components/NatalChartGuide"
import { getGuideTranslations, natalChartTranslations } from "../i18n/natalChart"
/**
 * ApiError est importé pour créer des instances dans les tests (new ApiError(...)).
 * vi.mock remplace la classe réelle par notre mock défini ci-dessous.
 */
import { ApiError, useLatestNatalChart, generateNatalChart } from "../api/natalChart"

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
  generateNatalChart: vi.fn(),
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
    expect(screen.getByRole("heading", { name: /Les aspects/i, level: 2 })).toBeInTheDocument()
    // Verify i18n metadata labels are rendered
    expect(screen.getByText(/Généré le/i)).toBeInTheDocument()
    expect(screen.getByText(/Système de maisons Maisons égales/i)).toBeInTheDocument()

    // Sample data check — now translated to French
    const planetSection = screen.getByRole("heading", { name: "Planètes" }).parentElement!
    const aspectSection = screen.getByRole("heading", { name: /Les aspects/i, level: 2 }).parentElement!

    const { getByText: getByTextInPlanets } = within(planetSection)
    const { getByText: getByTextInAspects } = within(aspectSection)

    expect(getByTextInPlanets(/Soleil/)).toBeInTheDocument()
    expect(getByTextInPlanets(/Gémeaux/)).toBeInTheDocument()
    expect(getByTextInAspects(/Trigone/)).toBeInTheDocument()
    expect(getByTextInAspects(/Lune/)).toBeInTheDocument()
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

  it("affiche le symbole ℞ apres le nom de la planete quand is_retrograde=true", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          planet_positions: [
            {
              planet_code: "MERCURY",
              sign_code: "ARIES",
              longitude: 15.0,
              house_number: 1,
              is_retrograde: true,
            },
          ],
          houses: [{ number: 1, cusp_longitude: 15.2 }],
          aspects: [],
        },
      },
    })

    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )

    expect(screen.getByText(/Mercure ℞:/i)).toBeInTheDocument()
  })

  it("n'affiche pas le symbole ℞ quand is_retrograde est absent (legacy)", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        result: {
          ...CHART_BASE.result,
          planet_positions: [{ planet_code: "MERCURY", sign_code: "ARIES", longitude: 15.0, house_number: 1 }],
          houses: [{ number: 1, cusp_longitude: 15.2 }],
          aspects: [],
        },
      },
    })

    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )

    expect(screen.queryByText(/Mercure ℞:/i)).not.toBeInTheDocument()
    expect(screen.getByText(/Mercure:/i)).toBeInTheDocument()
  })

  it("affiche le libelle house system mappe pour metadata.house_system=placidus", () => {
    mockUseLatestNatalChart.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        ...CHART_BASE,
        metadata: { ...CHART_BASE.metadata, house_system: "placidus" },
      },
    })

    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <NatalChartPage />
      </MemoryRouter>
    )

    expect(screen.getByText(/Système de maisons Placidus/)).toBeInTheDocument()
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
    const planetSection = screen.getByRole("heading", { name: "Planètes" }).parentElement!
    expect(within(planetSection).getByText(/Soleil/)).toBeInTheDocument()
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
    const planetSection = screen.getByRole("heading", { name: "Planètes" }).parentElement!
    expect(within(planetSection).getByText(/Gémeaux/)).toBeInTheDocument()
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

    it("affiche la section des aspects dans le guide (AC 1)", () => {
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
      
      // On vérifie que le titre de la section dans le guide correspond au titre de la section principale
      const guideAspectsTitle = screen.getByRole("heading", { name: "Les aspects", level: 3 })
      expect(guideAspectsTitle).toBeInTheDocument()
      expect(screen.getByText(/L'orbe effective \(orbe eff\.\) indique l'écart réel mesuré/)).toBeInTheDocument()
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

    describe("Story 20-14: guide enrichi 6 sections + FAQ", () => {
      it("affiche les 6 sections métier dans le guide (AC 1 - 20-14)", () => {
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

        expect(screen.getByRole("heading", { name: /Les signes astrologiques/i, level: 3 })).toBeInTheDocument()
        expect(screen.getByRole("heading", { name: /Les planètes/i, level: 3 })).toBeInTheDocument()
        expect(screen.getByRole("heading", { name: /Les maisons/i, level: 3 })).toBeInTheDocument()
        expect(screen.getByRole("heading", { name: /Les angles/i, level: 3 })).toBeInTheDocument()
        expect(screen.getByRole("heading", { name: /Signe solaire et ascendant/i, level: 3 })).toBeInTheDocument()
        expect(screen.getByRole("heading", { name: /Les aspects/i, level: 3 })).toBeInTheDocument()
      })

      it("affiche le contenu de la section angles (AC 2 - 20-14)", () => {
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

        expect(screen.getByText(/Ascendant \(ASC\)/i)).toBeInTheDocument()
        expect(screen.getByText(/Milieu du Ciel \(MC\)/i)).toBeInTheDocument()
      })

      it("affiche la section signe solaire et ascendant avec desc (AC 5 - 20-14)", () => {
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

        expect(screen.getByText(/Le signe solaire est le signe dans lequel se trouve le Soleil/i)).toBeInTheDocument()
      })

      it("affiche l'astuce rétrograde dans la section planètes (AC 2 - 20-14)", () => {
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

        expect(screen.getByText(/Le symbole ℞ signifie que la planète est en mouvement rétrograde apparent/i)).toBeInTheDocument()
      })

      it("affiche une FAQ avec 8 questions (AC 4 - 20-14)", () => {
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

        expect(screen.getByText(/Pourquoi parle-t-on de 360°/i)).toBeInTheDocument()
        expect(screen.getByText(/Pourquoi y a-t-il deux découpages.*signes et maisons/i)).toBeInTheDocument()
        expect(screen.getByText(/Qu'est-ce qu'une longitude brute/i)).toBeInTheDocument()
        expect(screen.getByText(/Qu'est-ce qu'une cuspide/i)).toBeInTheDocument()
        expect(screen.getByText(/Pourquoi certaines maisons semblent bizarres/i)).toBeInTheDocument()
        expect(screen.getByText(/À quoi sert l'orbe dans les aspects/i)).toBeInTheDocument()
        expect(screen.getByText(/Que signifie le symbole ℞/i)).toBeInTheDocument()
        expect(screen.getByText(/Pourquoi le signe solaire et l'ascendant sont-ils mis en avant/i)).toBeInTheDocument()
      })

      it("affiche le titre FAQ dans le guide (AC 4 - 20-14)", () => {
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

        expect(screen.getByRole("heading", { name: /FAQ/i, level: 3 })).toBeInTheDocument()
      })
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

  describe("Story 20-13: aspects enrichis orb/orb_used et rétrograde", () => {
    it("affiche orb et orb_used quand les deux champs sont présents (AC 1)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          result: {
            ...CHART_BASE.result,
            aspects: [
              {
                aspect_code: "TRINE",
                planet_a: "SUN",
                planet_b: "MOON",
                angle: 120.0,
                orb: 2.5,
                orb_used: 1.8,
              },
            ],
          },
        },
      })
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      expect(screen.getByText(/orbe 2\.50°/i)).toBeInTheDocument()
      expect(screen.getByText(/orbe eff\. 1\.80°/i)).toBeInTheDocument()
    })

    it("affiche un état vide explicite quand aspects est vide (AC 2)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          result: { ...CHART_BASE.result, aspects: [] },
        },
      })
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      expect(screen.getByText(/Aucun aspect majeur détecté/i)).toBeInTheDocument()
    })

    it("affiche encore le symbole ℞ (non-régression retrograde) (AC 3)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          result: {
            ...CHART_BASE.result,
            planet_positions: [
              {
                planet_code: "MERCURY",
                sign_code: "ARIES",
                longitude: 15.0,
                house_number: 1,
                is_retrograde: true,
              },
            ],
            aspects: [
              {
                aspect_code: "CONJUNCTION",
                planet_a: "MERCURY",
                planet_b: "SUN",
                angle: 0.0,
                orb: 1.2,
                orb_used: 1.0,
              },
            ],
          },
        },
      })
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      expect(screen.getByText(/Mercure ℞:/i)).toBeInTheDocument()
      expect(screen.getByText(/orbe eff\. 1\.00°/i)).toBeInTheDocument()
    })

    it("rendu stable sans orb_used sur payload legacy (AC 4)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          result: {
            ...CHART_BASE.result,
            aspects: [
              {
                aspect_code: "OPPOSITION",
                planet_a: "SUN",
                planet_b: "MOON",
                angle: 180.0,
                orb: 3.0,
              },
            ],
          },
        },
      })
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      expect(screen.getByText(/Opposition/i)).toBeInTheDocument()
      expect(screen.getByText(/orbe 3\.00°/i)).toBeInTheDocument()
      
      const legacyList = screen.getByRole("heading", { name: /Les aspects/i, level: 2 }).parentElement?.querySelector("ul")
      expect(legacyList?.textContent).not.toContain("orbe eff.")
    })

    it("rendu stable quand orb_used est null (sécurité API)", () => {
      mockUseLatestNatalChart.mockReturnValue({
        isLoading: false,
        isError: false,
        data: {
          ...CHART_BASE,
          result: {
            ...CHART_BASE.result,
            aspects: [
              {
                aspect_code: "SEXTILE",
                planet_a: "SUN",
                planet_b: "MARS",
                angle: 60.0,
                orb: 2.0,
                orb_used: null as any,
              },
            ],
          },
        },
      })
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <NatalChartPage />
        </MemoryRouter>
      )
      expect(screen.getByText(/Sextile/i)).toBeInTheDocument()
      expect(screen.getByText(/orbe 2\.00°/i)).toBeInTheDocument()
      
      const nullOrbList = screen.getByRole("heading", { name: /Les aspects/i, level: 2 }).parentElement?.querySelector("ul")
      expect(nullOrbList?.textContent).not.toContain("orbe eff.")
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
    expect(screen.getByRole("heading", { name: /Les aspects/i, level: 2 })).toBeInTheDocument()
    expect(screen.getByText(/Aucun aspect majeur détecté/i)).toBeInTheDocument()

    // Vérifier que les listes planètes et maisons sont vides (aucun <li>)
    const lists = screen.getAllByRole("list")
    const planetsAndHousesLists = lists.filter((ul) => ul.querySelectorAll("li").length === 0)
    expect(planetsAndHousesLists.length).toBe(2)
  })

  describe("Story 20-15: i18n guide natal fr/en/es et fallback", () => {
    function openGuide(container: HTMLElement) {
      const details = container.querySelector("details.natal-chart-guide")
      details!.setAttribute("open", "")
    }

    it("affiche le guide en anglais — sections et FAQ (AC 2 - 20-15)", () => {
      const { container } = render(
        <NatalChartGuide lang="en" missingBirthTime={false} />
      )
      openGuide(container)

      expect(screen.getByText("How to read your natal chart")).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Zodiac signs", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Planets", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Houses", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Angles", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Sun sign and ascendant", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Aspects", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "FAQ", level: 3 })).toBeInTheDocument()

      // FAQ en anglais — 8 questions présentes
      expect(screen.getByText(/Why do we talk about 360°/i)).toBeInTheDocument()
      expect(screen.getByText(/Why are there two divisions/i)).toBeInTheDocument()
      expect(screen.getByText(/What is a raw longitude/i)).toBeInTheDocument()
      expect(screen.getByText(/What is a cusp/i)).toBeInTheDocument()
      expect(screen.getByText(/Why do some houses look unusual or cross 0°/i)).toBeInTheDocument()
      expect(screen.getByText(/What is the orb used for in aspects/i)).toBeInTheDocument()
      expect(screen.getByText(/What does the ℞ symbol mean/i)).toBeInTheDocument()
      expect(screen.getByText(/Why are the sun sign and ascendant highlighted/i)).toBeInTheDocument()
    })

    it("affiche le guide en espagnol — sections et FAQ (AC 3 - 20-15)", () => {
      const { container } = render(
        <NatalChartGuide lang="es" missingBirthTime={false} />
      )
      openGuide(container)

      expect(screen.getByText("Cómo leer tu carta natal")).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Los signos zodiacales", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Los planetas", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Las casas", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Los ángulos", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Signo solar y ascendente", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Los aspectos", level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "FAQ", level: 3 })).toBeInTheDocument()

      // FAQ en espagnol — 8 questions présentes
      expect(screen.getByText(/¿Por qué se habla de 360°/i)).toBeInTheDocument()
      expect(screen.getByText(/¿Por qué hay dos divisiones/i)).toBeInTheDocument()
      expect(screen.getByText(/¿Qué es una longitud bruta/i)).toBeInTheDocument()
      expect(screen.getByText(/¿Qué es una cúspide/i)).toBeInTheDocument()
      expect(screen.getByText(/¿Por qué algunas casas parecen extrañas/i)).toBeInTheDocument()
      expect(screen.getByText(/¿Para qué sirve el orbe en los aspectos/i)).toBeInTheDocument()
      expect(screen.getByText(/¿Qué significa el símbolo ℞/i)).toBeInTheDocument()
      expect(screen.getByText(/¿Por qué se destacan el signo solar y el ascendente/i)).toBeInTheDocument()
    })

    it("affiche le guide en français — sections et FAQ (non-régression AC 1 - 20-15)", () => {
      const { container } = render(
        <NatalChartGuide lang="fr" missingBirthTime={false} />
      )
      openGuide(container)

      expect(screen.getByText("Comment lire ton thème natal")).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: /Les signes astrologiques/i, level: 3 })).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: /FAQ/i, level: 3 })).toBeInTheDocument()
      expect(screen.getByText(/Pourquoi parle-t-on de 360°/i)).toBeInTheDocument()
    })

    it("fallback vers FR sans crash quand la langue n'est pas dans le dictionnaire (AC 4 - 20-15)", () => {
      // Simule un runtime avec une langue non supportée — getGuideTranslations doit retourner FR
      // @ts-expect-error - intentionnellement invalide pour tester le fallback runtime
      const result = getGuideTranslations("pt")
      expect(result.title).toBe(natalChartTranslations.fr.guide.title)
      expect(result.signsTitle).toBe(natalChartTranslations.fr.guide.signsTitle)
      expect(result.faq).toHaveLength(natalChartTranslations.fr.guide.faq.length)
      // Aucun crash — le composant doit rendre sans erreur avec le guide FR
      const { container } = render(
        <NatalChartGuide lang={"pt" as any} missingBirthTime={false} />
      )
      openGuide(container)
      expect(screen.getByText("Comment lire ton thème natal")).toBeInTheDocument()
    })

    it("affiche le message ascendant manquant dans la bonne langue (AC 2/3 - 20-15)", () => {
      const { container: containerEn } = render(
        <NatalChartGuide lang="en" missingBirthTime={true} />
      )
      openGuide(containerEn)
      expect(screen.getByText(/Birth time is not provided.*the ascendant is not calculated/i)).toBeInTheDocument()
      cleanup()

      const { container: containerEs } = render(
        <NatalChartGuide lang="es" missingBirthTime={true} />
      )
      openGuide(containerEs)
      expect(screen.getByText(/La hora de nacimiento no está registrada.*el ascendente no se calcula/i)).toBeInTheDocument()
    })

    it("intégration : NatalChartPage transmet la langue du navigateur au guide (AC 1/2 - 20-15)", () => {
      // Mock navigator.language = 'en-US'
      vi.stubGlobal("navigator", { language: "en-US" })

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

      // Le titre du guide doit être en anglais
      expect(screen.getByText("How to read your natal chart")).toBeInTheDocument()
      expect(screen.queryByText("Comment lire ton thème natal")).not.toBeInTheDocument()
    })
  })
})

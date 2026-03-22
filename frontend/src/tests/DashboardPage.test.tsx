import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { createMemoryRouter, RouterProvider } from "react-router-dom"

import { setAccessToken } from "../utils/authToken"
import { ThemeProvider } from "../state/ThemeProvider"
import { routes } from "../app/routes"

const AUTH_ME_USER = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      id: 42,
      role: "user",
      email: "test@example.com",
      created_at: "2025-01-15T10:30:00Z",
    },
  }),
}

const PREDICTION_OK = {
  ok: true,
  status: 200,
  json: async () => ({
    meta: { date_local: "2026-03-12" },
    summary: {
      overall_summary: "Une excellente journée vous attend avec de belles opportunités.",
    },
    categories: [
      { code: 'love', note_20: 18 },
      { code: 'work', note_20: 14 }
    ],
    timeline: [],
    turning_points: [],
  }),
}

const BIRTH_DATA_OK = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      astro_profile: {
        sun_sign_code: 'Aries'
      },
      geolocation_consent: true
    }
  })
}

const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
}

describe("DashboardPage Landing", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    setupToken()

    // Mock ResizeObserver
    class ResizeObserverMock {
      observe = vi.fn();
      unobserve = vi.fn();
      disconnect = vi.fn();
    }
    vi.stubGlobal('ResizeObserver', ResizeObserverMock);

    // Mock matchMedia
    vi.stubGlobal('matchMedia', vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })));

    // Mock Canvas getContext
    // @ts-ignore
    HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
      clearRect: vi.fn(),
      beginPath: vi.fn(),
      arc: vi.fn(),
      fill: vi.fn(),
      stroke: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      save: vi.fn(),
      restore: vi.fn(),
      translate: vi.fn(),
      createLinearGradient: vi.fn(() => ({ addColorStop: vi.fn() })),
      createRadialGradient: vi.fn(() => ({ addColorStop: vi.fn() })),
      fillRect: vi.fn(),
    }));
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("affiche le résumé de l'horoscope et les raccourcis d'activités", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })

    expect(screen.getByText("Activités")).toBeInTheDocument()
    expect(screen.getByText("Chat astrologue")).toBeInTheDocument()
    expect(screen.getByText("Consultation")).toBeInTheDocument()
    expect(screen.getByText("Guidance ciblée")).toBeInTheDocument()
  })

  it("priorise daily_synthesis sur overall_summary", async () => {
    const predictionWithSynthesis = {
      ok: true,
      status: 200,
      json: async () => ({
        meta: { date_local: "2026-03-12" },
        daily_synthesis: "Texte synthétique LLM prioritaire.",
        summary: {
          overall_summary: "Résumé legacy à ignorer.",
        },
        categories: [{ code: 'love', note_20: 18 }],
        timeline: [],
        turning_points: [],
      }),
    }
    vi.stubGlobal("fetch", makeFetchMock(predictionWithSynthesis))
    
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Texte synthétique LLM prioritaire/i)).toBeInTheDocument()
    })
    expect(screen.queryByText(/Résumé legacy à ignorer/i)).not.toBeInTheDocument()
  })

  it("navigue vers le détail de l'horoscope quand on clique sur le résumé", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    const user = userEvent.setup()
    
    const { router } = renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })

    const summaryCard = screen.getByLabelText(/Voir l'horoscope complet/i)
    await user.click(summaryCard)

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/dashboard/horoscope")
    })
  })

  it("ouvre le détail via la touche espace sur la carte résumé", async () => {
    vi.stubGlobal("fetch", makeFetchMock())

    const { router } = renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })

    const summaryCard = screen.getByLabelText(/Voir l'horoscope complet/i)
    summaryCard.focus()
    summaryCard.dispatchEvent(new KeyboardEvent("keydown", { key: " ", bubbles: true }))

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/dashboard/horoscope")
    })
  })

  it("n'affiche plus les sections détaillées (Moments clés, Agenda)", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })

    expect(screen.queryByText("Moments clés du jour")).not.toBeInTheDocument()
    expect(screen.queryByText("Agenda du jour")).not.toBeInTheDocument()
  })

  it("ne duplique plus les controles avatar et theme dans le contenu du dashboard", async () => {
    vi.stubGlobal("fetch", makeFetchMock())

    const { container } = renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })

    expect(container.querySelector(".today-header")).not.toBeInTheDocument()
  })

  it("gère l'état de chargement du résumé sans masquer les activités", async () => {
    let resolvePrediction: (value: any) => void
    const predictionPromise = new Promise((resolve) => {
      resolvePrediction = resolve
    })

    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/predictions/daily")) return predictionPromise
      return NOT_FOUND
    }))

    renderDashboard()

    expect(screen.getByText("Horoscope du jour en cours de rédaction")).toBeInTheDocument()
    expect(screen.getByText("Activités")).toBeInTheDocument()
    
    resolvePrediction!(PREDICTION_OK)
    
    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })
  })

  it("freeze la navigation vers le détail tant que l'horoscope du jour est en cours de rédaction", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/predictions/daily")) {
        return new Promise(() => undefined)
      }
      return NOT_FOUND
    }))

    const user = userEvent.setup()
    const { router } = renderDashboard()

    const loadingCard = await screen.findByRole("status", {
      name: "Horoscope du jour en cours de rédaction",
    })

    await user.click(loadingCard)

    expect(router.state.location.pathname).toBe("/dashboard")
    expect(screen.queryByLabelText(/Voir l'horoscope complet/i)).not.toBeInTheDocument()
  })

  it("gère l'erreur de prédiction en affichant un message dédié et une relance", async () => {
    let shouldFail = true
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/predictions/daily")) {
        if (shouldFail) {
          return {
            ok: false,
            status: 500,
            json: async () => ({ error: "Internal Server Error" })
          }
        }

        return PREDICTION_OK
      }

      return NOT_FOUND
    })

    vi.stubGlobal("fetch", fetchMock)

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Impossible de charger le résumé du jour/i)).toBeInTheDocument()
    })

    shouldFail = false
    await userEvent.click(screen.getByRole("button", { name: "Réessayer" }))

    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })

    expect(screen.getByText("Activités")).toBeInTheDocument()
  })

  it("localise les nouveaux libellés dashboard en anglais", async () => {
    localStorage.setItem("lang", "en")
    vi.stubGlobal("fetch", makeFetchMock())

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })

    expect(screen.getByText("Dashboard")).toBeInTheDocument()
    expect(screen.getByText("Activities")).toBeInTheDocument()
    expect(screen.getByText("Astrologer chat")).toBeInTheDocument()
    expect(screen.getByLabelText(/View full horoscope/i)).toBeInTheDocument()
  })

  it("utilise un fallback neutre quand le signe est absent des données de naissance", async () => {
    const birthMissingSign = {
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          astro_profile: { sun_sign_code: null },
          geolocation_consent: true
        }
      })
    }
    vi.stubGlobal("fetch", makeFetchMock(PREDICTION_OK, birthMissingSign))

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })

    // On vérifie que ça n'a pas crashé et que le canvas est là
    expect(document.querySelector('canvas')).toBeInTheDocument()
  })
})

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, exp: Math.floor(Date.now() / 1000) + 3600 }))
  setAccessToken(`header.${payload}.signature`)
}

function makeFetchMock(predictionResp = PREDICTION_OK, birthResp = BIRTH_DATA_OK) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
    if (url.includes("/v1/predictions/daily")) return predictionResp
    if (url.includes("/v1/birth-profiles/me") || url.includes("birth-data")) return birthResp
    return NOT_FOUND
  })
}

function renderDashboard() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  
  const router = createMemoryRouter(routes, {
    initialEntries: ["/dashboard"],
  })

  return {
    ...render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <RouterProvider router={router} />
        </ThemeProvider>
      </QueryClientProvider>
    ),
    router,
    queryClient
  }
}


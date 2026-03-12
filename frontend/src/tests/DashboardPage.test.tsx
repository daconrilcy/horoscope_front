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
    categories: [],
    timeline: [],
    turning_points: [],
  }),
}


const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
}

function makeFetchMock(predictionResponse: object = PREDICTION_OK) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
    if (url.includes("/v1/predictions/daily")) return predictionResponse
    return NOT_FOUND
  })
}

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, role: "user" }))
  setAccessToken(`x.${payload}.y`)
}

function renderDashboard() {
  const router = createMemoryRouter(routes, {
    initialEntries: ["/dashboard"],
    future: { v7_relativeSplatPath: true },
  })
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  })

  return {
    router,
    ...render(
      <ThemeProvider>
        <QueryClientProvider client={queryClient}>
          <RouterProvider router={router} future={{ v7_startTransition: true }} />
        </QueryClientProvider>
      </ThemeProvider>
    ),
  }
}

describe("DashboardPage Landing", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    setupToken()
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
    expect(screen.getByText("Tirage du jour")).toBeInTheDocument()
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

    // Le résumé est en loading (on peut chercher une classe ou un élément skeleton si on veut être précis)
    // Mais ici on vérifie surtout que Activités est là
    expect(screen.getByText("Activités")).toBeInTheDocument()
    
    resolvePrediction!(PREDICTION_OK)
    
    await waitFor(() => {
      expect(screen.getByText(/Une excellente journée vous attend/i)).toBeInTheDocument()
    })
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
})

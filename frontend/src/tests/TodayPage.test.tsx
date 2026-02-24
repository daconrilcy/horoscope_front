import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { createMemoryRouter, RouterProvider } from "react-router-dom"

import { setAccessToken } from "../utils/authToken"
import { routes } from "../app/routes"
import { STATIC_HOROSCOPE, TODAY_DATE_FORMATTER } from "../constants/horoscope"

beforeEach(() => {
  localStorage.setItem("lang", "fr")
  vi.stubGlobal("fetch", makeFetchMock())
  setupToken()
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

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

const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
}

function makeFetchMock(authMeResponse: object = AUTH_ME_USER) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return authMeResponse
    return NOT_FOUND
  })
}

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, role: "user" }))
  setAccessToken(`x.${payload}.y`)
}

function renderWithRouter(initialEntries: string[] = ["/dashboard"]) {
  const router = createMemoryRouter(routes, {
    initialEntries,
    future: { v7_relativeSplatPath: true },
  })
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  })
  return {
    router,
    ...render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} future={{ v7_startTransition: true }} />
      </QueryClientProvider>
    ),
  }
}

describe("TodayPage", () => {
  describe("AC1: Assemblage des composants dans le bon ordre", () => {
    it("affiche le header 'Aujourd'hui' / 'Horoscope' et respecte la hiérarchie H1 unique", async () => {
      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        // kicker text unique à TodayHeader
        const kickers = screen.getAllByText("Aujourd'hui")
        expect(kickers.length).toBeGreaterThanOrEqual(1)
        
        const h1s = screen.getAllByRole("heading", { level: 1 })
        expect(h1s).toHaveLength(1)
        expect(h1s[0]).toHaveTextContent("Horoscope")
      })
    })

    it("respecte l'ordre vertical de la spec §10.3", async () => {
      const { container } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByText("Horoscope")).toBeInTheDocument()
      })

      // On vérifie l'ordre dans le DOM
      const sections = container.querySelectorAll('.today-page > *')
      
      // 1. TodayHeader (via sa classe ou son contenu)
      expect(sections[0]).toHaveClass('today-header')
      // 2. HeroHoroscopeCard
      expect(sections[1]).toHaveClass('hero-card')
      // 3. ShortcutsSection
      expect(sections[2]).toHaveClass('shortcuts-section')
      // 4. DailyInsightsSection (section sans classe spécifique sur le wrapper mais avec id sur le titre)
      expect(sections[3].querySelector('#daily-insights-title')).toBeInTheDocument()
    })
  })

  describe("AC2: Données statiques conformes à la spec", () => {
    it("affiche le chip avec le signe Verseau et la date du jour", async () => {
      const expectedDate = TODAY_DATE_FORMATTER.format(new Date())
        .replace(/\.$/, '')

      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        const chip = screen.getByText(new RegExp(STATIC_HOROSCOPE.signName, "i"))
        expect(chip).toBeInTheDocument()
        expect(screen.getByText(new RegExp(expectedDate, "i"))).toBeInTheDocument()
      })
    })

    it("affiche le headline de la journée", async () => {
      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: STATIC_HOROSCOPE.headline })
        ).toBeInTheDocument()
      })
    })

    it("affiche la section Raccourcis avec les 2 cards", async () => {
      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByText("Chat astrologue")).toBeInTheDocument()
      })
      expect(screen.getByText("En ligne")).toBeInTheDocument()
      expect(screen.getByText("Tirage du jour")).toBeInTheDocument()
      expect(screen.getByText("3 cartes")).toBeInTheDocument()
    })

    it("affiche la section Insights avec les 3 mini cards et navigue au clic sur le header ou une card", async () => {
      const user = userEvent.setup()
      const { router, unmount } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByText("Amour")).toBeInTheDocument()
      })
      expect(screen.getByText("Travail")).toBeInTheDocument()
      expect(screen.getByText("Énergie")).toBeInTheDocument()

      // Test clic sur le header de section
      const sectionHeader = screen.getByRole("button", { name: /Insights du jour/i })
      await user.click(sectionHeader)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/natal")
      })

      // Reset et test clic sur une card individuelle
      unmount()
      const { router: router2 } = renderWithRouter(["/dashboard"])
      
      await waitFor(() => {
        expect(screen.getByText("Amour")).toBeInTheDocument()
      })
      
      const loveCard = screen.getByRole("button", { name: /Amour/i })
      await user.click(loveCard)

      await waitFor(() => {
        expect(router2.state.location.pathname).toBe("/natal")
      })
    })
  })

  describe("AC3: Navigation depuis HeroHoroscopeCard", () => {
    it("navigue vers /natal quand on clique sur 'Lire en 2 min'", async () => {
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: STATIC_HOROSCOPE.headline })
        ).toBeInTheDocument()
      })

      const cta = screen.getByRole("button", {
        name: /Lire l'horoscope complet en 2 minutes/i,
      })
      await user.click(cta)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/natal")
      })
    })

    it("navigue vers /natal quand on clique sur 'Version détaillée'", async () => {
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: STATIC_HOROSCOPE.headline })
        ).toBeInTheDocument()
      })

      const detailedBtn = screen.getByRole("button", {
        name: /Voir la version détaillée de l'horoscope/i,
      })
      await user.click(detailedBtn)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/natal")
      })
    })
  })

  describe("AC4: Navigation depuis ShortcutsSection", () => {
    it("navigue vers /chat quand on clique sur 'Chat astrologue'", async () => {
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByText("Chat astrologue")).toBeInTheDocument()
      })

      const chatBtn = screen.getByRole("link", { name: /Chat astrologue/i })
      await user.click(chatBtn)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/chat")
      })
    })

    it("navigue vers /consultations quand on clique sur 'Tirage du jour'", async () => {
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByText("Tirage du jour")).toBeInTheDocument()
      })

      const tirageBtn = screen.getByRole("link", { name: /Tirage du jour/i })
      await user.click(tirageBtn)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/consultations")
      })
    })
  })

  describe("AC5: Avatar avec nom utilisateur", () => {
    it("affiche les initiales de l'utilisateur connecté", async () => {
      vi.stubGlobal("fetch", makeFetchMock({
        ok: true,
        status: 200,
        json: async () => ({
          data: { id: 42, role: "user", email: "cyril@example.com", created_at: "2025-01-15T10:30:00Z" },
        }),
      }))

      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByLabelText("Profil de cyril")).toBeInTheDocument()
      })
    })

    it("génère des initiales correctes pour les emails avec points", async () => {
      vi.stubGlobal("fetch", makeFetchMock({
        ok: true,
        status: 200,
        json: async () => ({
          data: { email: "john.doe@example.com" },
        }),
      }))

      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByText("JD")).toBeInTheDocument()
      })
    })

    it("affiche un état d'erreur si l'API d'authentification échoue mais conserve le header", async () => {
      vi.stubGlobal("fetch", makeFetchMock({
        ok: false,
        status: 401,
        json: async () => ({ error: "unauthorized" }),
      }))

      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        // Le header doit rester visible
        expect(screen.getByText("Horoscope")).toBeInTheDocument()
        // Le message d'erreur s'affiche dans le corps
        expect(screen.getByText("Impossible de charger votre profil.")).toBeInTheDocument()
        expect(screen.getByRole("button", { name: "Réessayer" })).toBeInTheDocument()
      })
    })

    it("affiche un état de chargement (pulse avatar) pendant la récupération des données utilisateur", async () => {
      let resolveAuthMe: (value: unknown) => void
      const authMePromise = new Promise((resolve) => {
        resolveAuthMe = resolve
      })

      vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input)
        if (url.endsWith("/v1/auth/me")) return authMePromise
        return NOT_FOUND
      }))

      renderWithRouter(["/dashboard"])

      // Le header doit être présent et l'avatar en mode chargement
      expect(screen.getByLabelText("Chargement du profil")).toBeInTheDocument()

      resolveAuthMe!({
        ok: true,
        status: 200,
        json: async () => ({ data: { email: "cyril@example.com" } }),
      })

      await waitFor(() => {
        expect(screen.getByLabelText("Profil de cyril")).toBeInTheDocument()
      })
    })
  })
})

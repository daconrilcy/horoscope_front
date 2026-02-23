import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { createMemoryRouter, RouterProvider } from "react-router-dom"

import { setAccessToken, clearAccessToken } from "../utils/authToken"
import { routes } from "../app/routes"

beforeEach(() => {
  localStorage.setItem("lang", "fr")
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

describe("DashboardPage", () => {
  describe("AC1: Affichage du dashboard", () => {
    it("affiche le titre 'Tableau de bord' et les cartes de raccourci", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      expect(screen.getByText("Mon thème astral")).toBeInTheDocument()
      expect(screen.getByText("Chat astrologue")).toBeInTheDocument()
      expect(screen.getByText("Consultations")).toBeInTheDocument()
      expect(screen.getByText("Astrologues")).toBeInTheDocument()
      expect(screen.getByText("Paramètres")).toBeInTheDocument()
    })
  })

  describe("AC2: Cartes de navigation", () => {
    it("redirige vers /natal quand on clique sur 'Mon thème astral'", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      const natalCard = screen.getByRole("link", { name: /Aller à Mon thème astral/i })
      await user.click(natalCard)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/natal")
      })
    })

    it("redirige vers /chat quand on clique sur 'Chat astrologue'", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      const chatCard = screen.getByRole("link", { name: /Aller à Chat astrologue/i })
      await user.click(chatCard)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/chat")
      })
    })

    it("redirige vers /consultations quand on clique sur 'Consultations'", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      const card = screen.getByRole("link", { name: /Aller à Consultations/i })
      await user.click(card)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/consultations")
        expect(screen.getByRole("heading", { name: "Consultations" })).toBeInTheDocument()
      })
    })

    it("redirige vers /astrologers quand on clique sur 'Astrologues'", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      const card = screen.getByRole("link", { name: /Aller à Astrologues/i })
      await user.click(card)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/astrologers")
        expect(screen.getByRole("heading", { name: "Nos Astrologues" })).toBeInTheDocument()
      })
    })

    it("redirige vers /settings quand on clique sur 'Paramètres'", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      const card = screen.getByRole("link", { name: /Aller à Paramètres/i })
      await user.click(card)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/account")
        expect(screen.getByRole("heading", { name: "Paramètres" })).toBeInTheDocument()
      })
    })
  })

  describe("AC3: Accessibilité", () => {
    it("permet la navigation au clavier avec Tab entre les cartes", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      const firstCard = screen.getByRole("link", { name: "Aller à Mon thème astral" })
      const secondCard = screen.getByRole("link", { name: "Aller à Chat astrologue" })

      firstCard.focus()
      expect(document.activeElement).toBe(firstCard)

      await user.tab()
      expect(document.activeElement).toBe(secondCard)
    })

    it("permet d'activer une carte avec Enter", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      const natalCard = screen.getByRole("link", { name: /Aller à Mon thème astral/i })
      natalCard.focus()
      await user.keyboard("{Enter}")

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/natal")
      })
    })

    it("les cartes ont des aria-labels appropriés", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      expect(screen.getByRole("link", { name: "Aller à Mon thème astral" })).toBeInTheDocument()
      expect(screen.getByRole("link", { name: "Aller à Chat astrologue" })).toBeInTheDocument()
      expect(screen.getByRole("link", { name: "Aller à Consultations" })).toBeInTheDocument()
      expect(screen.getByRole("link", { name: "Aller à Astrologues" })).toBeInTheDocument()
      expect(screen.getByRole("link", { name: "Aller à Paramètres" })).toBeInTheDocument()
    })

    it("le nav a un aria-label 'Navigation principale'", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/dashboard"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
      })

      expect(screen.getByRole("navigation", { name: "Navigation principale" })).toBeInTheDocument()
    })
  })
})

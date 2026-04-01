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

const CATEGORIES_OK = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      categories: [
        { code: "bug", label: "Bug / dysfonctionnement", description: null },
        { code: "other", label: "Autre demande", description: null },
      ]
    }
  })
}

const TICKETS_OK = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      tickets: [
        {
          ticket_id: 1,
          category_code: "bug",
          subject: "Test Ticket",
          status: "pending",
          created_at: "2026-04-01T10:00:00Z",
          resolved_at: null
        }
      ],
      total: 1,
      limit: 20,
      offset: 0
    }
  })
}

const CREATE_TICKET_OK = {
  ok: true,
  status: 201,
  json: async () => ({
    data: {
      ticket_id: 2,
      category_code: "bug",
      subject: "New Ticket",
      status: "pending",
      created_at: "2026-04-01T11:00:00Z",
      resolved_at: null
    }
  })
}

const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
}

describe("HelpPage", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    setupToken()
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("affiche les sections d'aide et les catégories", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/help/categories")) return CATEGORIES_OK
      if (url.includes("/v1/help/tickets")) return TICKETS_OK
      return NOT_FOUND
    }))

    renderHelpPage()

    await waitFor(() => {
      expect(screen.getByText("Comment fonctionne l'application")).toBeInTheDocument()
      expect(screen.getByText("Bug / dysfonctionnement")).toBeInTheDocument()
      expect(screen.getByText("Test Ticket")).toBeInTheDocument()
    })
  })

  it("permet de soumettre un ticket", async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/help/categories")) return CATEGORIES_OK
      if (url.includes("/v1/help/tickets") && input instanceof Request && input.method === "POST") return CREATE_TICKET_OK
      if (url.includes("/v1/help/tickets")) return TICKETS_OK
      return NOT_FOUND
    })
    vi.stubGlobal("fetch", fetchMock)

    renderHelpPage()

    const categoryCard = await screen.findByText("Bug / dysfonctionnement")
    await user.click(categoryCard)

    expect(screen.getByText(/Catégorie : Bug \/ dysfonctionnement/i)).toBeInTheDocument()

    const subjectInput = screen.getByLabelText(/Objet de votre demande/i)
    const descInput = screen.getByLabelText(/Description détaillée/i)

    await user.type(subjectInput, "Problème test")
    await user.type(descInput, "Ceci est une description de test assez longue.")

    const submitBtn = screen.getByRole("button", { name: /Envoyer ma demande/i })
    await user.click(submitBtn)

    await waitFor(() => {
      expect(screen.queryByText(/Catégorie : Bug/i)).not.toBeInTheDocument()
    })
  })
})

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, exp: Math.floor(Date.now() / 1000) + 3600 }))
  setAccessToken(`header.${payload}.signature`)
}

function renderHelpPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  
  const router = createMemoryRouter(routes, {
    initialEntries: ["/help"],
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

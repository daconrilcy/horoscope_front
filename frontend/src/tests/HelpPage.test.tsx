import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { createMemoryRouter, RouterProvider } from "react-router-dom"

import { clearAccessToken, setAccessToken } from "../utils/authToken"
import { ThemeProvider } from "../state/ThemeProvider"
import { routes } from "../app/routes"

const helpApiMock = vi.hoisted(() => ({
  categories: [] as Array<{ code: string; label: string; description: string | null }>,
  tickets: {
    tickets: [] as Array<{
      ticket_id: number
      category_code: string
      subject: string
      description: string
      support_response: string | null
      status: string
      created_at: string
      updated_at: string
      resolved_at: string | null
    }>,
    total: 0,
    limit: 20,
    offset: 0,
  },
  createTicket: vi.fn(),
}))

vi.mock("@api/authMe", () => ({
  useAuthMe: () => ({
    data: {
      id: 42,
      role: "user",
      email: "test@example.com",
      created_at: "2025-01-15T10:30:00Z",
    },
    isLoading: false,
    isError: false,
    refetch: vi.fn(),
  }),
}))

vi.mock("@api/help", () => ({
  useHelpCategories: () => ({
    data: helpApiMock.categories,
    isLoading: false,
    isError: false,
    refetch: vi.fn(),
  }),
  useHelpTickets: () => ({
    data: helpApiMock.tickets,
    isLoading: false,
    isError: false,
    refetch: vi.fn(),
  }),
  useCreateHelpTicket: () => ({
    mutateAsync: helpApiMock.createTicket,
    isError: false,
    error: null,
  }),
}))

describe("HelpPage", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    setupToken()
    helpApiMock.categories = [
      { code: "bug", label: "Bug / dysfonctionnement", description: "Signalement d'un bug" },
      { code: "other", label: "Autre demande", description: null },
    ]
    helpApiMock.tickets = {
      tickets: [
        {
          ticket_id: 1,
          category_code: "bug",
          subject: "Test Ticket",
          description: "Mon problème détaillé",
          support_response: "Nous avons bien pris en charge votre demande.",
          status: "pending",
          created_at: "2026-04-01T10:00:00Z",
          updated_at: "2026-04-01T10:15:00Z",
          resolved_at: null,
        },
      ],
      total: 1,
      limit: 20,
      offset: 0,
    }
    helpApiMock.createTicket.mockReset()
    helpApiMock.createTicket.mockResolvedValue({
      ticket_id: 2,
      category_code: "bug",
      subject: "Bug / dysfonctionnement",
      description: "Ceci est une description de test assez longue.",
      support_response: null,
      status: "pending",
      created_at: "2026-04-01T11:00:00Z",
      updated_at: "2026-04-01T11:00:00Z",
      resolved_at: null,
    })
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
    localStorage.clear()
    clearAccessToken()
  })

  it("affiche le hero premium et les sections d'aide", async () => {
    renderHelpPage()

    expect(
      await screen.findByText("Comment pouvons-nous vous aider aujourd’hui ?", {}, { timeout: 5000 }),
    ).toBeInTheDocument()
    // Hero + liste tickets (empty CTA ou doublon layout) : même libellé accessible
    const openTicketCtas = screen.getAllByRole("button", { name: "Ouvrir un ticket support" })
    expect(openTicketCtas.length).toBeGreaterThan(0)

    expect(screen.getByText("Explorer les sections du site")).toBeInTheDocument()
    expect(screen.getByText("Horoscope")).toBeInTheDocument()
    expect(screen.getByText("Suivez votre météo astrale")).toBeInTheDocument()

    expect(screen.getByText("Fonctionnement des abonnements")).toBeInTheDocument()
    expect(screen.getByText("Que comprend mon abonnement")).toBeInTheDocument()
    expect(screen.getByText("Qu’est-ce qu’un token ?")).toBeInTheDocument()
    expect(screen.getByText("Chaque abonnement donne accès à un ensemble de fonctionnalités adapté à votre formule.")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Voir le détail des abonnements/i })).toHaveAttribute(
      "href",
      "/help/subscriptions",
    )

    expect(screen.getByText("Abonnement & Facturation")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Accéder à mon espace facturation/i })).toHaveAttribute(
      "href",
      "/settings/subscription",
    )

    expect(screen.getByText("Bug / dysfonctionnement")).toBeInTheDocument()
    expect(screen.getByText("Signalement d'un bug")).toBeInTheDocument()

    expect(screen.getByRole("heading", { level: 2, name: "Mes demandes" })).toBeInTheDocument()
    expect(await screen.findByText("Test Ticket", {}, { timeout: 5000 })).toBeInTheDocument()
    expect(
      await screen.findByText("Nous avons bien pris en charge votre demande.", {}, { timeout: 5000 }),
    ).toBeInTheDocument()
  })

  it("permet de soumettre un ticket et affiche un message de succès", async () => {
    const user = userEvent.setup()

    renderHelpPage()

    const categoryCard = await screen.findByRole("button", { name: /Bug \/ dysfonctionnement/i })
    await user.click(categoryCard)

    expect(screen.getAllByText("Bug / dysfonctionnement").length).toBeGreaterThan(0)

    const descInput = screen.getByLabelText(/Description détaillée/i)
    await user.type(descInput, "Ceci est une description de test assez longue.")

    expect(screen.getByText("Plus vous donnez de détails, plus vite nous pourrons vous aider.")).toBeInTheDocument()

    const submitBtn = screen.getByRole("button", { name: /Envoyer ma demande/i })
    await user.click(submitBtn)

    await waitFor(() => {
      expect(screen.queryByLabelText(/Description détaillée/i)).not.toBeInTheDocument()
      expect(
        screen.getByText("Votre demande a été envoyée avec succès. Notre équipe reviendra vers vous prochainement."),
      ).toBeInTheDocument()
    })
  })

  it("utilise le fallback i18n pour la description de catégorie si null dans l'API", async () => {
    renderHelpPage()

    await waitFor(() => {
      expect(screen.getByText("Toute autre demande non listée ci-dessus.")).toBeInTheDocument()
    })
  })

  it("affiche un CTA dans l'état vide des tickets", async () => {
    const scrollIntoViewMock = vi.fn()
    helpApiMock.tickets = {
      tickets: [],
      total: 0,
      limit: 20,
      offset: 0,
    }

    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
      configurable: true,
      value: scrollIntoViewMock,
    })

    renderHelpPage()

    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: "Ouvrir un ticket support" })).toHaveLength(2)
    })

    const emptyCta = screen.getAllByRole("button", { name: "Ouvrir un ticket support" })[1]
    fireEvent.click(emptyCta)

    expect(scrollIntoViewMock).toHaveBeenCalled()
  })
})

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, exp: Math.floor(Date.now() / 1000) + 3600 }))
  setAccessToken(`header.${payload}.signature`)
}

function renderHelpPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
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
      </QueryClientProvider>,
    ),
    router,
    queryClient,
  }
}

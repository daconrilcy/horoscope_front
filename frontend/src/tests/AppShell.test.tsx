import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { TestAppRouter } from "../app/router"
import { ThemeProvider } from "../state/ThemeProvider"
import { setAccessToken } from "../utils/authToken"

beforeEach(() => {
  localStorage.setItem("lang", "fr")
  localStorage.setItem("theme", "light")

  vi.stubGlobal("matchMedia", vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })))
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
  document.documentElement.classList.remove("dark")
})

const AUTH_ME_SUCCESS = {
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

const BILLING_SUBSCRIPTION = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      status: "active",
      plan: { code: "basic-entry", display_name: "Basic", monthly_price_cents: 500, currency: "EUR", daily_message_limit: 5, is_active: true },
      failure_reason: null,
      updated_at: "2026-01-01T00:00:00Z",
    },
  }),
}

const BILLING_QUOTA = {
  ok: true,
  status: 200,
  json: async () => ({
    data: { quota_date: "2026-02-23", limit: 5, consumed: 2, remaining: 3, reset_at: "2026-02-24T00:00:00Z", blocked: false },
  }),
}

const PRIVACY_EMPTY = {
  ok: true,
  status: 200,
  json: async () => ({ data: null }),
}

const DAILY_PREDICTION_SUCCESS = {
  ok: true,
  status: 200,
  json: async () => ({
    meta: {
      date_local: "2026-03-08",
      timezone: "Europe/Paris",
      computed_at: "2026-03-08T06:00:00Z",
      reference_version: "2026.03",
      ruleset_version: "1.0.0",
      was_reused: false,
      house_system_effective: "placidus",
    },
    summary: {
      overall_tone: "open",
      overall_summary: "Journee favorable pour prendre contact.",
      top_categories: ["love"],
      bottom_categories: ["energy"],
      best_window: null,
      main_turning_point: null,
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

function makeFetchMock() {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return AUTH_ME_SUCCESS
    if (url.includes("/v1/predictions/daily")) return DAILY_PREDICTION_SUCCESS
    if (url.endsWith("/v1/billing/subscription")) return BILLING_SUBSCRIPTION
    if (url.endsWith("/v1/billing/quota")) return BILLING_QUOTA
    if (url.endsWith("/v1/privacy/export")) return PRIVACY_EMPTY
    if (url.endsWith("/v1/privacy/delete")) return PRIVACY_EMPTY
    return NOT_FOUND
  })
}

function renderAppShell(initialEntries: string[] = ["/dashboard"]) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  })

  return render(
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <TestAppRouter initialEntries={initialEntries} />
      </QueryClientProvider>
    </ThemeProvider>,
  )
}

function setupAuthenticatedUser() {
  const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
  setAccessToken(`x.${payload}.y`)
  vi.stubGlobal("fetch", makeFetchMock())
}

describe("AppShell", () => {
  it("applique le cycle complet hidden -> expanded -> icon-only -> hidden", async () => {
    setupAuthenticatedUser()
    renderAppShell(["/dashboard"])

    const sidebar = document.querySelector(".app-sidebar")
    expect(sidebar).toHaveClass("app-sidebar--hidden")
    expect(document.querySelector(".sidebar-backdrop")).not.toBeInTheDocument()

    const hamburgerButton = screen.getByRole("button", { name: "Ouvrir le menu" })
    fireEvent.click(hamburgerButton)

    await waitFor(() => {
      expect(document.querySelector(".app-sidebar")).toHaveClass("app-sidebar--expanded")
      expect(document.querySelector(".sidebar-backdrop")).toBeInTheDocument()
    })

    fireEvent.click(screen.getAllByRole("link", { name: "Chat" })[0])

    await waitFor(() => {
      expect(document.querySelector(".app-sidebar")).toHaveClass("app-sidebar--icon-only")
      expect(document.querySelector(".sidebar-backdrop")).not.toBeInTheDocument()
      expect(document.querySelector(".app-shell-main")).toHaveClass("app-shell-main--with-sidebar-offset")
    })

    fireEvent.click(screen.getByRole("button", { name: "Fermer le menu" }))

    await waitFor(() => {
      expect(document.querySelector(".app-sidebar")).toHaveClass("app-sidebar--hidden")
      expect(document.querySelector(".app-shell-main")).not.toHaveClass("app-shell-main--with-sidebar-offset")
    })
  })

  it("ouvre et ferme le menu utilisateur puis permet la deconnexion", async () => {
    setupAuthenticatedUser()
    renderAppShell(["/dashboard"])

    const avatarButton = await screen.findByRole("button", { name: "Menu utilisateur" })
    fireEvent.click(avatarButton)

    await waitFor(() => {
      expect(screen.getByRole("menu")).toBeInTheDocument()
    })

    fireEvent.click(avatarButton)
    await waitFor(() => {
      expect(screen.queryByRole("menu")).not.toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: "Menu utilisateur" }))
    fireEvent.click(screen.getByRole("menuitem", { name: "Se déconnecter" }))

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument()
    })
  })

  it("bascule le theme dark/light depuis le header", async () => {
    setupAuthenticatedUser()
    renderAppShell(["/dashboard"])

    expect(document.documentElement).not.toHaveClass("dark")

    fireEvent.click(await screen.findByRole("button", { name: "Changer le thème" }))

    await waitFor(() => {
      expect(document.documentElement).toHaveClass("dark")
    })
  })
})

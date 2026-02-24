import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { clearAccessToken, setAccessToken } from "../utils/authToken"
import { TestAppRouter } from "../app/router"
import { STATIC_HOROSCOPE } from "../constants/horoscope"
import { ThemeProvider } from "../state/ThemeProvider"

beforeEach(() => {
  localStorage.setItem("lang", "fr")
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
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

const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
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

function makeFetchMock(withAuthMe = true) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (withAuthMe && url.endsWith("/v1/auth/me")) return AUTH_ME_SUCCESS
    if (url.endsWith("/v1/billing/subscription")) return BILLING_SUBSCRIPTION
    if (url.endsWith("/v1/billing/quota")) return BILLING_QUOTA
    if (url.endsWith("/v1/privacy/export")) return PRIVACY_EMPTY
    if (url.endsWith("/v1/privacy/delete")) return PRIVACY_EMPTY
    return NOT_FOUND
  })
}

function renderApp(initialEntries: string[] = ["/"]) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  })
  return render(
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <TestAppRouter initialEntries={initialEntries} />
      </QueryClientProvider>
    </ThemeProvider>
  )
}

describe("App", () => {
  it("redirects unauthenticated user from / to /login", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    localStorage.removeItem("access_token")
    
    renderApp(["/"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument()
    })
  })

  it("shows login form at /login when unauthenticated", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    localStorage.removeItem("access_token")
    
    renderApp(["/login"])
    
    expect(screen.getByLabelText("Adresse e-mail")).toBeInTheDocument()
    expect(screen.getByLabelText("Mot de passe")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Se connecter" })).toBeInTheDocument()
  })

  it("navigates from login to register when Créer un compte is clicked", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    localStorage.removeItem("access_token")
    
    renderApp(["/login"])
    
    fireEvent.click(screen.getByRole("button", { name: "Créer un compte" }))
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Créer un compte" })).toBeInTheDocument()
    })
  })

  it("navigates from register to login when Se connecter is clicked", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    localStorage.removeItem("access_token")
    
    renderApp(["/register"])
    
    expect(screen.getByRole("heading", { name: "Créer un compte" })).toBeInTheDocument()
    
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument()
    })
  })

  it("redirects authenticated user from / to /dashboard", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
    setAccessToken(`x.${payload}.y`)
    
    renderApp(["/"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: STATIC_HOROSCOPE.headline })).toBeInTheDocument()
    })
  })

  it("shows AppShell with sidebar for authenticated user", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
    setAccessToken(`x.${payload}.y`)
    
    renderApp(["/dashboard"])
    
    await waitFor(() => {
      expect(screen.getAllByRole("link", { name: "Chat" }).length).toBeGreaterThan(0)
    })
    expect(screen.getAllByRole("link", { name: "Profil" }).length).toBeGreaterThan(0)
    expect(screen.getAllByRole("link", { name: "Tirages" }).length).toBeGreaterThan(0)
  })

  it("redirects to login when logout button is clicked", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
    setAccessToken(`x.${payload}.y`)
    
    renderApp(["/dashboard"])
    
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Se déconnecter" })).toBeInTheDocument()
    })
    
    fireEvent.click(screen.getByRole("button", { name: "Se déconnecter" }))
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument()
    })
  })

  it("redirects unauthenticated user to login when accessing protected route", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    localStorage.removeItem("access_token")
    
    renderApp(["/chat"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument()
    })
  })
})

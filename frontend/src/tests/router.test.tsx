import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { createMemoryRouter, RouterProvider } from "react-router-dom"

import { setAccessToken, clearAccessToken } from "../utils/authToken"
import { TestAppRouter } from "../app/router"
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

const AUTH_ME_OPS = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      id: 1,
      role: "ops",
      email: "ops@example.com",
      created_at: "2025-01-01T00:00:00Z",
    },
  }),
}

const AUTH_ME_SUPPORT = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      id: 2,
      role: "support",
      email: "support@example.com",
      created_at: "2025-01-01T00:00:00Z",
    },
  }),
}

const AUTH_ME_ENTERPRISE = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      id: 3,
      role: "enterprise_admin",
      email: "enterprise@example.com",
      created_at: "2025-01-01T00:00:00Z",
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

function makeFetchMock(authMeResponse: object = AUTH_ME_USER) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return authMeResponse
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
    <QueryClientProvider client={queryClient}>
      <TestAppRouter initialEntries={initialEntries} />
    </QueryClientProvider>
  )
}

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, role: "user" }))
  setAccessToken(`x.${payload}.y`)
}

describe("AuthGuard", () => {
  it("redirects unauthenticated user to /login with returnTo", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    clearAccessToken()
    
    renderApp(["/dashboard"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument()
    })
  })

  it("allows authenticated user to access protected route", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    setupToken()
    
    renderApp(["/dashboard"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
    })
  })

  it("redirects to /login when accessing nested protected route without auth", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    clearAccessToken()
    
    renderApp(["/billing"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument()
    })
  })
})

describe("RoleGuard", () => {
  it("redirects non-ops user from /admin to /dashboard", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_USER))
    setupToken()
    
    renderApp(["/admin/monitoring"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
    })
  })

  it("allows ops user to access /admin routes", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    
    renderApp(["/admin/monitoring"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Administration/i })).toBeInTheDocument()
    })
  })

  it("allows support user to access /support route", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_SUPPORT))
    setupToken("2")
    
    renderApp(["/support"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Support/i })).toBeInTheDocument()
    })
  })

  it("redirects regular user from /support to /dashboard", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_USER))
    setupToken()
    
    renderApp(["/support"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
    })
  })

  it("redirects non-enterprise user from /enterprise to /dashboard", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_USER))
    setupToken()
    
    renderApp(["/enterprise/credentials"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
    })
  })

  it("allows enterprise_admin to access /enterprise routes", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ENTERPRISE))
    setupToken("3")
    
    renderApp(["/enterprise/credentials"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Espace Entreprise/i })).toBeInTheDocument()
    })
  })
})

describe("RootRedirect", () => {
  it("redirects / to /login when unauthenticated", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    clearAccessToken()
    
    renderApp(["/"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument()
    })
  })

  it("redirects / to /dashboard when authenticated", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    setupToken()
    
    renderApp(["/"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
    })
  })
})

describe("Navigation", () => {
  it("navigates between routes using sidebar links", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    setupToken()
    const user = userEvent.setup()
    
    renderApp(["/dashboard"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
    })
    
    const chatLinks = screen.getAllByRole("link", { name: /Chat/i })
    await user.click(chatLinks[0])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Aucune conversation|No conversation/i })).toBeInTheDocument()
    })
  })

  it("supports browser back/forward navigation", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    setupToken()
    const user = userEvent.setup()
    
    const router = createMemoryRouter(routes, {
      initialEntries: ["/dashboard"],
      future: { v7_relativeSplatPath: true },
    })
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    })
    
    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} future={{ v7_startTransition: true }} />
      </QueryClientProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
    })
    
    const chatLinks = screen.getAllByRole("link", { name: /Chat/i })
    await user.click(chatLinks[0])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Aucune conversation|No conversation/i })).toBeInTheDocument()
    })
    
    router.navigate(-1)
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Tableau de bord" })).toBeInTheDocument()
    })
    
    router.navigate(1)
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Aucune conversation|No conversation/i })).toBeInTheDocument()
    })
  })

  it("preserves returnTo parameter through login flow", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    clearAccessToken()
    const user = userEvent.setup()
    
    const router = createMemoryRouter(routes, {
      initialEntries: ["/chat"],
      future: { v7_relativeSplatPath: true },
    })
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    })
    
    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} future={{ v7_startTransition: true }} />
      </QueryClientProvider>
    )
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument()
    })
    
    const registerButton = screen.getByRole("button", { name: /créer un compte/i })
    await user.click(registerButton)
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Créer un compte" })).toBeInTheDocument()
    })
    
    expect(router.state.location.pathname).toBe("/register")
    expect(router.state.location.search).toContain("returnTo")
    expect(router.state.location.search).toContain("%2Fchat")
  })
})

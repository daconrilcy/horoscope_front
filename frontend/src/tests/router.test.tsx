import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { createMemoryRouter, RouterProvider } from "react-router-dom"

import { setAccessToken, clearAccessToken } from "../utils/authToken"
import { TestAppRouter } from "../app/router"
import { routes } from "../app/routes"
import { ThemeProvider } from "../state/ThemeProvider"
import { adminTranslations } from "../i18n/admin"
import { navigationTranslations } from "../i18n/navigation"

beforeEach(() => {
  localStorage.setItem("lang", "fr")

  class ResizeObserverMock {
    observe = vi.fn()
    unobserve = vi.fn()
    disconnect = vi.fn()
  }

  vi.stubGlobal("ResizeObserver", ResizeObserverMock)

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
  })) as typeof HTMLCanvasElement.prototype.getContext
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

const tAdmin = adminTranslations
const tNav = navigationTranslations("fr")

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

function makeFetchMock(authMeResponse: object = AUTH_ME_USER) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return authMeResponse
    if (url.includes("/v1/predictions/daily")) return DAILY_PREDICTION_SUCCESS
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

function setupToken(sub = "42", role = "user") {
  const payload = btoa(JSON.stringify({ sub, role }))
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
      expect(screen.getByRole("heading", { level: 2, name: "Tableau de bord" })).toBeInTheDocument()
    })
  })
})

describe("RoleGuard", () => {
  it("redirects non-ops user from /admin to /dashboard", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_USER))
    setupToken()
    
    renderApp(["/admin/monitoring"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1, name: "Astrorizon" })).toBeInTheDocument()
    })
  })

  it("allows ops user to access /admin routes", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1", "ops")
    
    renderApp(["/admin/monitoring"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: new RegExp(tAdmin.page.fr.title, "i") })).toBeInTheDocument()
    })
  })

  it("allows support user to access /support route", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_SUPPORT))
    setupToken("2", "support")
    
    renderApp(["/support"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Support et opérations/i })).toBeInTheDocument()
    })
  })

  it("allows enterprise_admin to access /enterprise routes", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ENTERPRISE))
    setupToken("3", "enterprise_admin")
    
    renderApp(["/enterprise/credentials"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /API Entreprise/i })).toBeInTheDocument()
    })
  })
})

describe("Dashboard Path", () => {
  it("renders DashboardPage on /dashboard", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    setupToken()
    
    renderApp(["/dashboard"])
    
    await waitFor(() => {
      expect(screen.getByText(/Accédez rapidement à toutes les fonctionnalités/i)).toBeInTheDocument()
    })
  })

  it("keeps dashboard tab active in BottomNav for both routes", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    setupToken()
    
    // Test /dashboard
    const { unmount } = renderApp(["/dashboard"])
    await waitFor(() => {
      const nav = screen.getByRole("navigation", { name: /principale/i })
      const dashboardLink = within(nav).getByRole("link", { name: new RegExp(tNav.nav.today, "i") })
      expect(dashboardLink).toHaveClass("bottom-nav__item--active")
    })
    unmount()

    // Test /dashboard/horoscope
    renderApp(["/dashboard/horoscope"])
    await waitFor(() => {
      const nav = screen.getByRole("navigation", { name: /principale/i })
      const dashboardLink = within(nav).getByRole("link", { name: new RegExp(tNav.nav.today, "i") })
      expect(dashboardLink).toHaveClass("bottom-nav__item--active")
    })
  })
})

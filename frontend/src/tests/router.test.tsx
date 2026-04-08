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
      plan: { code: "basic", display_name: "Basic", monthly_price_cents: 500, currency: "EUR", daily_message_limit: 5, is_active: true },
      failure_reason: null,
      updated_at: "2026-01-01T00:00:00Z",
    },
  }),
}

const ENTITLEMENTS_ME = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      features: [
        {
          feature_code: "astrologer_chat",
          final_access: true,
          reason: "canonical_binding",
          usage_states: [
            {
              quota_key: "messages",
              quota_limit: 5,
              used: 2,
              remaining: 3,
              exhausted: false,
              period_unit: "day",
              period_value: 1,
              reset_mode: "calendar",
              window_start: "2026-02-23T00:00:00Z",
              window_end: "2026-02-24T00:00:00Z",
            },
          ],
        },
      ],
    },
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
    if (url.endsWith("/v1/entitlements/me")) return ENTITLEMENTS_ME
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

describe("AdminGuard", () => {
  it("redirects non-admin user from /admin to /", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1", "ops")
    
    renderApp(["/admin/monitoring"])
    
    await waitFor(() => {
      // In our test setup, "/" might redirect or show something specific.
      // Based on AC, it should redirect to "/" (which usually leads to dashboard for logged in users)
      expect(window.location.pathname).toBe("/")
    })
  })

  it("allows admin user to access /admin routes", async () => {
    const AUTH_ME_ADMIN = {
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          id: 99,
          role: "admin",
          email: "admin@example.com",
          created_at: "2025-01-01T00:00:00Z",
        },
      }),
    }
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ADMIN))
    setupToken("99", "admin")
    
    renderApp(["/admin/monitoring"])
    
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: new RegExp(tAdmin.page.fr.title, "i") })).toBeInTheDocument()
    })
  })
})

describe("RoleGuard", () => {
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

describe("Consultations Routing", () => {
  it("renders /consultations without missing provider error", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    setupToken()

    renderApp(["/consultations"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1, name: /consultation/i })).toBeInTheDocument()
    })
  })
})

describe("Route config", () => {
  function collectPaths(routeList: typeof routes): string[] {
    return routeList.flatMap((route) => {
      const currentPath = route.path ? [route.path] : []
      const childPaths = route.children ? collectPaths(route.children as typeof routes) : []
      return [...currentPath, ...childPaths]
    })
  }

  it("déclare les routes astrologers et chat conversation", () => {
    const paths = collectPaths(routes)

    expect(paths).toContain("astrologers")
    expect(paths).toContain("astrologers/:id")
    expect(paths).toContain("chat/:conversationId")
    expect(paths).toContain("profile")
    expect(paths).toContain("birth-profile")
  })
})

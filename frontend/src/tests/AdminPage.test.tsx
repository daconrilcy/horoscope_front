import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { afterEach, describe, expect, it, vi, beforeEach } from "vitest"

import { TestAppRouter } from "../app/router"
import { setAccessToken, clearAccessToken } from "../utils/authToken"
import { ThemeProvider } from "../state/ThemeProvider"
import { adminTranslations } from "../i18n/admin"

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
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
  clearAccessToken()
})

const t = adminTranslations
const fr = t.page.fr
const frSec = t.sections.fr

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

const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
}

function makeFetchMock(authMeResponse: object) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return authMeResponse
    if (url.includes("/v1/billing/subscription")) return { ok: true, status: 200, json: async () => ({ data: null }) }
    if (url.includes("/v1/entitlements/me")) return { ok: true, status: 200, json: async () => ({ data: { features: [] } }) }
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

function setupToken(sub = "1", role = "admin") {
  const payload = btoa(JSON.stringify({ sub, role }))
  setAccessToken(`x.${payload}.y`)
}

describe("AdminPage - Story 65.4", () => {
  it("redirects non-admin user (user) from /admin to dashboard", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_USER))
    setupToken("42", "user")

    renderApp(["/admin"])

    await waitFor(() => {
      expect(screen.getByText(/Accédez rapidement à toutes les fonctionnalités/i)).toBeInTheDocument()
    })
  })

  it("redirects non-admin user (ops) from /admin to /", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1", "ops")

    renderApp(["/admin"])

    await waitFor(() => {
      expect(window.location.pathname).toBe("/")
    })
  })

  it("allows admin user to access /admin hub", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ADMIN))
    setupToken("99", "admin")

    renderApp(["/admin"])

    await waitFor(() => {
      // Check for AdminLayout's sidebar link (the logo)
      expect(screen.getByRole("link", { name: fr.title })).toBeInTheDocument()
      // Check for Hub grid presence
      expect(screen.getByRole("region", { name: /Hub d'administration/i })).toBeInTheDocument()
    }, { timeout: 2000 })
  })

  it("displays 10 sections in the sidebar for admin", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ADMIN))
    setupToken("99", "admin")

    renderApp(["/admin/dashboard"])

    await waitFor(() => {
      const sidebarNav = screen.getByRole("navigation", { name: /Sections d'administration/i })
      expect(sidebarNav).toBeInTheDocument()

      const sections = [
        frSec.dashboard,
        frSec.users,
        frSec.entitlements,
        frSec.ai_generations,
        frSec.prompts,
        frSec.content,
        frSec.billing,
        frSec.logs,
        frSec.support,
        frSec.settings,
      ]

      sections.forEach(label => {
        expect(within(sidebarNav).getByRole("link", { name: new RegExp(label, "i") })).toBeInTheDocument()
      })
    })
  })

  it("redirects legacy routes to new ones", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ADMIN))
    setupToken("99", "admin")

    // Test /admin/monitoring -> should render Logs page content
    const { unmount } = renderApp(["/admin/monitoring"])
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Logs & Incidents" })).toBeInTheDocument()
    })
    unmount()

    // Test /admin/personas -> should render Prompts page content
    renderApp(["/admin/personas"])
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Prompts & Personas" })).toBeInTheDocument()
    })
  })
})

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { createMemoryRouter, RouterProvider } from "react-router-dom"

import { setAccessToken } from "../utils/authToken"
import { routes } from "../app/routes"
import { settingsTranslations } from "../i18n/settings"

beforeEach(() => {
  localStorage.setItem("lang", "fr")
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

const t = settingsTranslations
const fr = t.page.fr
const frTabs = t.tabs.fr
const frAcc = t.account.fr

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

const BILLING_SUBSCRIPTION = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      status: "active",
      plan: {
        code: "basic-entry",
        display_name: "Basic",
        monthly_price_cents: 500,
        currency: "EUR",
        daily_message_limit: 5,
        is_active: true,
      },
      failure_reason: null,
      updated_at: "2026-01-01T00:00:00Z",
      is_active: true,
    },
  }),
}

const BILLING_QUOTA = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      quota_date: "2026-02-23",
      limit: 5,
      consumed: 2,
      remaining: 3,
      reset_at: "2026-02-24T00:00:00Z",
      blocked: false,
    },
  }),
}

const EXPORT_STATUS_NONE = {
  ok: true,
  status: 200,
  json: async () => ({ data: null }),
}

const DELETE_STATUS_NONE = {
  ok: true,
  status: 200,
  json: async () => ({ data: null }),
}

const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
}

function makeFetchMock(overrides: Record<string, object> = {}) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return overrides.authMe ?? AUTH_ME_USER
    if (url.endsWith("/v1/billing/subscription")) return overrides.subscription ?? BILLING_SUBSCRIPTION
    if (url.endsWith("/v1/billing/quota")) return overrides.quota ?? BILLING_QUOTA
    if (url.endsWith("/v1/privacy/export")) return overrides.exportStatus ?? EXPORT_STATUS_NONE
    if (url.endsWith("/v1/privacy/delete")) return overrides.deleteStatus ?? DELETE_STATUS_NONE
    return NOT_FOUND
  })
}

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, role: "user" }))
  setAccessToken(`x.${payload}.y`)
}

function renderWithRouter(initialEntries: string[] = ["/settings"]) {
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

describe("SettingsPage", () => {
  describe("AC1: Navigation settings", () => {
    it("affiche les onglets Compte, Abonnement, Usage", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/settings"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
      })

      const nav = screen.getByRole("navigation", { name: frTabs.navLabel })
      expect(within(nav).getByRole("link", { name: frTabs.account })).toBeInTheDocument()
      expect(within(nav).getByRole("link", { name: frTabs.subscription })).toBeInTheDocument()
      expect(within(nav).getByRole("link", { name: frTabs.usage })).toBeInTheDocument()
    })

    it("redirige vers /settings/account par défaut", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      const { router } = renderWithRouter(["/settings"])

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/account")
      })
    })

    it("navigue entre les onglets", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/settings"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
      })

      const subscriptionTab = screen.getByRole("link", { name: frTabs.subscription })
      await user.click(subscriptionTab)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/subscription")
      })

      const usageTab = screen.getByRole("link", { name: frTabs.usage })
      await user.click(usageTab)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/usage")
      })
    })
  })

  describe("AC2: Page compte", () => {
    it("affiche les informations du compte", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByText(frAcc.title)).toBeInTheDocument()
        expect(screen.getByText(frAcc.email)).toBeInTheDocument()
      })

      expect(screen.getByText("test@example.com")).toBeInTheDocument()
      expect(screen.getByText(frAcc.memberSince)).toBeInTheDocument()
      expect(screen.getByText(frAcc.role)).toBeInTheDocument()
    })
  })

  describe("AC4: Page abonnement", () => {
    it("affiche le BillingPanel avec le plan actuel", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/settings/subscription"])

      await waitFor(() => {
        expect(screen.getByText("Mon abonnement")).toBeInTheDocument()
      })

      await waitFor(() => {
        expect(screen.getByText(/Abonnement actif./)).toBeInTheDocument()
      })
    })
  })
})

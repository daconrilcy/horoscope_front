import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
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

const SUBSCRIPTION_BASIC = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      status: "active",
      plan: { code: "basic", display_name: "Basic", monthly_price_cents: 900, currency: "EUR" },
    },
  }),
}

const PLANS_OK = {
  ok: true,
  status: 200,
  json: async () => ({
    data: [
      {
        plan_code: "free",
        plan_name: "Free",
        monthly_price_cents: 0,
        currency: "EUR",
        is_active: true,
        features: [
          {
            feature_code: "natal_chart_short",
            feature_name: "Thème natal",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
        ],
      },
      {
        plan_code: "basic",
        plan_name: "Basic",
        monthly_price_cents: 900,
        currency: "EUR",
        is_active: true,
        features: [
          {
            feature_code: "natal_chart_short",
            feature_name: "Thème natal",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
          {
            feature_code: "natal_chart_long",
            feature_name: "Thème natal (long)",
            is_enabled: true,
            access_mode: "quota",
            quotas: [
              {
                quota_key: "interpretations",
                quota_limit: 1,
                period_unit: "lifetime",
                period_value: 0,
                reset_mode: "lifetime",
              },
            ],
          },
        ],
      },
      {
        plan_code: "premium",
        plan_name: "Premium",
        monthly_price_cents: 2900,
        currency: "EUR",
        is_active: true,
        features: [
          {
            feature_code: "natal_chart_short",
            feature_name: "Thème natal",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
        ],
      },
    ],
    meta: { request_id: "test-request-id" },
  }),
}

const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
}

describe("SubscriptionGuidePage", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    setupToken()
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("affiche les 3 cartes de plans et identifie le plan actuel", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/entitlements/plans")) return PLANS_OK
      if (url.includes("/v1/billing/subscription")) return SUBSCRIPTION_BASIC
      return NOT_FOUND
    }))

    renderSubscriptionGuidePage()

    await waitFor(() => {
      // Hero title
      expect(screen.getByText("Choisissez la formule qui vous ressemble")).toBeInTheDocument()
      
      const main = screen.getByRole("main")

      // Plans display
      expect(within(main).getByText("Free")).toBeInTheDocument()
      expect(within(main).getByText("Basic")).toBeInTheDocument()
      expect(within(main).getByText("Premium")).toBeInTheDocument()

      // Current plan badge
      expect(within(main).getByText("Votre plan actuel")).toBeInTheDocument()

      // Features list
      expect(within(main).getAllByText("Thème natal (court)")).toHaveLength(3)
      expect(within(main).getByText("Thème natal (détaillé)")).toBeInTheDocument()
      expect(within(main).getByText("1 interprétations incluses")).toBeInTheDocument()

      // Prices
      expect(within(main).getByText("0 €")).toBeInTheDocument()
      expect(within(main).getByText("9 €")).toBeInTheDocument()
      expect(within(main).getByText("29 €")).toBeInTheDocument()

      // CTA check
      const manageCtas = within(main).getAllByRole("link", { name: /Gérer|Passer à ce plan/i })
      expect(manageCtas[0]).toHaveAttribute("href", "/settings/subscription")
    })
  })

  it("affiche l'état d'erreur en cas d'échec de l'API", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/entitlements/plans")) return NOT_FOUND
      if (url.includes("/v1/billing/subscription")) return SUBSCRIPTION_BASIC
      return NOT_FOUND
    }))

    renderSubscriptionGuidePage()

    await waitFor(() => {
      expect(screen.getByText("Erreur")).toBeInTheDocument()
    })
  })

  it("affiche l'état vide si aucun plan n'est retourné", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/entitlements/plans")) {
        return {
          ok: true,
          status: 200,
          json: async () => ({ data: [], meta: { request_id: "empty" } }),
        }
      }
      if (url.includes("/v1/billing/subscription")) return SUBSCRIPTION_BASIC
      return NOT_FOUND
    }))

    renderSubscriptionGuidePage()

    await waitFor(() => {
      expect(screen.getByText("Aucune donnée disponible")).toBeInTheDocument()
    })
  })
})

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, exp: Math.floor(Date.now() / 1000) + 3600 }))
  setAccessToken(`header.${payload}.signature`)
}

function renderSubscriptionGuidePage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  const router = createMemoryRouter(routes, {
    initialEntries: ["/help/subscriptions"],
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

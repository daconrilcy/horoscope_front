import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { createMemoryRouter, RouterProvider } from "react-router-dom"

import { setAccessToken } from "../utils/authToken"
import { ThemeProvider } from "../state/ThemeProvider"
import { routerFutureFlags, routerProviderFutureFlags } from "./test-utils"
import { SubscriptionGuidePage } from "../pages/SubscriptionGuidePage"

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

const ENTITLEMENTS_ME_BASIC = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      plan_code: "basic",
      billing_status: "active",
      features: [],
    },
  }),
}

const ENTITLEMENTS_ME_FREE = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      plan_code: "free",
      billing_status: "active",
      features: [],
    },
  }),
}

const SUBSCRIPTION_FREE = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      status: "inactive",
      plan: null,
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
        processing_priority: "low",
        features: [
          {
            feature_code: "natal_astral",
            feature_name: "Thème natal",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
          {
            feature_code: "horoscope_daily",
            feature_name: "Horoscope quotidien",
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
        processing_priority: "medium",
        features: [
          {
            feature_code: "natal_astral",
            feature_name: "Thème natal",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
          {
            feature_code: "natal_astral_full",
            feature_name: "Interprétation complète du thème natal",
            is_enabled: true,
            access_mode: "quota",
            quotas: [
              {
                quota_key: "interpretations",
                quota_limit: 1,
                period_unit: "lifetime",
                period_value: 1,
                reset_mode: "lifetime",
              },
            ],
          },
          {
            feature_code: "horoscope_daily",
            feature_name: "Horoscope quotidien",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
        ],
      },
      {
        plan_code: "premium",
        plan_name: "Premium",
        monthly_price_cents: 2900,
        currency: "EUR",
        is_active: true,
        processing_priority: "high",
        features: [
          {
            feature_code: "natal_astral",
            feature_name: "Thème natal",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
          {
            feature_code: "natal_astral_full",
            feature_name: "Thème natal (long)",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
          {
            feature_code: "horoscope_daily",
            feature_name: "Horoscope quotidien",
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

let activeQueryClient: QueryClient | null = null

describe("SubscriptionGuidePage", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    setupToken()
  })

  afterEach(() => {
    cleanup()
    activeQueryClient?.clear()
    activeQueryClient = null
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("affiche les 3 cartes de plans et identifie le plan actuel avec priorité", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/entitlements/plans")) return PLANS_OK
      if (url.includes("/v1/entitlements/me")) return ENTITLEMENTS_ME_BASIC
      if (url.includes("/v1/billing/subscription")) return SUBSCRIPTION_BASIC
      return NOT_FOUND
    }))

    renderSubscriptionGuidePage()

    expect(await screen.findByText("Choisissez l’expérience astrologique qui vous correspond")).toBeInTheDocument()
    expect(screen.getByText(/Notre approche de l’astrologie ne se limite pas à des réponses automatiques/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Gérer mon abonnement" })).toHaveAttribute("href", "/settings/subscription")
    expect(screen.getByRole("link", { name: "Comparer les offres" })).toHaveAttribute("href", "#subscription-plans")
    expect(screen.getByText("Repères rapides")).toBeInTheDocument()
    expect(screen.getByText("Votre plan actuel : Basic")).toBeInTheDocument()

    const main = document.querySelector(".page-layout__main") as HTMLElement
    expect(main).not.toBeNull()
    expect(within(main).getByText("Free")).toBeInTheDocument()
    expect(within(main).getByText("Basic")).toBeInTheDocument()
    expect(within(main).getByText("Premium")).toBeInTheDocument()
    const basicCard = within(main).getByText("Basic").closest(".subscription-plan-card")
    expect(basicCard).not.toBeNull()
    expect(basicCard).toHaveClass("subscription-plan-card--featured")
    expect(within(main).getByText("Horoscope quotidien inclus")).toBeInTheDocument()
    expect(within(main).getByText("Horoscope quotidien complet")).toBeInTheDocument()

    const detailToggles = within(main).getAllByText("Explorer les détails")
    expect(detailToggles).toHaveLength(3)
    detailToggles.forEach((toggle) => {
      fireEvent.click(toggle)
    })
    expect(within(main).getByText("Comment choisir")).toBeInTheDocument()
    expect(within(main).getByText("Comment fonctionnent les tokens ?")).toBeInTheDocument()
  })

  it("identifie correctement le plan free comme plan actuel", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/entitlements/plans")) return PLANS_OK
      if (url.includes("/v1/entitlements/me")) return ENTITLEMENTS_ME_FREE
      if (url.includes("/v1/billing/subscription")) return SUBSCRIPTION_FREE
      return NOT_FOUND
    }))

    renderSubscriptionGuidePage()

    expect(await screen.findByText("Votre plan actuel : Free")).toBeInTheDocument()
    const main = document.querySelector(".page-layout__main") as HTMLElement
    expect(main).not.toBeNull()
    const freeCard = within(main).getByText("Free").closest(".subscription-plan-card")
    expect(freeCard).not.toBeNull()
    expect(within(freeCard as HTMLElement).getByText("Votre plan actuel")).toBeInTheDocument()
    expect(within(freeCard as HTMLElement).queryByRole("link", { name: "Passer à ce plan" })).not.toBeInTheDocument()
  })

  it("affiche l'état d'erreur en cas d'échec de l'API", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) return AUTH_ME_USER
      if (url.includes("/v1/entitlements/plans")) return NOT_FOUND
      if (url.includes("/v1/entitlements/me")) return ENTITLEMENTS_ME_BASIC
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
      if (url.includes("/v1/entitlements/me")) return ENTITLEMENTS_ME_BASIC
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
  activeQueryClient = queryClient

  const router = createMemoryRouter(
    [
      {
        path: "/help/subscriptions",
        element: <SubscriptionGuidePage />,
      },
      {
        path: "/settings/subscription",
        element: <div>Subscription settings</div>,
      },
    ],
    {
    initialEntries: ["/help/subscriptions"],
    future: routerFutureFlags,
    },
  )

  return {
    ...render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <RouterProvider router={router} future={routerProviderFutureFlags} />
        </ThemeProvider>
      </QueryClientProvider>,
    ),
    router,
    queryClient,
  }
}

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react"
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
            feature_code: "natal_chart_short",
            feature_name: "Thème natal",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
          {
            feature_code: "natal_chart_long",
            feature_name: "Thème natal (long)",
            is_enabled: false,
            access_mode: "disabled",
            quotas: [],
          },
          {
            feature_code: "astrologer_chat",
            feature_name: "Chat astrologique",
            is_enabled: true,
            access_mode: "quota",
            quotas: [
              {
                quota_key: "messages",
                quota_limit: 1,
                period_unit: "week",
                period_value: 1,
                reset_mode: "calendar",
              },
            ],
          },
          {
            feature_code: "thematic_consultation",
            feature_name: "Consultations thématiques",
            is_enabled: false,
            access_mode: "disabled",
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
            feature_code: "natal_chart_short",
            feature_name: "Thème natal",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
          {
            feature_code: "natal_chart_long",
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
            feature_code: "astrologer_chat",
            feature_name: "Chat astrologique",
            is_enabled: true,
            access_mode: "quota",
            quotas: [
              {
                quota_key: "tokens",
                quota_limit: 50000,
                period_unit: "month",
                period_value: 1,
                reset_mode: "calendar",
              },
            ],
          },
          {
            feature_code: "thematic_consultation",
            feature_name: "Consultations thématiques",
            is_enabled: true,
            access_mode: "quota",
            quotas: [
              {
                quota_key: "tokens",
                quota_limit: 20000,
                period_unit: "week",
                period_value: 1,
                reset_mode: "calendar",
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
        processing_priority: "high",
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
            access_mode: "unlimited",
            quotas: [],
          },
          {
            feature_code: "astrologer_chat",
            feature_name: "Chat astrologique",
            is_enabled: true,
            access_mode: "unlimited",
            quotas: [],
          },
          {
            feature_code: "thematic_consultation",
            feature_name: "Consultations thématiques",
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

    await waitFor(() => {
      expect(screen.getByText("Choisissez l’expérience astrologique qui vous correspond")).toBeInTheDocument()
      expect(
        screen.getByText(/Notre approche de l’astrologie ne se limite pas à des réponses automatiques/),
      ).toBeInTheDocument()
      expect(screen.getByRole("link", { name: "Gérer mon abonnement" })).toHaveAttribute("href", "/settings/subscription")
      expect(screen.getByRole("link", { name: "Comparer les offres" })).toHaveAttribute("href", "#subscription-plans")
      expect(screen.getByText("Repères rapides")).toBeInTheDocument()
      expect(screen.getByText("Votre plan actuel : Basic")).toBeInTheDocument()
      expect(screen.getByText("À partir de 0 €")).toBeInTheDocument()

      const main = screen.getByRole("main")

      expect(within(main).getByText("Free")).toBeInTheDocument()
      expect(within(main).getByText("Basic")).toBeInTheDocument()
      expect(within(main).getByText("Premium")).toBeInTheDocument()

      expect(within(main).getByText("Découverte")).toBeInTheDocument()
      expect(within(main).getByText("Usage régulier")).toBeInTheDocument()
      expect(within(main).getByText("Expérience complète")).toBeInTheDocument()
      expect(within(main).getByText("Pour explorer l’essentiel, en toute simplicité.")).toBeInTheDocument()
      expect(within(main).getByText("Votre compagnon astrologique du quotidien.")).toBeInTheDocument()
      expect(within(main).getByText("La version la plus fluide, la plus profonde, la plus généreuse.")).toBeInTheDocument()

      expect(within(main).getByText("Traitement standard")).toBeInTheDocument()
      expect(within(main).getByText("Traitement prioritaire")).toBeInTheDocument()
      expect(within(main).getByText("Traitement haute priorité")).toBeInTheDocument()

      expect(within(main).getByText("Votre plan actuel")).toBeInTheDocument()
      const basicCard = within(main).getByText("Basic").closest(".subscription-plan-card")
      expect(basicCard).not.toBeNull()
      expect(basicCard).toHaveClass("subscription-plan-card--featured")
      expect(within(basicCard as HTMLElement).queryByText("Le plus choisi")).not.toBeInTheDocument()
      expect(within(main).getAllByText("Horoscope du jour enrichi")).toHaveLength(2)
      expect(within(main).getByText("1 message de chat par semaine")).toBeInTheDocument()
      expect(within(main).getByText("Chat astrologique inclus")).toBeInTheDocument()
      expect(within(main).getByText("Chat astrologique complet")).toBeInTheDocument()
      expect(within(main).getByText("Pour découvrir")).toBeInTheDocument()
      expect(within(main).getByText("Pour un usage quotidien")).toBeInTheDocument()
      expect(within(main).getByText("Pour une expérience complète")).toBeInTheDocument()
      const detailToggles = within(main).getAllByText("Explorer les détails")
      expect(detailToggles).toHaveLength(3)
      detailToggles.forEach((toggle) => {
        fireEvent.click(toggle)
      })

      expect(within(main).getAllByText("Thème natal")).toHaveLength(3)
      expect(within(main).getAllByText("Interprétation complète du thème natal")).toHaveLength(3)
      expect(within(main).getAllByText("1 interprétations incluses")).toHaveLength(1)
      expect(within(main).getAllByText("Inclus")).toHaveLength(6)
      expect(within(main).queryByText(/20.?000 tokens \/ semaine/)).not.toBeInTheDocument()
      expect(within(main).queryByText(/50.?000 tokens \/ mois/)).not.toBeInTheDocument()
      expect(within(main).getAllByText("Chat astrologique")).toHaveLength(3)
      expect(within(main).getAllByText("Non inclus")).toHaveLength(2)

      expect(within(main).getByText("0 €")).toBeInTheDocument()
      expect(within(main).getByText("9 €")).toBeInTheDocument()
      expect(within(main).getByText("29 €")).toBeInTheDocument()

      const upgradeCtas = within(main).getAllByRole("link", { name: "Passer à ce plan" })
      expect(upgradeCtas).toHaveLength(2)
      expect(upgradeCtas[0]).toHaveAttribute("href", "/settings/subscription")
      expect(within(main).queryByRole("link", { name: "Votre plan actuel" })).not.toBeInTheDocument()

      expect(within(main).getByText("Comment choisir")).toBeInTheDocument()
      expect(within(main).getByText("Comment fonctionnent les tokens ?")).toBeInTheDocument()
      expect(within(main).getByText("Vous pouvez changer à tout moment")).toBeInTheDocument()
    })
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

    await waitFor(() => {
      const main = screen.getByRole("main")
      const freeCard = within(main).getByText("Free").closest(".subscription-plan-card")
      expect(freeCard).not.toBeNull()
      expect(within(freeCard as HTMLElement).getByText("Votre plan actuel")).toBeInTheDocument()
      expect(within(freeCard as HTMLElement).queryByRole("link", { name: "Passer à ce plan" })).not.toBeInTheDocument()
    })
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

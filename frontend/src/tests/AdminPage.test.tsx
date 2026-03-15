import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { afterEach, describe, expect, it, vi } from "vitest"

import { TestAppRouter } from "../app/router"
import { setAccessToken } from "../utils/authToken"
import { ThemeProvider } from "../state/ThemeProvider"
import { adminTranslations } from "../i18n/admin"

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

const t = adminTranslations
const fr = t.page.fr
const frSec = t.sections.fr
const frPricing = t.pricing.fr

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

const MONITORING_KPI = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      window: "24h",
      aggregation_scope: "instance_local",
      messages_total: 100,
      out_of_scope_count: 8,
      out_of_scope_rate: 0.08,
      llm_error_count: 3,
      llm_error_rate: 0.03,
      p95_latency_ms: 420,
    },
  }),
}

const PERSONAS_LIST = {
  ok: true,
  status: 200,
  json: async () => ({ data: [] }),
}

const BILLING_PLANS = {
  ok: true,
  status: 200,
  json: async () => ({
    data: [
      {
        code: "basic",
        display_name: "Formule Basic",
        monthly_price_cents: 990,
        currency: "EUR",
        daily_message_limit: 10,
        is_active: true,
      },
      {
        code: "premium",
        display_name: "Formule Premium",
        monthly_price_cents: 1990,
        currency: "EUR",
        daily_message_limit: 50,
        is_active: true,
      },
    ],
  }),
}

const BILLING_PLANS_EMPTY = {
  ok: true,
  status: 200,
  json: async () => ({ data: [] }),
}

const RECONCILIATION_ISSUES = {
  ok: true,
  status: 200,
  json: async () => ({
    items: [],
    total: 0,
    offset: 0,
    limit: 50,
  }),
}

function makeFetchMock(authMeResponse: object, options?: { plansResponse?: object }) {
  const plansResp = options?.plansResponse ?? BILLING_PLANS
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return authMeResponse
    if (url.includes("/v1/ops/monitoring")) return MONITORING_KPI
    if (url.includes("/v1/ops/persona")) return PERSONAS_LIST
    if (url.includes("/v1/b2b/reconciliation")) return RECONCILIATION_ISSUES
    if (url.includes("/v1/billing/plans")) return plansResp
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

function setupToken(sub = "1", role = "ops") {
  const payload = btoa(JSON.stringify({ sub, role }))
  setAccessToken(`x.${payload}.y`)
}

describe("AdminPage - AC#1: Protection d'accès", () => {
  it("redirects non-ops/admin user from /admin to /dashboard", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_USER))
    setupToken("42", "user")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin"])

    await waitFor(() => {
      expect(screen.getByText(/Accédez rapidement à toutes les fonctionnalités/i)).toBeInTheDocument()
    })
  })

  it("allows ops user to access /admin hub", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
    })
  })

  it("allows admin user to access /admin hub", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ADMIN))
    setupToken("99", "admin")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
    })
  })
})

describe("AdminPage - AC#2: Hub admin", () => {
  it("shows navigation cards to all admin sections", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
    })

    expect(screen.getByRole("link", { name: new RegExp(frSec.pricing, "i") })).toBeInTheDocument()
    expect(screen.getByRole("link", { name: new RegExp(frSec.monitoring, "i") })).toBeInTheDocument()
    expect(screen.getByRole("link", { name: new RegExp(frSec.personas, "i") })).toBeInTheDocument()
    expect(screen.getByRole("link", { name: new RegExp(frSec.reconciliation, "i") })).toBeInTheDocument()
  })

  it("navigates to monitoring subpage when clicked", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    localStorage.setItem("lang", "fr")
    const user = userEvent.setup()

    renderApp(["/admin"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
    })

    const monitoringLink = screen.getByRole("link", { name: new RegExp(frSec.monitoring, "i") })
    await user.click(monitoringLink)

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Monitoring conversationnel Ops/i })).toBeInTheDocument()
    })
  })

  it("navigates to personas subpage when clicked", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    localStorage.setItem("lang", "fr")
    const user = userEvent.setup()

    renderApp(["/admin"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
    })

    const personasLink = screen.getByRole("link", { name: new RegExp(frSec.personas, "i") })
    await user.click(personasLink)

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: new RegExp(frSec.personas, "i") })).toBeInTheDocument()
    })
  })
})

describe("AdminPage - AC#4: Page monitoring", () => {
  it("renders OpsMonitoringPanel on /admin/monitoring", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin/monitoring"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Monitoring conversationnel Ops/i })).toBeInTheDocument()
    })
  })

  it("shows back to hub link on subpages", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin/monitoring"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
    })

    expect(screen.getByRole("link", { name: new RegExp(fr.backToHub, "i") })).toBeInTheDocument()
  })
})

describe("AdminPage - AC#5: Page personas", () => {
  it("renders OpsPersonaPanel on /admin/personas", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin/personas"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: new RegExp(frSec.personas, "i") })).toBeInTheDocument()
    })
  })
})

describe("AdminPage - AC#3: Page pricing", () => {
  it("renders PricingAdmin page with title on /admin/pricing", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ADMIN))
    setupToken("99", "admin")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin/pricing"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: new RegExp(frPricing.title, "i") })).toBeInTheDocument()
    })
  })

  it("displays billing plans in a table when API returns data", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ADMIN))
    setupToken("99", "admin")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin/pricing"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: new RegExp(frPricing.title, "i") })).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByRole("table", { name: new RegExp(frPricing.tableLabel, "i") })).toBeInTheDocument()
    })

    expect(screen.getByText("basic")).toBeInTheDocument()
    expect(screen.getByText("Formule Basic")).toBeInTheDocument()
    expect(screen.getByText("premium")).toBeInTheDocument()
    expect(screen.getByText("Formule Premium")).toBeInTheDocument()
  })

  it("displays empty state when no plans exist", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ADMIN, { plansResponse: BILLING_PLANS_EMPTY }))
    setupToken("99", "admin")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin/pricing"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: new RegExp(frPricing.title, "i") })).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText(new RegExp(frPricing.emptyState, "i"))).toBeInTheDocument()
    })
  })

  it("navigates to pricing subpage from hub", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_ADMIN))
    setupToken("99", "admin")
    localStorage.setItem("lang", "fr")
    const user = userEvent.setup()

    renderApp(["/admin"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
    })

    const pricingLink = screen.getByRole("link", { name: new RegExp(frSec.pricing, "i") })
    await user.click(pricingLink)

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: new RegExp(frPricing.title, "i") })).toBeInTheDocument()
    })
  })
})

describe("AdminPage - Reconciliation subpage", () => {
  it("renders B2BReconciliationPanel on /admin/reconciliation", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    localStorage.setItem("lang", "fr")

    renderApp(["/admin/reconciliation"])

    await waitFor(() => {
      expect(screen.getByTestId("reconciliation-admin-title")).toBeInTheDocument()
    })
  })

  it("navigates to reconciliation subpage from hub", async () => {
    vi.stubGlobal("fetch", makeFetchMock(AUTH_ME_OPS))
    setupToken("1")
    localStorage.setItem("lang", "fr")
    const user = userEvent.setup()

    renderApp(["/admin"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: fr.title })).toBeInTheDocument()
    })

    const reconLink = screen.getByRole("link", { name: new RegExp(frSec.reconciliation, "i") })
    await user.click(reconLink)

    await waitFor(() => {
      expect(screen.getByTestId("reconciliation-admin-title")).toBeInTheDocument()
    })
  })
})

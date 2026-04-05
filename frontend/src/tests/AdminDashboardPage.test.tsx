import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { afterEach, describe, expect, it, vi, beforeEach } from "vitest"

import { AdminDashboardPage } from "../pages/admin/AdminDashboardPage"
import { setAccessToken, clearAccessToken } from "../utils/authToken"
import { ThemeProvider } from "../state/ThemeProvider"

beforeEach(() => {
  localStorage.setItem("lang", "fr")
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
  clearAccessToken()
})

const MOCK_SNAPSHOT = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      total_users: 1234,
      active_users_7j: 567,
      active_users_30j: 890,
      subscriptions_by_plan: { premium: 100 },
      mrr_cents: 199900,
      trials_count: 12,
      last_updated: "2025-04-05T12:00:00Z",
    },
  }),
}

const MOCK_FLUX = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      period: "30d",
      plan: "all",
      new_users: 150,
      churn_count: 5,
      upgrades_count: 0,
      downgrades_count: 0,
      payment_failures_count: 2,
      revenue_cents: 50000,
      trend_data: [
        { date: "2025-03-06", new_users: 10 },
        { date: "2025-04-05", new_users: 20 },
      ],
      last_updated: "2025-04-05T12:00:00Z",
    },
  }),
}

function makeFetchMock() {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.includes("/v1/admin/dashboard/kpis-snapshot")) return MOCK_SNAPSHOT
    if (url.includes("/v1/admin/dashboard/kpis-flux")) return MOCK_FLUX
    return { ok: false, status: 404, json: async () => ({}) }
  })
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  })
  return render(
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <AdminDashboardPage />
      </QueryClientProvider>
    </ThemeProvider>
  )
}

describe("AdminDashboardPage", () => {
  it("renders both snapshot and flux KPIs", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    setAccessToken("fake-token")

    renderPage()

    await waitFor(() => {
      // Snapshot
      expect(screen.getByText("1234")).toBeInTheDocument()
      expect(screen.getByText(/1.*999/)).toBeInTheDocument()
      
      // Flux
      expect(screen.getByText("150")).toBeInTheDocument() // new users
      expect(screen.getByText("5")).toBeInTheDocument() // churn
    })

    // Trend chart should be visible
    expect(document.querySelector(".trend-chart")).toBeInTheDocument()
  })

  it("re-fetches flux KPIs when filters change", async () => {
    const fetchMock = makeFetchMock()
    vi.stubGlobal("fetch", fetchMock)
    setAccessToken("fake-token")
    const user = userEvent.setup()

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("150")).toBeInTheDocument()
    })

    // Change period
    const periodSelect = screen.getByLabelText(/Période :/i)
    await user.selectOptions(periodSelect, "7d")

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("period=7d"),
        expect.anything()
      )
    })
  })
})

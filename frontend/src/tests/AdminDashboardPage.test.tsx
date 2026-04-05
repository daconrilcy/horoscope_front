import { cleanup, render, screen, waitFor } from "@testing-library/react"
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

const MOCK_KPIS = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      total_users: 1234,
      active_users_7j: 567,
      active_users_30j: 890,
      subscriptions_by_plan: {
        premium: 100,
        standard: 50,
      },
      mrr_cents: 199900,
      arr_cents: 2398800,
      trials_count: 12,
      last_updated: "2025-04-05T12:00:00Z",
    },
  }),
}

function makeFetchMock(kpisResponse: object) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/admin/dashboard/kpis-snapshot")) return kpisResponse
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
  it("renders KPIs correctly after loading", async () => {
    vi.stubGlobal("fetch", makeFetchMock(MOCK_KPIS))
    setAccessToken("fake-token")

    renderPage()

    // Loading state
    expect(screen.getByText("Tableau de bord")).toBeInTheDocument()
    
    // Values
    await waitFor(() => {
      expect(screen.getByText("1234")).toBeInTheDocument() // total users
      expect(screen.getByText("567")).toBeInTheDocument() // active 7j
      expect(screen.getByText("12")).toBeInTheDocument() // trials
      expect(screen.getByText(/1.*999/)).toBeInTheDocument() // MRR (localized)
    })

    // Plan details
    expect(screen.getByText("premium")).toBeInTheDocument()
    expect(screen.getByText("100")).toBeInTheDocument()
    expect(screen.getByText("standard")).toBeInTheDocument()
    expect(screen.getByText("50")).toBeInTheDocument()
  })

  it("shows error state on fetch failure", async () => {
    vi.stubGlobal("fetch", makeFetchMock({ ok: false, status: 500 }))
    setAccessToken("fake-token")

    renderPage()

    await waitFor(() => {
      expect(screen.getByText(/Erreur lors du chargement des KPIs/i)).toBeInTheDocument()
    })
  })
})

import { cleanup, render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { afterEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"

import { AdminUserDetailPage } from "../pages/admin/AdminUserDetailPage"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/admin/users/42"]}>
        <Routes>
          <Route path="/admin/users/:userId" element={<AdminUserDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
  clearAccessToken()
})

describe("AdminUserDetailPage", () => {
  it("renders all quota windows for the same feature", async () => {
    setAccessToken("fake-token")
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            id: 42,
            email: "admin-user-detail@test.com",
            role: "user",
            created_at: "2026-04-06T12:00:00Z",
            is_active: true,
            is_suspended: false,
            is_locked: false,
            plan_code: "basic",
            subscription_status: "active",
            stripe_customer_id_masked: "cus_1234...9999",
            payment_method_summary: null,
            last_invoice_amount_cents: null,
            last_invoice_date: null,
            activity_summary: {
              total_tokens: 12345,
              tokens_in: 8000,
              tokens_out: 4345,
              messages_count: 30,
              natal_charts_total: 3,
              natal_charts_short: 2,
              natal_charts_complete: 1,
            },
            quotas: [
              {
                feature_code: "astrologer_chat",
                used: 120,
                limit: 500,
                period: "1 day",
              },
              {
                feature_code: "astrologer_chat",
                used: 11235,
                limit: 50000,
                period: "1 week",
              },
              {
                feature_code: "astrologer_chat",
                used: 25234,
                limit: 200000,
                period: "1 month",
              },
            ],
            recent_tickets: [],
            recent_audit_events: [],
          },
        }),
      }))
    )

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("1 day")).toBeInTheDocument()
      expect(screen.getByText("1 week")).toBeInTheDocument()
      expect(screen.getByText("1 month")).toBeInTheDocument()
    })

    expect(screen.getAllByText("astrologer_chat")).toHaveLength(3)
    expect(screen.getByText("120 / 500")).toBeInTheDocument()
    expect(screen.getByText("11235 / 50000")).toBeInTheDocument()
    expect(screen.getByText("25234 / 200000")).toBeInTheDocument()
  })
})

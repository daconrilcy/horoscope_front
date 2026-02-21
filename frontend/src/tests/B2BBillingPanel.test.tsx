import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { B2BBillingPanel } from "../components/B2BBillingPanel"

const mockUseB2BBillingLatestCycle = vi.fn()
const mockUseB2BBillingCycles = vi.fn()

vi.mock("../api/b2bBilling", () => ({
  B2BBillingApiError: class extends Error {
    code: string
    status: number
    details: Record<string, unknown>
    requestId: string | null

    constructor(
      code: string,
      message: string,
      status: number,
      details: Record<string, unknown> = {},
      requestId: string | null = null,
    ) {
      super(message)
      this.code = code
      this.status = status
      this.details = details
      this.requestId = requestId
    }
  },
  useB2BBillingLatestCycle: () => mockUseB2BBillingLatestCycle(),
  useB2BBillingCycles: () => mockUseB2BBillingCycles(),
}))

afterEach(() => {
  cleanup()
  mockUseB2BBillingLatestCycle.mockReset()
  mockUseB2BBillingCycles.mockReset()
})

describe("B2BBillingPanel", () => {
  it("submits api key and renders latest billing cycle", async () => {
    const mutateAsyncLatest = vi.fn().mockResolvedValue({
      cycle_id: 10,
      account_id: 1,
      plan_id: 2,
      plan_code: "b2b_standard",
      plan_display_name: "B2B Standard",
      period_start: "2026-02-01",
      period_end: "2026-02-28",
      status: "closed",
      currency: "EUR",
      fixed_amount_cents: 5000,
      included_units: 10000,
      consumed_units: 12000,
      billable_units: 2000,
      unit_price_cents: 2,
      variable_amount_cents: 4000,
      total_amount_cents: 9000,
      limit_mode: "overage",
      overage_applied: true,
      calculation_snapshot: {},
      closed_by_user_id: 9,
      created_at: "2026-03-01T00:00:00Z",
      updated_at: "2026-03-01T00:00:00Z",
    })
    const mutateAsyncHistory = vi.fn().mockResolvedValue({
      items: [
        {
          cycle_id: 9,
          account_id: 1,
          plan_id: 2,
          plan_code: "b2b_standard",
          plan_display_name: "B2B Standard",
          period_start: "2026-01-01",
          period_end: "2026-01-31",
          status: "closed",
          currency: "EUR",
          fixed_amount_cents: 5000,
          included_units: 10000,
          consumed_units: 10000,
          billable_units: 0,
          unit_price_cents: 2,
          variable_amount_cents: 0,
          total_amount_cents: 5000,
          limit_mode: "block",
          overage_applied: false,
          calculation_snapshot: {},
          closed_by_user_id: 9,
          created_at: "2026-02-01T00:00:00Z",
          updated_at: "2026-02-01T00:00:00Z",
        },
      ],
      total: 1,
      limit: 10,
      offset: 0,
    })
    mockUseB2BBillingLatestCycle.mockReturnValue({
      isPending: false,
      isSuccess: true,
      error: null,
      mutateAsync: mutateAsyncLatest,
      data: {
        cycle_id: 10,
        account_id: 1,
        plan_id: 2,
        plan_code: "b2b_standard",
        plan_display_name: "B2B Standard",
        period_start: "2026-02-01",
        period_end: "2026-02-28",
        status: "closed",
        currency: "EUR",
        fixed_amount_cents: 5000,
        included_units: 10000,
        consumed_units: 12000,
        billable_units: 2000,
        unit_price_cents: 2,
        variable_amount_cents: 4000,
        total_amount_cents: 9000,
        limit_mode: "overage",
        overage_applied: true,
        calculation_snapshot: {},
        closed_by_user_id: 9,
        created_at: "2026-03-01T00:00:00Z",
        updated_at: "2026-03-01T00:00:00Z",
      },
    })
    mockUseB2BBillingCycles.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: mutateAsyncHistory,
    })

    render(<B2BBillingPanel />)
    fireEvent.change(screen.getByLabelText("Cle API B2B"), { target: { value: "b2b_billing_secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Recuperer le releve facture" }))

    await waitFor(() => expect(mutateAsyncLatest).toHaveBeenCalledWith("b2b_billing_secret"))
    await waitFor(() =>
      expect(mutateAsyncHistory).toHaveBeenCalledWith({ apiKey: "b2b_billing_secret", limit: 10, offset: 0 }),
    )
    expect(screen.getByText("Fixe: 50.00 EUR")).toBeInTheDocument()
    expect(screen.getByText("Variable: 40.00 EUR")).toBeInTheDocument()
    expect(screen.getByText("Total: 90.00 EUR")).toBeInTheDocument()
    expect(screen.getByText("Historique recent")).toBeInTheDocument()
  })

  it("renders loading, error and empty states", () => {
    mockUseB2BBillingLatestCycle.mockReturnValueOnce({
      isPending: true,
      isSuccess: false,
      error: null,
      mutateAsync: vi.fn(),
      data: undefined,
    })
    mockUseB2BBillingCycles.mockReturnValueOnce({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    const { rerender } = render(<B2BBillingPanel />)
    expect(screen.getByText("Chargement facturation B2B...")).toBeInTheDocument()

    mockUseB2BBillingLatestCycle.mockReturnValueOnce({
      isPending: false,
      isSuccess: false,
      error: {
        code: "invalid_api_key",
        message: "invalid api key",
        requestId: "rid-b2b-billing-err",
        details: { retry_after: "5" },
      },
      mutateAsync: vi.fn(),
      data: undefined,
    })
    mockUseB2BBillingCycles.mockReturnValueOnce({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    rerender(<B2BBillingPanel />)
    expect(screen.getByText(/Erreur facturation B2B:/)).toBeInTheDocument()
    expect(screen.getByText(/\[details=retry_after=5\]/)).toBeInTheDocument()

    mockUseB2BBillingLatestCycle.mockReturnValueOnce({
      isPending: false,
      isSuccess: true,
      error: null,
      mutateAsync: vi.fn(),
      data: null,
    })
    mockUseB2BBillingCycles.mockReturnValueOnce({
      isPending: false,
      error: null,
      mutateAsync: vi.fn().mockResolvedValue({ items: [], total: 0, limit: 10, offset: 0 }),
    })
    rerender(<B2BBillingPanel />)
    expect(screen.getByText("Aucun cycle de facturation cloture pour ce compte.")).toBeInTheDocument()
  })
})

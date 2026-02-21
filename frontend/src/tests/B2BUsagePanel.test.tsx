import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { B2BUsagePanel } from "../components/B2BUsagePanel"

const mockUseB2BUsageSummary = vi.fn()

vi.mock("../api/b2bUsage", () => ({
  B2BUsageApiError: class extends Error {
    code: string
    status: number
    details: Record<string, string>
    requestId: string | null

    constructor(
      code: string,
      message: string,
      status: number,
      details: Record<string, string> = {},
      requestId: string | null = null,
    ) {
      super(message)
      this.code = code
      this.status = status
      this.details = details
      this.requestId = requestId
    }
  },
  useB2BUsageSummary: () => mockUseB2BUsageSummary(),
}))

afterEach(() => {
  cleanup()
  mockUseB2BUsageSummary.mockReset()
})

describe("B2BUsagePanel", () => {
  it("submits api key and renders usage summary", async () => {
    const mutate = vi.fn()
    mockUseB2BUsageSummary.mockReturnValue({
      isPending: false,
      isSuccess: true,
      error: null,
      mutate,
      data: {
        account_id: 1,
        credential_id: 2,
        usage_date: "2026-02-20",
        month_start: "2026-02-01",
        month_end: "2026-02-28",
        daily_limit: 5,
        daily_consumed: 2,
        daily_remaining: 3,
        monthly_limit: 100,
        monthly_consumed: 10,
        monthly_remaining: 90,
        limit_mode: "block",
        blocked: false,
        overage_applied: false,
      },
    })

    render(<B2BUsagePanel />)
    fireEvent.change(screen.getByLabelText("Cle API B2B"), { target: { value: "b2b_usage_secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Recuperer le resume de consommation" }))

    await waitFor(() => expect(mutate).toHaveBeenCalledWith("b2b_usage_secret"))
    expect(screen.getByText("Quotidien: 2/5 (3 restant)")).toBeInTheDocument()
    expect(screen.getByText("Mensuel: 10/100 (90 restant)")).toBeInTheDocument()
  })

  it("renders loading, error and empty states", () => {
    mockUseB2BUsageSummary.mockReturnValueOnce({
      isPending: true,
      isSuccess: false,
      error: null,
      mutate: vi.fn(),
      data: undefined,
    })
    const { rerender } = render(<B2BUsagePanel />)
    expect(screen.getByText("Chargement consommation B2B...")).toBeInTheDocument()

    mockUseB2BUsageSummary.mockReturnValueOnce({
      isPending: false,
      isSuccess: false,
      error: {
        code: "invalid_api_key",
        message: "invalid api key",
        requestId: "rid-b2b-usage-err",
      },
      mutate: vi.fn(),
      data: undefined,
    })
    rerender(<B2BUsagePanel />)
    expect(screen.getByText(/Erreur consommation B2B:/)).toBeInTheDocument()
    expect(screen.getByText(/request_id=rid-b2b-usage-err/)).toBeInTheDocument()

    mockUseB2BUsageSummary.mockReturnValueOnce({
      isPending: false,
      isSuccess: true,
      error: null,
      mutate: vi.fn(),
      data: {
        account_id: 1,
        credential_id: 2,
        usage_date: "2026-02-20",
        month_start: "2026-02-01",
        month_end: "2026-02-28",
        daily_limit: 5,
        daily_consumed: 0,
        daily_remaining: 5,
        monthly_limit: 100,
        monthly_consumed: 0,
        monthly_remaining: 100,
        limit_mode: "block",
        blocked: false,
        overage_applied: false,
      },
    })
    rerender(<B2BUsagePanel />)
    expect(screen.getByText("Aucune consommation enregistree pour cette periode.")).toBeInTheDocument()
  })
})

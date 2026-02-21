import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { B2BReconciliationPanel } from "../components/B2BReconciliationPanel"

const mockUseIssues = vi.fn()
const mockUseDetail = vi.fn()
const mockUseAction = vi.fn()

vi.mock("../api/b2bReconciliation", () => ({
  B2BReconciliationApiError: class extends Error {
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
  useB2BReconciliationIssues: (...args: unknown[]) => mockUseIssues(...args),
  useB2BReconciliationIssueDetail: (...args: unknown[]) => mockUseDetail(...args),
  useB2BReconciliationAction: () => mockUseAction(),
}))

function setAccessTokenWithRole(role: string) {
  const payload = btoa(JSON.stringify({ role }))
  localStorage.setItem("access_token", `x.${payload}.y`)
}

afterEach(() => {
  cleanup()
  localStorage.removeItem("access_token")
  mockUseIssues.mockReset()
  mockUseDetail.mockReset()
  mockUseAction.mockReset()
})

describe("B2BReconciliationPanel", () => {
  it("does not render for non ops role", () => {
    setAccessTokenWithRole("user")
    mockUseIssues.mockReturnValue({
      isPending: false,
      isFetching: false,
      error: null,
      data: null,
      refetch: vi.fn(),
    })
    mockUseDetail.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      refetch: vi.fn(),
    })
    mockUseAction.mockReturnValue({
      isPending: false,
      isSuccess: false,
      error: null,
      mutate: vi.fn(),
    })

    render(<B2BReconciliationPanel />)
    expect(screen.queryByText("Reconciliation B2B Ops")).not.toBeInTheDocument()
  })

  it("loads list, detail and executes actions", async () => {
    setAccessTokenWithRole("ops")
    const issuesRefetch = vi.fn()
    const detailRefetch = vi.fn()
    const actionMutate = vi.fn((_: unknown, options?: { onSuccess?: () => void }) => {
      options?.onSuccess?.()
    })
    mockUseIssues.mockReturnValue({
      isPending: false,
      isFetching: false,
      error: null,
      refetch: issuesRefetch,
      data: {
        items: [
          {
            issue_id: "9:2026-02-01:2026-02-28",
            account_id: 9,
            period_start: "2026-02-01",
            period_end: "2026-02-28",
            mismatch_type: "usage_vs_billing_mismatch",
            severity: "major",
            status: "open",
            usage_measured_units: 10,
            billing_consumed_units: 1,
            delta_units: 9,
            billing_cycle_id: 1,
            billable_units: 0,
            total_amount_cents: 5000,
            source_trace: { usage_rows: 1 },
            recommended_actions: [],
            last_action: null,
          },
        ],
        total: 1,
        limit: 50,
        offset: 0,
      },
    })
    mockUseDetail.mockReturnValue({
      isPending: false,
      error: null,
      refetch: detailRefetch,
      data: {
        issue: {
          issue_id: "9:2026-02-01:2026-02-28",
          account_id: 9,
          period_start: "2026-02-01",
          period_end: "2026-02-28",
          mismatch_type: "usage_vs_billing_mismatch",
          severity: "major",
          status: "open",
          usage_measured_units: 10,
          billing_consumed_units: 1,
          delta_units: 9,
          billing_cycle_id: 1,
          billable_units: 0,
          total_amount_cents: 5000,
          source_trace: { usage_rows: 1 },
          recommended_actions: [
            { code: "mark_investigated", label: "Marquer investigue", description: "desc" },
          ],
          last_action: null,
        },
        action_log: [],
      },
    })
    mockUseAction.mockReturnValue({
      isPending: false,
      isSuccess: true,
      error: null,
      data: {
        issue_id: "9:2026-02-01:2026-02-28",
        action: "mark_investigated",
        status: "accepted",
        message: "ok",
        correction_state: "investigating",
      },
      mutate: actionMutate,
    })

    render(<B2BReconciliationPanel />)
    fireEvent.click(screen.getByRole("button", { name: "Charger la reconciliation" }))
    expect(issuesRefetch).toHaveBeenCalled()

    fireEvent.click(screen.getByRole("button", { name: "A9 2026-02-01 -> 2026-02-28 (major)" }))
    await waitFor(() =>
      expect(mockUseDetail).toHaveBeenLastCalledWith("9:2026-02-01:2026-02-28", true),
    )

    fireEvent.change(screen.getByLabelText("Note action (optionnel)"), { target: { value: "analyste assigne" } })
    fireEvent.click(screen.getByRole("button", { name: "Marquer investigue" }))

    expect(actionMutate).toHaveBeenCalledWith({
      issueId: "9:2026-02-01:2026-02-28",
      action: "mark_investigated",
      note: "analyste assigne",
    }, expect.objectContaining({ onSuccess: expect.any(Function) }))
    expect(issuesRefetch).toHaveBeenCalledTimes(2)
    expect(detailRefetch).toHaveBeenCalledTimes(1)
    expect(screen.getByText("Action executee: mark_investigated (investigating)")).toBeInTheDocument()
  })

  it("renders loading, empty and error states", () => {
    setAccessTokenWithRole("ops")
    mockUseIssues.mockReturnValue({
      isPending: false,
      isFetching: false,
      error: null,
      data: { items: [], total: 0, limit: 50, offset: 0 },
      refetch: vi.fn(),
    })
    mockUseDetail.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      refetch: vi.fn(),
    })
    mockUseAction.mockReturnValue({
      isPending: false,
      isSuccess: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })

    mockUseIssues.mockReturnValueOnce({
      isPending: true,
      isFetching: true,
      error: null,
      data: null,
      refetch: vi.fn(),
    })
    mockUseDetail.mockReturnValueOnce({
      isPending: false,
      error: null,
      data: null,
      refetch: vi.fn(),
    })
    const { rerender } = render(<B2BReconciliationPanel />)
    expect(screen.getByText("Chargement reconciliation...")).toBeInTheDocument()

    mockUseIssues.mockReturnValueOnce({
      isPending: false,
      isFetching: false,
      error: {
        code: "invalid_token",
        message: "token invalid",
        requestId: "rid-reco-ui",
      },
      data: null,
      refetch: vi.fn(),
    })
    mockUseDetail.mockReturnValueOnce({
      isPending: false,
      error: null,
      data: null,
      refetch: vi.fn(),
    })
    rerender(<B2BReconciliationPanel />)
    expect(screen.getByText(/Erreur reconciliation liste: token invalid/)).toBeInTheDocument()

    mockUseIssues.mockReturnValueOnce({
      isPending: false,
      isFetching: false,
      error: null,
      data: { items: [], total: 0, limit: 50, offset: 0 },
      refetch: vi.fn(),
    })
    mockUseDetail.mockReturnValueOnce({
      isPending: false,
      error: null,
      data: null,
      refetch: vi.fn(),
    })
    rerender(<B2BReconciliationPanel />)
    fireEvent.click(screen.getByRole("button", { name: "Charger la reconciliation" }))
    expect(screen.getByText("Aucun ecart de reconciliation pour ces filtres.")).toBeInTheDocument()
  })
})

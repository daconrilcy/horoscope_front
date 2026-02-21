import { afterEach, describe, expect, it, vi } from "vitest"

import {
  B2BReconciliationApiError,
  useB2BReconciliationAction,
  useB2BReconciliationIssueDetail,
  useB2BReconciliationIssues,
} from "../api/b2bReconciliation"

vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => options,
  useQuery: (options: unknown) => options,
}))

describe("b2b reconciliation api", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    localStorage.removeItem("access_token")
  })

  it("loads reconciliation issues with filters", async () => {
    localStorage.setItem("access_token", "token")
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            data: { items: [], total: 0, limit: 50, offset: 0 },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { queryFn } = useB2BReconciliationIssues({ accountId: 9, severity: "major", limit: 50 }, true)
    const payload = await queryFn()
    expect(payload.total).toBe(0)
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/v1/ops/b2b/reconciliation/issues?account_id=9&severity=major&limit=50&offset=0",
      expect.objectContaining({
        method: "GET",
        headers: { Authorization: "Bearer token" },
      }),
    )
  })

  it("loads reconciliation detail", async () => {
    localStorage.setItem("access_token", "token")
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
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
                source_trace: {},
                recommended_actions: [],
                last_action: null,
              },
              action_log: [],
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { queryFn } = useB2BReconciliationIssueDetail("9:2026-02-01:2026-02-28", true)
    const data = await queryFn()
    expect(data.issue.delta_units).toBe(9)
  })

  it("executes reconciliation action", async () => {
    localStorage.setItem("access_token", "token")
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            data: {
              issue_id: "9:2026-02-01:2026-02-28",
              action: "mark_investigated",
              status: "accepted",
              message: "ok",
              correction_state: "investigating",
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useB2BReconciliationAction()
    const result = await mutationFn({
      issueId: "9:2026-02-01:2026-02-28",
      action: "mark_investigated",
      note: "assigned",
    })
    expect(result.action).toBe("mark_investigated")
  })

  it("maps backend errors including request_id", async () => {
    localStorage.setItem("access_token", "token")
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "rate_limit_exceeded",
              message: "too many requests",
              details: { retry_after: 5 },
              request_id: "rid-reco-1",
            },
          }),
          { status: 429, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { queryFn } = useB2BReconciliationIssues({}, true)
    await expect(queryFn()).rejects.toEqual(
      expect.objectContaining({
        code: "rate_limit_exceeded",
        status: 429,
        requestId: "rid-reco-1",
      }),
    )
  })

  it("falls back to unknown_error on malformed response", async () => {
    localStorage.setItem("access_token", "token")
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("bad gateway", { status: 502 })))
    const { queryFn } = useB2BReconciliationIssues({}, true)
    try {
      await queryFn()
    } catch (error) {
      expect(error).toBeInstanceOf(B2BReconciliationApiError)
      expect(error).toMatchObject({ code: "unknown_error", status: 502 })
    }
  })
})


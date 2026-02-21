import { afterEach, describe, expect, it, vi } from "vitest"

import { B2BBillingApiError, useB2BBillingCycles, useB2BBillingLatestCycle } from "../api/b2bBilling"

vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => options,
}))

describe("b2b billing api", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("loads latest billing cycle with api key", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
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
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useB2BBillingLatestCycle()
    const data = await mutationFn("b2b_billing_key")
    expect(data?.total_amount_cents).toBe(9000)
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/v1/b2b/billing/cycles/latest",
      expect.objectContaining({
        method: "GET",
        headers: { "X-API-Key": "b2b_billing_key" },
      }),
    )
  })

  it("lists billing cycles with query params", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            data: {
              items: [],
              total: 0,
              limit: 10,
              offset: 5,
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useB2BBillingCycles()
    const data = await mutationFn({ apiKey: "b2b_billing_key", limit: 10, offset: 5 })
    expect(data.total).toBe(0)
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/v1/b2b/billing/cycles?limit=10&offset=5",
      expect.objectContaining({
        method: "GET",
        headers: { "X-API-Key": "b2b_billing_key" },
      }),
    )
  })

  it("maps backend errors including request_id", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "rate_limit_exceeded",
              message: "too many requests",
              details: { retry_after_seconds: 30 },
              request_id: "rid-b2b-billing-1",
            },
          }),
          { status: 429, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useB2BBillingLatestCycle()
    await expect(mutationFn("b2b_billing_key")).rejects.toEqual(
      expect.objectContaining({
        code: "rate_limit_exceeded",
        status: 429,
        details: { retry_after_seconds: 30 },
        requestId: "rid-b2b-billing-1",
      }),
    )
  })

  it("falls back to unknown_error on invalid error payload", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("bad gateway", { status: 502 })))

    const { mutationFn } = useB2BBillingLatestCycle()
    try {
      await mutationFn("b2b_billing_key")
    } catch (error) {
      expect(error).toBeInstanceOf(B2BBillingApiError)
      expect(error).toMatchObject({
        code: "unknown_error",
        status: 502,
      })
    }
  })
})


import { afterEach, describe, expect, it, vi } from "vitest"

import { B2BUsageApiError, useB2BUsageSummary } from "../api/b2bUsage"

vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => options,
}))

describe("b2b usage api", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("returns usage summary and forwards api key header", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
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
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useB2BUsageSummary()
    const data = await mutationFn("b2b_usage_key")
    expect(data.daily_consumed).toBe(2)
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/v1/b2b/usage/summary",
      expect.objectContaining({
        method: "GET",
        headers: { "X-API-Key": "b2b_usage_key" },
      }),
    )
  })

  it("keeps backend error code/details/request_id", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "rate_limit_exceeded",
              message: "too many requests",
              details: { retry_after_seconds: "30" },
              request_id: "rid-b2b-usage-1",
            },
          }),
          { status: 429, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useB2BUsageSummary()
    await expect(mutationFn("b2b_usage_key")).rejects.toEqual(
      expect.objectContaining({
        code: "rate_limit_exceeded",
        status: 429,
        details: { retry_after_seconds: "30" },
        requestId: "rid-b2b-usage-1",
      }),
    )
  })

  it("uses fallback error values when body is invalid", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("bad gateway", { status: 502 })))

    const { mutationFn } = useB2BUsageSummary()
    try {
      await mutationFn("b2b_usage_key")
    } catch (error) {
      expect(error).toBeInstanceOf(B2BUsageApiError)
      expect(error).toMatchObject({
        code: "unknown_error",
        status: 502,
      })
    }
  })
})


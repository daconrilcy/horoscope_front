import { afterEach, describe, expect, it, vi } from "vitest"

import { B2BAstrologyApiError, useB2BWeeklyBySign } from "../api/b2bAstrology"

vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => options,
}))

describe("b2b astrology api", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("returns weekly-by-sign payload and sends X-API-Key header", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            data: {
              api_version: "v1",
              reference_version: "2026.01",
              generated_at: "2026-02-20T00:00:00Z",
              items: [{ sign_code: "aries", sign_name: "Aries", weekly_summary: "Momentum stable." }],
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useB2BWeeklyBySign()
    const data = await mutationFn("b2b_demo_key")
    expect(data.api_version).toBe("v1")
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/v1/b2b/astrology/weekly-by-sign",
      expect.objectContaining({
        method: "GET",
        headers: { "X-API-Key": "b2b_demo_key" },
      }),
    )
  })

  it("maps backend error payload including request_id", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "invalid_api_key",
              message: "invalid api key",
              details: { field: "x_api_key" },
              request_id: "rid-b2b-astro-1",
            },
          }),
          { status: 401, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useB2BWeeklyBySign()
    await expect(mutationFn("bad_key")).rejects.toEqual(
      expect.objectContaining({
        code: "invalid_api_key",
        status: 401,
        details: { field: "x_api_key" },
        requestId: "rid-b2b-astro-1",
      }),
    )
  })

  it("falls back to unknown_error when error body is not json", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("oops", { status: 500 })))

    const { mutationFn } = useB2BWeeklyBySign()
    try {
      await mutationFn("bad_key")
    } catch (error) {
      expect(error).toBeInstanceOf(B2BAstrologyApiError)
      expect(error).toMatchObject({
        code: "unknown_error",
        status: 500,
      })
    }
  })
})


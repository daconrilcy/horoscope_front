import { afterEach, describe, expect, it, vi } from "vitest"

import { API_TIMEOUT_MS, apiFetch } from "../api/client"

describe("apiFetch", () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it("returns response when request completes before timeout", async () => {
    const response = new Response(JSON.stringify({ ok: true }), { status: 200 })
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response))

    await expect(apiFetch("https://example.test/ok")).resolves.toBe(response)
  })

  it("aborts request after configured timeout", async () => {
    vi.useFakeTimers()
    vi.stubGlobal(
      "fetch",
      vi.fn((_input: RequestInfo | URL, init?: RequestInit) => {
        return new Promise<Response>((_resolve, reject) => {
          const signal = init?.signal
          signal?.addEventListener("abort", () => {
            reject(new DOMException("Aborted", "AbortError"))
          })
        })
      }),
    )

    const pendingRequest = apiFetch("https://example.test/slow")
    const rejection = expect(pendingRequest).rejects.toMatchObject({ name: "AbortError" })
    await vi.advanceTimersByTimeAsync(API_TIMEOUT_MS + 1)
    await rejection
  })
})

import { afterEach, describe, expect, it, vi } from "vitest"

import { API_BASE_URL, API_TIMEOUT_MS, apiFetch } from "../api/client"
import { AUTH_TOKEN_KEY, hasUsableAccessToken, setAccessToken } from "../utils/authToken"

function toBase64Url(value: string): string {
  return btoa(value).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "")
}

function buildAccessToken(): string {
  const header = toBase64Url(JSON.stringify({ alg: "HS256", typ: "JWT" }))
  const payload = toBase64Url(JSON.stringify({
    sub: "user-1",
    exp: Math.floor(Date.now() / 1000) + 3600,
  }))
  return `${header}.${payload}.sig`
}

describe("apiFetch", () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("returns response when request completes before timeout", async () => {
    const response = new Response(JSON.stringify({ ok: true }), { status: 200 })
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response))

    await expect(apiFetch("https://example.test/ok")).resolves.toBe(response)
  })

  it("prefixes relative API paths with the configured backend base URL", async () => {
    const response = new Response(JSON.stringify({ ok: true }), { status: 200 })
    const fetchMock = vi.fn().mockResolvedValue(response)
    vi.stubGlobal("fetch", fetchMock)

    await expect(apiFetch("/v1/admin/users?q=")).resolves.toBe(response)

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/v1/admin/users?q=`,
      expect.objectContaining({
        signal: expect.any(AbortSignal),
      }),
    )
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

  it("clears the local session when backend rejects the token subject", async () => {
    setAccessToken("header.payload.signature")
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "invalid_token",
              message: "token subject is invalid",
            },
          }),
          { status: 401 },
        ),
      ),
    )

    const response = await apiFetch("/v1/astral/jobs")

    expect(response.status).toBe(401)
    expect(localStorage.getItem(AUTH_TOKEN_KEY)).toBeNull()
  })

  it("rejects the sent bearer locally when backend returns a non-json 401", async () => {
    const token = buildAccessToken()
    setAccessToken(token)
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("Unauthorized", { status: 401 })))

    const response = await apiFetch("/v1/astral/jobs", {
      headers: { Authorization: `Bearer ${token}` },
    })

    expect(response.status).toBe(401)
    expect(localStorage.getItem(AUTH_TOKEN_KEY)).toBeNull()
    expect(hasUsableAccessToken(token)).toBe(false)
  })
})

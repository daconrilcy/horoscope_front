import { render } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError, generateNatalChart, useLatestNatalChart } from "../api/natalChart"

const useQueryMock = vi.fn()
const useAccessTokenSnapshotMock = vi.fn()
const getSubjectFromAccessTokenMock = vi.fn()

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => useQueryMock(options),
}))

vi.mock("../utils/authToken", () => ({
  useAccessTokenSnapshot: () => useAccessTokenSnapshotMock(),
  getSubjectFromAccessToken: (token: string | null) => getSubjectFromAccessTokenMock(token),
}))

function HookProbe() {
  useLatestNatalChart()
  return null
}

describe("generateNatalChart", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("sends Content-Type: application/json header", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: { chart_id: "c1", result: {}, metadata: {}, created_at: "" } }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await generateNatalChart("test-token").catch(() => {})

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect((init.headers as Record<string, string>)["Content-Type"]).toBe("application/json")
    expect((init.headers as Record<string, string>)["Authorization"]).toBe("Bearer test-token")
    expect(init.body).toBe("{}")
  })

  it("parses FastAPI native 422 format {detail: [...]} as unprocessable_entity", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({ detail: [{ loc: ["body"], msg: "Field required", type: "missing" }] }),
      }),
    )

    await expect(generateNatalChart("test-token")).rejects.toMatchObject({
      code: "unprocessable_entity",
      status: 422,
      message: "Field required",
    })
  })

  it("parses standard API error format {error: {...}} correctly", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({ error: { code: "unprocessable_entity", message: "Données invalides" } }),
      }),
    )

    await expect(generateNatalChart("test-token")).rejects.toMatchObject({
      code: "unprocessable_entity",
      status: 422,
      message: "Données invalides",
    })
  })

  it("falls back to unknown_error when response body is unparseable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => { throw new Error("not JSON") },
      }),
    )

    await expect(generateNatalChart("test-token")).rejects.toMatchObject({
      code: "unknown_error",
      status: 500,
    })
  })
})

describe("useLatestNatalChart", () => {
  beforeEach(() => {
    useQueryMock.mockReset()
    useAccessTokenSnapshotMock.mockReset()
    getSubjectFromAccessTokenMock.mockReset()
  })

  it("uses user-scoped query key when token exists", () => {
    useAccessTokenSnapshotMock.mockReturnValue("token-a")
    getSubjectFromAccessTokenMock.mockReturnValue("42")
    useQueryMock.mockReturnValue({})

    render(<HookProbe />)

    expect(useQueryMock).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["latest-natal-chart", "42"],
        enabled: true,
      }),
    )
  })

  it("disables query when token is absent", () => {
    useAccessTokenSnapshotMock.mockReturnValue(null)
    getSubjectFromAccessTokenMock.mockReturnValue(null)
    useQueryMock.mockReturnValue({})

    render(<HookProbe />)

    expect(useQueryMock).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["latest-natal-chart", "anonymous"],
        enabled: false,
      }),
    )
  })
})

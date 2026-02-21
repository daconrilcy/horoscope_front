import { afterEach, describe, expect, it, vi } from "vitest"

import {
  B2BEditorialApiError,
  useB2BEditorialConfig,
  useUpdateB2BEditorialConfig,
} from "../api/b2bEditorial"

vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => options,
}))

describe("b2b editorial api", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("loads editorial config with api key header", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            data: {
              config_id: 1,
              account_id: 2,
              version_number: 1,
              is_active: true,
              tone: "neutral",
              length_style: "medium",
              output_format: "paragraph",
              preferred_terms: ["focus"],
              avoided_terms: ["drama"],
              created_by_credential_id: 5,
              created_at: "2026-02-20T00:00:00Z",
              updated_at: "2026-02-20T00:00:00Z",
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useB2BEditorialConfig()
    const data = await mutationFn("b2b_editorial_key")
    expect(data.version_number).toBe(1)
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/v1/b2b/editorial/config",
      expect.objectContaining({
        method: "GET",
        headers: { "X-API-Key": "b2b_editorial_key" },
      }),
    )
  })

  it("updates editorial config with payload and content type", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            data: {
              config_id: 2,
              account_id: 2,
              version_number: 2,
              is_active: true,
              tone: "friendly",
              length_style: "short",
              output_format: "bullet",
              preferred_terms: ["focus", "clarte"],
              avoided_terms: ["drama"],
              created_by_credential_id: 5,
              created_at: "2026-02-20T00:00:00Z",
              updated_at: "2026-02-20T00:10:00Z",
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useUpdateB2BEditorialConfig()
    const payload = {
      tone: "friendly" as const,
      length_style: "short" as const,
      output_format: "bullet" as const,
      preferred_terms: ["focus", "clarte"],
      avoided_terms: ["drama"],
    }
    const data = await mutationFn({ apiKey: "b2b_editorial_key", payload })
    expect(data.tone).toBe("friendly")
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/v1/b2b/editorial/config",
      expect.objectContaining({
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "b2b_editorial_key",
        },
        body: JSON.stringify(payload),
      }),
    )
  })

  it("maps backend error payload for read/update", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "invalid_payload",
              message: "payload is invalid",
              details: { field: "tone" },
              request_id: "rid-b2b-editorial-1",
            },
          }),
          { status: 422, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { mutationFn } = useUpdateB2BEditorialConfig()
    await expect(
      mutationFn({
        apiKey: "b2b_editorial_key",
        payload: {
          tone: "friendly",
          length_style: "short",
          output_format: "bullet",
          preferred_terms: [],
          avoided_terms: [],
        },
      }),
    ).rejects.toEqual(
      expect.objectContaining({
        code: "invalid_payload",
        status: 422,
        details: { field: "tone" },
        requestId: "rid-b2b-editorial-1",
      }),
    )
  })

  it("falls back to unknown error on non json response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("oops", { status: 500 })))

    const { mutationFn } = useB2BEditorialConfig()
    try {
      await mutationFn("b2b_editorial_key")
    } catch (error) {
      expect(error).toBeInstanceOf(B2BEditorialApiError)
      expect(error).toMatchObject({
        code: "unknown_error",
        status: 500,
      })
    }
  })
})


import { afterEach, describe, expect, it, vi } from "vitest"

import {
  EnterpriseCredentialsApiError,
  useEnterpriseCredentials,
  useGenerateEnterpriseCredential,
  useRotateEnterpriseCredential,
} from "../api/enterpriseCredentials"

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => options,
  useMutation: (options: unknown) => options,
}))

describe("enterprise credentials api", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("uses bearer token for credentials listing", async () => {
    localStorage.setItem("access_token", "test.token.value")
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            data: {
              account_id: 1,
              company_name: "Acme Media",
              status: "active",
              has_active_credential: true,
              credentials: [],
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { queryFn } = useEnterpriseCredentials(true)
    const data = await queryFn()
    expect(data.company_name).toBe("Acme Media")
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/v1/b2b/credentials",
      expect.objectContaining({
        method: "GET",
        headers: { Authorization: "Bearer test.token.value" },
      }),
    )
  })

  it("calls generate and rotate endpoints", async () => {
    localStorage.setItem("access_token", "test.token.value")
    vi.stubGlobal(
      "fetch",
      vi.fn()
        .mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              data: {
                credential_id: 10,
                key_prefix: "b2b_xxxx",
                api_key: "b2b_secret_1",
                status: "active",
                created_at: "2026-02-20T00:00:00Z",
              },
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          ),
        )
        .mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              data: {
                credential_id: 11,
                key_prefix: "b2b_yyyy",
                api_key: "b2b_secret_2",
                status: "active",
                created_at: "2026-02-20T00:00:00Z",
              },
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          ),
        ),
    )

    const { mutationFn: generateMutationFn } = useGenerateEnterpriseCredential()
    const { mutationFn: rotateMutationFn } = useRotateEnterpriseCredential()
    const generated = await generateMutationFn()
    const rotated = await rotateMutationFn()

    expect(generated.api_key).toBe("b2b_secret_1")
    expect(rotated.api_key).toBe("b2b_secret_2")
    expect(fetch).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/v1/b2b/credentials/generate",
      expect.objectContaining({
        method: "POST",
        headers: { Authorization: "Bearer test.token.value" },
      }),
    )
    expect(fetch).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/v1/b2b/credentials/rotate",
      expect.objectContaining({
        method: "POST",
        headers: { Authorization: "Bearer test.token.value" },
      }),
    )
  })

  it("propagates backend error details and request_id", async () => {
    localStorage.setItem("access_token", "test.token.value")
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "forbidden",
              message: "insufficient role",
              details: { expected_role: "enterprise_admin" },
              request_id: "rid-enterprise-api-1",
            },
          }),
          { status: 403, headers: { "Content-Type": "application/json" } },
        ),
      ),
    )

    const { queryFn } = useEnterpriseCredentials(true)
    await expect(queryFn()).rejects.toEqual(
      expect.objectContaining({
        code: "forbidden",
        status: 403,
        details: { expected_role: "enterprise_admin" },
        requestId: "rid-enterprise-api-1",
      }),
    )
  })

  it("falls back to unknown_error for non json error body", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("oops", { status: 500 })))

    const { mutationFn } = useGenerateEnterpriseCredential()
    try {
      await mutationFn()
    } catch (error) {
      expect(error).toBeInstanceOf(EnterpriseCredentialsApiError)
      expect(error).toMatchObject({
        code: "unknown_error",
        status: 500,
      })
    }
  })
})


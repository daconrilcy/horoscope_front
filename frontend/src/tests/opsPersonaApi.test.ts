import { afterEach, describe, expect, it, vi } from "vitest"

import {
  OpsPersonaApiError,
  getActivePersonaConfig,
  updateActivePersonaConfig,
} from "../api/opsPersona"

const mockApiFetch = vi.fn()

vi.mock("../api/client", async () => {
  const actual = await vi.importActual<typeof import("../api/client")>("../api/client")
  return {
    ...actual,
    apiFetch: (...args: unknown[]) => mockApiFetch(...args),
  }
})

describe("ops persona api", () => {
  afterEach(() => {
    mockApiFetch.mockReset()
    localStorage.clear()
  })

  it("maps abort errors to request_timeout", async () => {
    mockApiFetch.mockRejectedValue(new DOMException("Aborted", "AbortError"))

    await expect(getActivePersonaConfig()).rejects.toMatchObject({
      code: "request_timeout",
      status: 408,
    })
  })

  it("maps generic transport errors to network_error", async () => {
    mockApiFetch.mockRejectedValue(new Error("socket closed"))

    await expect(getActivePersonaConfig()).rejects.toMatchObject({
      code: "network_error",
      status: 0,
    })
  })

  it("keeps backend error details payload", async () => {
    mockApiFetch.mockResolvedValue(
      new Response(
        JSON.stringify({
          error: {
            code: "invalid_persona_config",
            message: "persona config is invalid",
            details: { field: "tone", nested: { reason: "unsupported" } },
          },
        }),
        { status: 422, headers: { "Content-Type": "application/json" } },
      ),
    )

    await expect(
      updateActivePersonaConfig({
        tone: "calm",
        prudence_level: "high",
        scope_policy: "strict",
        response_style: "concise",
      }),
    ).rejects.toEqual(
      expect.objectContaining({
        code: "invalid_persona_config",
        status: 422,
        details: { field: "tone", nested: { reason: "unsupported" } },
      }),
    )
  })

  it("uses OpsPersonaApiError type for transport mapping", async () => {
    mockApiFetch.mockRejectedValue(new DOMException("Aborted", "AbortError"))

    try {
      await getActivePersonaConfig()
    } catch (error) {
      expect(error).toBeInstanceOf(OpsPersonaApiError)
    }
  })
})

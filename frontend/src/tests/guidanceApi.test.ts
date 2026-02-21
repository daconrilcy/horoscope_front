import { afterEach, describe, expect, it, vi } from "vitest"

import {
  GuidanceApiError,
  requestContextualGuidance,
  requestGuidance,
} from "../api/guidance"

const mockApiFetch = vi.fn()

vi.mock("../api/client", async () => {
  const actual = await vi.importActual<typeof import("../api/client")>("../api/client")
  return {
    ...actual,
    apiFetch: (...args: unknown[]) => mockApiFetch(...args),
  }
})

describe("guidance api", () => {
  afterEach(() => {
    mockApiFetch.mockReset()
    localStorage.clear()
  })

  it("maps abort errors to request_timeout", async () => {
    mockApiFetch.mockRejectedValue(new DOMException("Aborted", "AbortError"))

    await expect(requestGuidance({ period: "daily" })).rejects.toMatchObject({
      code: "request_timeout",
      status: 408,
    })
  })

  it("maps generic transport errors to network_error", async () => {
    mockApiFetch.mockRejectedValue(new Error("socket closed"))

    await expect(requestGuidance({ period: "weekly" })).rejects.toMatchObject({
      code: "network_error",
      status: 0,
    })
  })

  it("keeps backend error code/message/details", async () => {
    mockApiFetch.mockResolvedValue(
      new Response(
        JSON.stringify({
          error: {
            code: "invalid_guidance_period",
            message: "guidance period is invalid",
            details: { supported_periods: "daily,weekly" },
          },
        }),
        { status: 422, headers: { "Content-Type": "application/json" } },
      ),
    )

    await expect(requestGuidance({ period: "daily" })).rejects.toEqual(
      expect.objectContaining({
        code: "invalid_guidance_period",
        message: "guidance period is invalid",
        status: 422,
        details: { supported_periods: "daily,weekly" },
      }),
    )
  })

  it("returns contextual guidance payload on success", async () => {
    mockApiFetch.mockResolvedValue(
      new Response(
        JSON.stringify({
          data: {
            guidance_type: "contextual",
            situation: "Situation",
            objective: "Objectif",
            time_horizon: null,
            summary: "Synthese",
            key_points: ["k1"],
            actionable_advice: ["a1"],
            disclaimer: "D",
            attempts: 1,
            fallback_used: false,
            context_message_count: 0,
            generated_at: "2026-02-20T00:00:00+00:00",
          },
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    )

    const result = await requestContextualGuidance({
      situation: "Situation",
      objective: "Objectif",
    })
    expect(result.guidance_type).toBe("contextual")
    expect(result.summary).toBe("Synthese")
  })

  it("uses GuidanceApiError type for transport mapping", async () => {
    mockApiFetch.mockRejectedValue(new DOMException("Aborted", "AbortError"))

    try {
      await requestGuidance({ period: "daily" })
    } catch (error) {
      expect(error).toBeInstanceOf(GuidanceApiError)
    }
  })
})


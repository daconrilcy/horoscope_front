import { afterEach, describe, expect, it, vi } from "vitest"

import {
  PrivacyApiError,
  getDeleteStatus,
  getExportStatus,
  requestDelete,
  requestExport,
} from "../api/privacy"

const mockApiFetch = vi.fn()

vi.mock("../api/client", async () => {
  const actual = await vi.importActual<typeof import("../api/client")>("../api/client")
  return {
    ...actual,
    apiFetch: (...args: unknown[]) => mockApiFetch(...args),
  }
})

describe("privacy api", () => {
  afterEach(() => {
    mockApiFetch.mockReset()
    localStorage.clear()
  })

  it("maps abort errors to request_timeout", async () => {
    mockApiFetch.mockRejectedValue(new DOMException("Aborted", "AbortError"))

    await expect(requestExport()).rejects.toMatchObject({
      code: "request_timeout",
      status: 408,
    })
  })

  it("maps generic transport errors to network_error", async () => {
    mockApiFetch.mockRejectedValue(new Error("socket closed"))

    await expect(requestDelete()).rejects.toMatchObject({
      code: "network_error",
      status: 0,
    })
  })

  it("keeps backend error payload details", async () => {
    mockApiFetch.mockResolvedValue(
      new Response(
        JSON.stringify({
          error: {
            code: "privacy_request_invalid",
            message: "delete confirmation is invalid",
            details: { expected_confirmation: "DELETE", nested: { reason: "missing" } },
          },
        }),
        { status: 422, headers: { "Content-Type": "application/json" } },
      ),
    )

    await expect(requestDelete()).rejects.toEqual(
      expect.objectContaining({
        code: "privacy_request_invalid",
        status: 422,
        details: { expected_confirmation: "DELETE", nested: { reason: "missing" } },
      }),
    )
  })

  it("returns null for privacy_not_found statuses", async () => {
    mockApiFetch.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          error: {
            code: "privacy_not_found",
            message: "privacy export request was not found",
            details: {},
          },
        }),
        { status: 404, headers: { "Content-Type": "application/json" } },
      ),
    )
    mockApiFetch.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          error: {
            code: "privacy_not_found",
            message: "privacy delete request was not found",
            details: {},
          },
        }),
        { status: 404, headers: { "Content-Type": "application/json" } },
      ),
    )

    await expect(getExportStatus()).resolves.toBeNull()
    await expect(getDeleteStatus()).resolves.toBeNull()
  })

  it("uses PrivacyApiError type for transport mapping", async () => {
    mockApiFetch.mockRejectedValue(new DOMException("Aborted", "AbortError"))

    try {
      await requestExport()
    } catch (error) {
      expect(error).toBeInstanceOf(PrivacyApiError)
    }
  })
})

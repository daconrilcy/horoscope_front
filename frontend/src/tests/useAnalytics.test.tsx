import { renderHook } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest"

vi.mock("../config/analytics", () => ({
  ANALYTICS_CONFIG: {
    provider: "plausible",
    enabled: true,
  },
}))

import { SENSITIVE_ANALYTICS_FIELD_NAMES, useAnalytics } from "../hooks/useAnalytics"

describe("useAnalytics", () => {
  const plausibleMock = vi.fn()

  beforeEach(() => {
    plausibleMock.mockReset()
    ;(window as Window & { plausible?: typeof plausibleMock }).plausible = plausibleMock
    localStorage.clear()
  })

  afterEach(() => {
    delete (window as Window & { plausible?: typeof plausibleMock }).plausible
  })

  it("tracks plausible events without requiring cookie consent", () => {
    const { result } = renderHook(() => useAnalytics())

    result.current.track("landing_view", { source: "test" })

    expect(plausibleMock).toHaveBeenCalledWith("landing_view", {
      props: { source: "test" },
    })
  })

  it("retire les champs sensibles avant emission", () => {
    const { result } = renderHook(() => useAnalytics())

    result.current.track("natal_projection_success", {
      route: "/natal",
      state: "success",
      projection_type: "beginner_summary_v1",
      birth_date: "1990-01-15",
      prompt: "raw prompt",
      provider_response: { text: "raw" },
    })

    const payload = plausibleMock.mock.calls[0]?.[1]?.props ?? {}
    expect(payload).toEqual({
      route: "/natal",
      state: "success",
      projection_type: "beginner_summary_v1",
    })
    SENSITIVE_ANALYTICS_FIELD_NAMES.forEach((fieldName) => {
      expect(payload).not.toHaveProperty(fieldName)
    })
  })
})

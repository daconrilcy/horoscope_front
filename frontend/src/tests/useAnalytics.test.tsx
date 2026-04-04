import { renderHook } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest"

vi.mock("../config/analytics", () => ({
  ANALYTICS_CONFIG: {
    provider: "plausible",
    enabled: true,
  },
}))

import { useAnalytics } from "../hooks/useAnalytics"

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
})

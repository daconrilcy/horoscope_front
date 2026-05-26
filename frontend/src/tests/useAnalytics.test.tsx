// Tests du hook analytics central et de la configuration provider locale.
import { renderHook } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest"

type PlausibleMock = ReturnType<typeof vi.fn>

const clearAnalyticsEnv = () => {
  vi.unstubAllEnvs()
  vi.stubEnv("VITE_ANALYTICS_PROVIDER", undefined)
  vi.stubEnv("VITE_ANALYTICS_ENABLED", undefined)
  vi.stubEnv("VITE_ANALYTICS_DOMAIN", undefined)
  vi.stubEnv("VITE_ANALYTICS_API_HOST", undefined)
}

const loadAnalyticsHook = async () => {
  vi.resetModules()
  return import("../hooks/useAnalytics")
}

describe("useAnalytics", () => {
  const plausibleMock = vi.fn()

  beforeEach(() => {
    clearAnalyticsEnv()
    plausibleMock.mockReset()
    ;(window as Window & { plausible?: PlausibleMock }).plausible = plausibleMock
    localStorage.clear()
  })

  afterEach(() => {
    delete (window as Window & { plausible?: PlausibleMock }).plausible
    vi.unstubAllEnvs()
  })

  it("conserve noop comme defaut local sans variables Plausible", async () => {
    const { ANALYTICS_CONFIG } = await import("../config/analytics")
    const { useAnalytics } = await loadAnalyticsHook()
    const consoleDebug = vi.spyOn(console, "debug").mockImplementation(() => undefined)

    const { result } = renderHook(() => useAnalytics())

    result.current.track("landing_view", { source: "local" })

    expect(ANALYTICS_CONFIG).toMatchObject({
      provider: "noop",
      enabled: true,
    })
    expect(consoleDebug).toHaveBeenCalledWith("[Analytics NOOP] landing_view", {
      source: "local",
    })
    expect(plausibleMock).not.toHaveBeenCalled()
    consoleDebug.mockRestore()
  })

  it("tracks plausible events without requiring cookie consent", async () => {
    vi.stubEnv("VITE_ANALYTICS_PROVIDER", "plausible")
    vi.stubEnv("VITE_ANALYTICS_ENABLED", "true")
    vi.stubEnv("VITE_ANALYTICS_DOMAIN", "app.example.com")
    const { useAnalytics } = await loadAnalyticsHook()
    const { result } = renderHook(() => useAnalytics())

    result.current.track("landing_view", { source: "test" })

    expect(plausibleMock).toHaveBeenCalledWith("landing_view", {
      props: { source: "test" },
    })
  })

  it("retire les champs sensibles avant emission Plausible", async () => {
    vi.stubEnv("VITE_ANALYTICS_PROVIDER", "plausible")
    vi.stubEnv("VITE_ANALYTICS_ENABLED", "true")
    vi.stubEnv("VITE_ANALYTICS_DOMAIN", "app.example.com")
    const { SENSITIVE_ANALYTICS_FIELD_NAMES, useAnalytics } = await loadAnalyticsHook()
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

import { afterEach, describe, expect, it, vi } from "vitest"

import { GeocodingError, geocodeCity } from "../api/geocoding"

afterEach(() => {
  vi.unstubAllGlobals()
})

describe("geocodeCity", () => {
  it("returns { lat, lon, display_name } when Nominatim finds a result", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [
          { lat: "48.8566", lon: "2.3522", display_name: "Paris, Île-de-France, France" },
        ],
      }),
    )

    const result = await geocodeCity("Paris", "France")

    expect(result).not.toBeNull()
    expect(result?.lat).toBeCloseTo(48.8566)
    expect(result?.lon).toBeCloseTo(2.3522)
    expect(result?.display_name).toBe("Paris, Île-de-France, France")
  })

  it("sends correct URL with encoded query and User-Agent header", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ lat: "48.8566", lon: "2.3522", display_name: "Paris, France" }],
    })
    vi.stubGlobal("fetch", fetchMock)

    await geocodeCity("Paris", "France")

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("nominatim.openstreetmap.org/search")
    expect(url).toContain("q=Paris,France")
    expect(url).toContain("format=json")
    expect(url).toContain("limit=1")
    expect((init.headers as Record<string, string>)["User-Agent"]).toMatch(/horoscope-app/)
  })

  it("returns null when Nominatim returns an empty array (city not found)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [],
      }),
    )

    const result = await geocodeCity("XyzUnknownCity", "ZZ")

    expect(result).toBeNull()
  })

  it("throws GeocodingError with code service_unavailable on network error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Network error")))

    await expect(geocodeCity("Paris", "France")).rejects.toBeInstanceOf(GeocodingError)
    await expect(geocodeCity("Paris", "France")).rejects.toMatchObject({ code: "service_unavailable" })
  })

  it("throws GeocodingError with code service_unavailable on non-OK response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
      }),
    )

    await expect(geocodeCity("Paris", "France")).rejects.toBeInstanceOf(GeocodingError)
    await expect(geocodeCity("Paris", "France")).rejects.toMatchObject({ code: "service_unavailable" })
  })

  it("throws GeocodingError with code service_unavailable on AbortError (timeout)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new DOMException("Aborted", "AbortError")))

    await expect(geocodeCity("Paris", "France")).rejects.toBeInstanceOf(GeocodingError)
    await expect(geocodeCity("Paris", "France")).rejects.toMatchObject({ code: "service_unavailable" })
  })
})

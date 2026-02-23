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

  it("properly encodes city and country with special characters in the URL", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ lat: "40.7128", lon: "-74.0060", display_name: "New York City, New York, United States" }],
    })
    vi.stubGlobal("fetch", fetchMock)

    await geocodeCity("New York", "United States")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=New%20York,United%20States")
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

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect(err).toMatchObject({ code: "service_unavailable" })
  })

  it("throws GeocodingError with code service_unavailable on non-OK response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
      }),
    )

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect(err).toMatchObject({ code: "service_unavailable" })
  })

  it("throws GeocodingError with code service_unavailable on AbortError (timeout)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new DOMException("Aborted", "AbortError")))

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect(err).toMatchObject({ code: "service_unavailable" })
  })

  it("throws GeocodingError when externalSignal is aborted before fetch resolves", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((_url: string, init: RequestInit) => {
        return new Promise<never>((_resolve, reject) => {
          init.signal?.addEventListener("abort", () => {
            reject(new DOMException("Aborted", "AbortError"))
          })
        })
      }),
    )

    const externalController = new AbortController()
    const promise = geocodeCity("Paris", "France", externalController.signal)
    externalController.abort()

    const err = await promise.catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect(err).toMatchObject({ code: "service_unavailable" })
  })

  it("returns null immediately when externalSignal is already aborted (early return)", async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal("fetch", fetchMock)

    const alreadyAbortedController = new AbortController()
    alreadyAbortedController.abort()

    const result = await geocodeCity("Paris", "France", alreadyAbortedController.signal)

    expect(result).toBeNull()
    // Fetch should never be called when signal is pre-aborted
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it("removes abort listener from externalSignal after successful fetch (no memory leak)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [{ lat: "48.8566", lon: "2.3522", display_name: "Paris, France" }],
      }),
    )

    const controller = new AbortController()
    const addEventListenerSpy = vi.spyOn(controller.signal, "addEventListener")
    const removeEventListenerSpy = vi.spyOn(controller.signal, "removeEventListener")

    await geocodeCity("Paris", "France", controller.signal)

    // Verify the same handler function is passed to both add and remove
    expect(addEventListenerSpy).toHaveBeenCalledWith("abort", expect.any(Function), { once: true })
    expect(removeEventListenerSpy).toHaveBeenCalledWith("abort", expect.any(Function))

    // Extract the handler functions to verify they are the same reference
    const addedHandler = addEventListenerSpy.mock.calls[0][1]
    const removedHandler = removeEventListenerSpy.mock.calls[0][1]
    expect(addedHandler).toBe(removedHandler)
  })

  it("properly encodes city names with accents (São Paulo)", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ lat: "-23.5505", lon: "-46.6333", display_name: "São Paulo, Brazil" }],
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("São Paulo", "Brazil")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=S%C3%A3o%20Paulo,Brazil")
    expect(result?.lat).toBeCloseTo(-23.5505)
    expect(result?.lon).toBeCloseTo(-46.6333)
  })

  it("properly encodes city names with apostrophes (L'Aquila)", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ lat: "42.3498", lon: "13.3995", display_name: "L'Aquila, Abruzzo, Italy" }],
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("L'Aquila", "Italy")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=L'Aquila,Italy")
    expect(result?.lat).toBeCloseTo(42.3498)
  })

  it("properly encodes city names with hyphens (Bois-d'Arcy)", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ lat: "48.8003", lon: "2.0367", display_name: "Bois-d'Arcy, Yvelines, France" }],
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("Bois-d'Arcy", "France")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=Bois-d'Arcy,France")
    expect(result?.lat).toBeCloseTo(48.8003)
  })

  it("properly encodes German city names with umlauts (München)", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ lat: "48.1351", lon: "11.5820", display_name: "München, Bavaria, Germany" }],
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("München", "Germany")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=M%C3%BCnchen,Germany")
    expect(result?.lat).toBeCloseTo(48.1351)
  })

  it("properly encodes Japanese city names (東京)", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ lat: "35.6762", lon: "139.6503", display_name: "東京都, Japan" }],
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("東京", "Japan")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=%E6%9D%B1%E4%BA%AC,Japan")
    expect(result?.lat).toBeCloseTo(35.6762)
  })

  it("throws GeocodingError when Nominatim returns invalid lat (NaN)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [{ lat: "not_a_number", lon: "2.3522", display_name: "Paris, France" }],
      }),
    )

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect((err as GeocodingError).message).toContain("invalid coordinates")
  })

  it("throws GeocodingError when Nominatim returns invalid lon (NaN)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [{ lat: "48.8566", lon: "invalid", display_name: "Paris, France" }],
      }),
    )

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect((err as GeocodingError).message).toContain("invalid coordinates")
  })
})

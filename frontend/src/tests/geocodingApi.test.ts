import { afterEach, describe, expect, it, vi } from "vitest"

import { GeocodingError, geocodeCity } from "../api/geocoding"

afterEach(() => {
  vi.unstubAllGlobals()
})

/** Construit une réponse backend succès avec les résultats fournis. */
function backendSuccess(results: Array<{ lat: number; lon: number; display_name: string }>) {
  return {
    ok: true,
    json: async () => ({
      data: {
        results: results.map((result, index) => ({
          provider: "nominatim",
          provider_place_id: 1000 + index,
          ...result,
        })),
        count: results.length,
      },
      meta: { request_id: "rid-test" },
    }),
  }
}

/** Réponse backend avec liste vide (lieu non trouvé). */
const backendNotFound = {
  ok: true,
  json: async () => ({ data: { results: [], count: 0 }, meta: { request_id: "rid-test" } }),
}

function backendResolveSuccess(
  payload: { id?: number; latitude: number; longitude: number; display_name: string },
) {
  return {
    ok: true,
    json: async () => ({
      data: {
        id: payload.id ?? 42,
        latitude: payload.latitude,
        longitude: payload.longitude,
        display_name: payload.display_name,
      },
      meta: { request_id: "rid-test" },
    }),
  }
}

describe("geocodeCity", () => {
  it("returns { lat, lon, display_name } when backend finds a result", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn()
        .mockResolvedValueOnce(
          backendSuccess([{ lat: 48.8566, lon: 2.3522, display_name: "Paris, Île-de-France, France" }]),
        )
        .mockResolvedValueOnce(
          backendResolveSuccess({
            id: 42,
            latitude: 48.8566,
            longitude: 2.3522,
            display_name: "Paris, Île-de-France, France",
          }),
        ),
    )

    const result = await geocodeCity("Paris", "France")

    expect(result).not.toBeNull()
    expect(result?.place_resolved_id).toBe(42)
    expect(result?.lat).toBeCloseTo(48.8566)
    expect(result?.lon).toBeCloseTo(2.3522)
    expect(result?.display_name).toBe("Paris, Île-de-France, France")
  })

  it("sends request to backend geocoding endpoint with encoded query", async () => {
    const fetchMock = vi.fn().mockResolvedValue(backendNotFound)
    vi.stubGlobal("fetch", fetchMock)

    await geocodeCity("Paris", "France")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("/v1/geocoding/search")
    expect(url).toContain("limit=1")
    // Le User-Agent n'est plus envoyé par le frontend (géré par le backend)
    expect(url).not.toContain("nominatim.openstreetmap.org")
  })

  it("calls resolve endpoint after a successful search", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(
        backendSuccess([{ lat: 48.8566, lon: 2.3522, display_name: "Paris, Île-de-France, France" }]),
      )
      .mockResolvedValueOnce(
        backendResolveSuccess({
          id: 123,
          latitude: 48.8566,
          longitude: 2.3522,
          display_name: "Paris, Île-de-France, France",
        }),
      )
    vi.stubGlobal("fetch", fetchMock)

    await geocodeCity("Paris", "France")

    const [, resolveInit] = fetchMock.mock.calls[1] as [string, RequestInit]
    const [resolveUrl] = fetchMock.mock.calls[1] as [string, RequestInit]
    expect(resolveUrl).toContain("/v1/geocoding/resolve")
    expect(resolveInit.method).toBe("POST")
  })

  it("properly encodes city and country in the query parameter", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(
        backendSuccess([{ lat: 40.7128, lon: -74.006, display_name: "New York City, New York, United States" }]),
      )
      .mockResolvedValueOnce(
        backendResolveSuccess({
          latitude: 40.7128,
          longitude: -74.006,
          display_name: "New York City, New York, United States",
        }),
      )
    vi.stubGlobal("fetch", fetchMock)

    await geocodeCity("New York", "United States")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=")
    expect(url).toContain("New%20York")
    expect(url).toContain("United%20States")
  })

  it("returns null when backend returns empty results (city not found)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(backendNotFound))

    const result = await geocodeCity("XyzUnknownCity", "ZZ")

    expect(result).toBeNull()
  })

  it("throws GeocodingError with code service_unavailable on network error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Network error")))

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect(err).toMatchObject({ code: "service_unavailable" })
  })

  it("throws GeocodingError with backend error code on non-OK response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({
          error: { code: "geocoding_provider_unavailable", message: "Unavailable" },
        }),
      }),
    )

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect(err).toMatchObject({ code: "geocoding_provider_unavailable" })
  })

  it("throws GeocodingError with geocoding_rate_limited code on 429 response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 429,
        json: async () => ({
          error: { code: "geocoding_rate_limited", message: "Rate limited" },
        }),
      }),
    )

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect(err).toMatchObject({ code: "geocoding_rate_limited" })
  })

  it("throws GeocodingError with service_unavailable code on AbortError (timeout)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new DOMException("Aborted", "AbortError")))

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect(err).toMatchObject({ code: "service_unavailable" })
  })

  it("returns null when externalSignal is aborted before fetch resolves", async () => {
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

    await expect(promise).resolves.toBeNull()
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
      vi.fn()
        .mockResolvedValueOnce(
          backendSuccess([{ lat: 48.8566, lon: 2.3522, display_name: "Paris, France" }]),
        )
        .mockResolvedValueOnce(
          backendResolveSuccess({
            id: 42,
            latitude: 48.8566,
            longitude: 2.3522,
            display_name: "Paris, France",
          }),
        ),
    )

    const controller = new AbortController()
    const addEventListenerSpy = vi.spyOn(controller.signal, "addEventListener")
    const removeEventListenerSpy = vi.spyOn(controller.signal, "removeEventListener")

    await geocodeCity("Paris", "France", controller.signal)

    expect(addEventListenerSpy).toHaveBeenCalledWith("abort", expect.any(Function), { once: true })
    expect(removeEventListenerSpy).toHaveBeenCalledWith("abort", expect.any(Function))

    const addedHandler = addEventListenerSpy.mock.calls[0][1]
    const removedHandler = removeEventListenerSpy.mock.calls[0][1]
    expect(addedHandler).toBe(removedHandler)
  })

  it("properly encodes city names with accents (São Paulo)", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(
        backendSuccess([{ lat: -23.5505, lon: -46.6333, display_name: "São Paulo, Brazil" }]),
      )
      .mockResolvedValueOnce(
        backendResolveSuccess({
          latitude: -23.5505,
          longitude: -46.6333,
          display_name: "São Paulo, Brazil",
        }),
      )
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("São Paulo", "Brazil")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=")
    expect(url).toContain("S%C3%A3o%20Paulo")
    expect(result?.lat).toBeCloseTo(-23.5505)
    expect(result?.lon).toBeCloseTo(-46.6333)
  })

  it("properly encodes city names with apostrophes (L'Aquila)", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(
        backendSuccess([{ lat: 42.3498, lon: 13.3995, display_name: "L'Aquila, Abruzzo, Italy" }]),
      )
      .mockResolvedValueOnce(
        backendResolveSuccess({
          latitude: 42.3498,
          longitude: 13.3995,
          display_name: "L'Aquila, Abruzzo, Italy",
        }),
      )
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("L'Aquila", "Italy")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=")
    expect(result?.lat).toBeCloseTo(42.3498)
  })

  it("properly encodes city names with hyphens (Bois-d'Arcy)", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(
        backendSuccess([{ lat: 48.8003, lon: 2.0367, display_name: "Bois-d'Arcy, Yvelines, France" }]),
      )
      .mockResolvedValueOnce(
        backendResolveSuccess({
          latitude: 48.8003,
          longitude: 2.0367,
          display_name: "Bois-d'Arcy, Yvelines, France",
        }),
      )
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("Bois-d'Arcy", "France")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("q=")
    expect(result?.lat).toBeCloseTo(48.8003)
  })

  it("properly encodes German city names with umlauts (München)", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(
        backendSuccess([{ lat: 48.1351, lon: 11.582, display_name: "München, Bavaria, Germany" }]),
      )
      .mockResolvedValueOnce(
        backendResolveSuccess({
          latitude: 48.1351,
          longitude: 11.582,
          display_name: "München, Bavaria, Germany",
        }),
      )
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("München", "Germany")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("M%C3%BCnchen")
    expect(result?.lat).toBeCloseTo(48.1351)
  })

  it("properly encodes Japanese city names (東京)", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(
        backendSuccess([{ lat: 35.6762, lon: 139.6503, display_name: "東京都, Japan" }]),
      )
      .mockResolvedValueOnce(
        backendResolveSuccess({
          latitude: 35.6762,
          longitude: 139.6503,
          display_name: "東京都, Japan",
        }),
      )
    vi.stubGlobal("fetch", fetchMock)

    const result = await geocodeCity("東京", "Japan")

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain("%E6%9D%B1%E4%BA%AC")
    expect(result?.lat).toBeCloseTo(35.6762)
  })

  it("throws GeocodingError when backend returns invalid lat (NaN)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          data: {
            results: [{ lat: NaN, lon: 2.3522, display_name: "Paris, France" }],
            count: 1,
          },
        }),
      }),
    )

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect((err as GeocodingError).message).toContain("invalid coordinates")
  })

  it("throws GeocodingError when backend returns invalid lon (NaN)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          data: {
            results: [{ lat: 48.8566, lon: NaN, display_name: "Paris, France" }],
            count: 1,
          },
        }),
      }),
    )

    const err = await geocodeCity("Paris", "France").catch((e: unknown) => e)
    expect(err).toBeInstanceOf(GeocodingError)
    expect((err as GeocodingError).message).toContain("invalid coordinates")
  })
})

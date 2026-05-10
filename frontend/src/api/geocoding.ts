import { apiFetch, parseApiErrorDetails } from "./client"

/** Timeout en ms pour les requêtes de géocodage vers le backend (15s pour laisser le temps à Nominatim) */
const GEOCODING_TIMEOUT_MS = 15000

export type GeocodingResult = {
  place_resolved_id: number
  lat: number
  lon: number
  display_name: string
  timezone_iana?: string | null
}

export class GeocodingError extends Error {
  readonly code: string

  constructor(message: string, code?: string) {
    super(message)
    this.name = "GeocodingError"
    this.code = code ?? "service_unavailable"
  }
}

export type ReverseGeocodingResult = {
  display_name: string
  city: string | null
  country: string | null
  lat: number
  lon: number
  timezone_iana: string | null
}

/**
 * Inverse le géocodage (coordonnées -> lieu) via le backend.
 */
export async function reverseGeocode(
  lat: number,
  lon: number,
  accessToken: string,
  lang?: string,
): Promise<ReverseGeocodingResult> {
  const url = lang
    ? `/v1/geocoding/reverse?lang=${lang}`
    : "/v1/geocoding/reverse"

  try {
    const response = await apiFetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ lat, lon }),
      timeoutMs: GEOCODING_TIMEOUT_MS,
    })

    if (!response.ok) {
      const error = await parseApiErrorDetails(response, {})
      const errorCode = error.code === "unknown_error" ? "service_unavailable" : error.code
      throw new GeocodingError(`Reverse geocoding backend error: ${response.status}`, errorCode)
    }

    const payload = (await response.json()) as { data: ReverseGeocodingResult }
    return payload.data
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new GeocodingError("Reverse geocoding timed out", "service_unavailable")
    }
    throw err
  }
}

/**
 * Géocode une ville via le proxy backend (qui interroge Nominatim côté serveur).
 * @param city - Nom de la ville à géocoder
 * @param country - Nom du pays (améliore la précision du géocodage)
 * @param externalSignal - Signal d'annulation optionnel pour interrompre la requête
 * @returns Coordonnées et nom résolu si trouvé, null si non trouvé ou annulé
 * @throws {GeocodingError} Si le service est indisponible ou retourne des données invalides
 */
export async function geocodeCity(
  city: string,
  country: string,
  externalSignal?: AbortSignal,
): Promise<GeocodingResult | null> {
  // Early return si déjà annulé
  if (externalSignal?.aborted) {
    return null
  }
  let timedOut = false
  const timeoutId = window.setTimeout(() => {
    timedOut = true
  }, GEOCODING_TIMEOUT_MS)

  try {
    const q = encodeURIComponent(`${city.trim()}, ${country.trim()}`)
    const response = await apiFetch(`/v1/geocoding/search?q=${q}&limit=1`, {
      signal: externalSignal,
      timeoutMs: GEOCODING_TIMEOUT_MS,
    })

    if (!response.ok) {
      const error = await parseApiErrorDetails(response, {})
      const errorCode = error.code === "unknown_error" ? "service_unavailable" : error.code
      throw new GeocodingError(`Geocoding backend error: ${response.status}`, errorCode)
    }

    const payload = (await response.json()) as {
      data: {
        results: Array<{
          provider: string
          provider_place_id: number
          lat: number
          lon: number
          display_name: string
          [key: string]: unknown
        }>
        count: number
      }
    }
    const results = payload.data?.results ?? []
    if (results.length === 0) return null

    const candidate = results[0]
    const { lat, lon } = candidate
    if (!isFinite(lat) || !isFinite(lon)) {
      throw new GeocodingError("Backend returned invalid coordinates", "service_unavailable")
    }

    const resolveResponse = await apiFetch("/v1/geocoding/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: externalSignal,
      timeoutMs: GEOCODING_TIMEOUT_MS,
      body: JSON.stringify({
        provider: candidate.provider,
        provider_place_id: candidate.provider_place_id,
        snapshot: candidate,
      }),
    })

    if (!resolveResponse.ok) {
      const error = await parseApiErrorDetails(resolveResponse, {})
      const errorCode = error.code === "unknown_error" ? "service_unavailable" : error.code
      throw new GeocodingError(`Geocoding resolve backend error: ${resolveResponse.status}`, errorCode)
    }

    const resolvePayload = (await resolveResponse.json()) as {
      data: { id: number; latitude: number; longitude: number; display_name: string; timezone_iana?: string | null }
    }
    const resolved = resolvePayload.data
    if (
      Number.isInteger(resolved?.id) &&
      resolved.id > 0 &&
      isFinite(resolved.latitude) &&
      isFinite(resolved.longitude)
    ) {
      return {
        place_resolved_id: resolved.id,
        lat: resolved.latitude,
        lon: resolved.longitude,
        display_name: resolved.display_name,
        timezone_iana: resolved.timezone_iana ?? null,
      }
    }
    
    throw new GeocodingError("Backend returned malformed resolved data", "service_unavailable")
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      if (!timedOut && externalSignal?.aborted) {
        return null
      }
    }
    if (err instanceof GeocodingError) throw err
    throw new GeocodingError("Geocoding service unavailable", "service_unavailable")
  } finally {
    window.clearTimeout(timeoutId)
  }
}

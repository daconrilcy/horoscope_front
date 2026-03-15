import { geocodeCity, GeocodingError } from "@api/geocoding"

export type GeocodingState = "idle" | "loading" | "success" | "error_not_found" | "error_unavailable"

export type GeoResult = {
  place_resolved_id: number
  lat: number
  lon: number
  display_name: string
  timezone_iana?: string | null
} | null

/**
 * Splits a "City, Country" birth_place string into separate city and country parts.
 */
export function inferCityCountryFromBirthPlace(
  birthPlace: string | undefined,
): { city: string; country: string } {
  if (!birthPlace) return { city: "", country: "" }
  const chunks = birthPlace
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
  if (chunks.length === 0) return { city: "", country: "" }
  if (chunks.length === 1) return { city: chunks[0], country: "" }
  return {
    city: chunks[0],
    country: chunks[chunks.length - 1],
  }
}

/**
 * Calls geocodeCity with abort-signal support.
 * The caller is responsible for managing the AbortController lifecycle.
 * Returns the geocoding result and a flag indicating a service-level failure.
 */
export async function performGeocode(
  city: string,
  country: string,
  signal: AbortSignal,
): Promise<{ result: GeoResult; isServiceUnavailable: boolean }> {
  if (!city || !country) return { result: null, isServiceUnavailable: false }

  try {
    const result = await geocodeCity(city, country, signal)
    return { result, isServiceUnavailable: false }
  } catch (err) {
    return { result: null, isServiceUnavailable: err instanceof GeocodingError }
  }
}

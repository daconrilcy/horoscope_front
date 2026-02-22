const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
const GEOCODING_TIMEOUT_MS = 10000
const NOMINATIM_USER_AGENT = "horoscope-app/1.0 (contact: admin@horoscope.app)"

export type GeocodingResult = {
  lat: number
  lon: number
  display_name: string
}

export class GeocodingError extends Error {
  readonly code: "service_unavailable"

  constructor(message: string) {
    super(message)
    this.name = "GeocodingError"
    this.code = "service_unavailable"
  }
}

export async function geocodeCity(city: string, country: string): Promise<GeocodingResult | null> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), GEOCODING_TIMEOUT_MS)
  try {
    const q = `${encodeURIComponent(city.trim())},${encodeURIComponent(country.trim())}`
    const url = `${NOMINATIM_URL}?q=${q}&format=json&limit=1`
    const response = await fetch(url, {
      headers: { "User-Agent": NOMINATIM_USER_AGENT },
      signal: controller.signal,
    })
    if (!response.ok) {
      throw new GeocodingError(`Nominatim returned status ${response.status}`)
    }
    const data = (await response.json()) as Array<{ lat: string; lon: string; display_name: string }>
    if (data.length === 0) return null
    return {
      lat: parseFloat(data[0].lat),
      lon: parseFloat(data[0].lon),
      display_name: data[0].display_name,
    }
  } catch (err) {
    if (err instanceof GeocodingError) throw err
    throw new GeocodingError("Service de géocodage indisponible")
  } finally {
    clearTimeout(timeoutId)
  }
}

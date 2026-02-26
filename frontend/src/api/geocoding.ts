import { API_BASE_URL } from "./client"

/** Timeout en ms pour les requêtes de géocodage vers le backend (15s pour laisser le temps à Nominatim) */
const GEOCODING_TIMEOUT_MS = 15000

export type GeocodingResult = {
  lat: number
  lon: number
  display_name: string
}

export class GeocodingError extends Error {
  readonly code: string

  constructor(message: string, code?: string) {
    super(message)
    this.name = "GeocodingError"
    this.code = code ?? "service_unavailable"
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
  const controller = new AbortController()
  let timedOut = false
  const timeoutId = setTimeout(() => {
    timedOut = true
    controller.abort()
  }, GEOCODING_TIMEOUT_MS)
  const abortHandler = () => controller.abort()
  externalSignal?.addEventListener("abort", abortHandler, { once: true })

  try {
    const q = encodeURIComponent(`${city.trim()}, ${country.trim()}`)
    const url = `${API_BASE_URL}/v1/geocoding/search?q=${q}&limit=1`
    const response = await fetch(url, { signal: controller.signal })

    if (!response.ok) {
      let errorCode = "service_unavailable"
      try {
        const errPayload = (await response.json()) as { error?: { code?: string } }
        errorCode = errPayload.error?.code ?? "service_unavailable"
      } catch {
        // ignore parse failure
      }
      throw new GeocodingError(`Geocoding backend error: ${response.status}`, errorCode)
    }

    const payload = (await response.json()) as {
      data: { results: Array<{ lat: number; lon: number; display_name: string }>; count: number }
    }
    const results = payload.data?.results ?? []
    if (results.length === 0) return null

    const { lat, lon, display_name } = results[0]
    if (!isFinite(lat) || !isFinite(lon)) {
      throw new GeocodingError("Backend returned invalid coordinates", "service_unavailable")
    }
    return { lat, lon, display_name }
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      if (!timedOut && externalSignal?.aborted) {
        return null
      }
    }
    if (err instanceof GeocodingError) throw err
    throw new GeocodingError("Geocoding service unavailable", "service_unavailable")
  } finally {
    clearTimeout(timeoutId)
    externalSignal?.removeEventListener("abort", abortHandler)
  }
}

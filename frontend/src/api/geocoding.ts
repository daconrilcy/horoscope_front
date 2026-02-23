/** URL de base de l'API Nominatim (OpenStreetMap) pour le géocodage */
const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
/** Timeout en ms pour les requêtes de géocodage (10 secondes) */
const GEOCODING_TIMEOUT_MS = 10000
/** User-Agent pour Nominatim (requis par leur ToS). Version statique — à synchroniser si nécessaire. */
const NOMINATIM_USER_AGENT = "horoscope-app/1.0"

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

/**
 * Géocode une ville via l'API Nominatim (OpenStreetMap).
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
  // Early return if already aborted to avoid unnecessary setup and fetch
  if (externalSignal?.aborted) {
    return null
  }
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), GEOCODING_TIMEOUT_MS)
  // Handler stocké pour pouvoir le retirer dans finally (évite fuite mémoire si signal réutilisé)
  const abortHandler = () => controller.abort()
  externalSignal?.addEventListener("abort", abortHandler, { once: true })
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
    const lat = parseFloat(data[0].lat)
    const lon = parseFloat(data[0].lon)
    if (!isFinite(lat) || !isFinite(lon)) {
      throw new GeocodingError("Nominatim returned invalid coordinates")
    }
    return { lat, lon, display_name: data[0].display_name }
  } catch (err) {
    if (err instanceof GeocodingError) throw err
    throw new GeocodingError("Geocoding service unavailable")
  } finally {
    clearTimeout(timeoutId)
    externalSignal?.removeEventListener("abort", abortHandler)
  }
}

import { API_BASE_URL, apiFetch } from "./client"

export type AstroProfile = {
  sun_sign_code: string | null
  ascendant_sign_code: string | null
  missing_birth_time: boolean
}

export type BirthProfileData = {
  birth_date: string
  birth_time: string | null
  birth_place: string
  birth_timezone: string
  place_resolved_id?: number
  birth_city?: string
  birth_country?: string
  birth_lat?: number
  birth_lon?: number
  astro_profile?: AstroProfile

  // Story 30.19: Geolocation consent and current location.
  geolocation_consent: boolean
  current_city?: string | null
  current_country?: string | null
  current_lat?: number | null
  current_lon?: number | null
  current_location_display?: string | null
  current_timezone?: string | null
}

type RawBirthProfileData = BirthProfileData & {
  birth_place_text?: string
  birth_place_resolved_id?: number
  birth_place_resolved?: unknown
}

export class BirthProfileApiError extends Error {
  code: string
  status: number
  requestId?: string

  constructor(code: string, message: string, status: number, requestId?: string) {
    super(message)
    this.name = "BirthProfileApiError"
    this.code = code
    this.status = status
    this.requestId = requestId
  }
}

function normalizeBirthProfileData(data: RawBirthProfileData): BirthProfileData {
  return {
    birth_date: data.birth_date,
    birth_time: data.birth_time,
    birth_place: data.birth_place,
    birth_timezone: data.birth_timezone,
    place_resolved_id: data.place_resolved_id ?? data.birth_place_resolved_id,
    birth_city: data.birth_city,
    birth_country: data.birth_country,
    birth_lat: data.birth_lat,
    birth_lon: data.birth_lon,
    astro_profile: data.astro_profile,
    geolocation_consent: data.geolocation_consent,
    current_city: data.current_city,
    current_country: data.current_country,
    current_lat: data.current_lat,
    current_lon: data.current_lon,
    current_location_display: data.current_location_display,
    current_timezone: data.current_timezone,
  }
}

function serializeBirthProfileData(data: BirthProfileData): BirthProfileData {
  return {
    birth_date: data.birth_date,
    birth_time: data.birth_time,
    birth_place: data.birth_place,
    birth_timezone: data.birth_timezone,
    ...(data.place_resolved_id !== undefined ? { place_resolved_id: data.place_resolved_id } : {}),
    ...(data.birth_city !== undefined ? { birth_city: data.birth_city } : {}),
    ...(data.birth_country !== undefined ? { birth_country: data.birth_country } : {}),
    ...(data.birth_lat !== undefined ? { birth_lat: data.birth_lat } : {}),
    ...(data.birth_lon !== undefined ? { birth_lon: data.birth_lon } : {}),
    geolocation_consent: data.geolocation_consent,
    ...(data.current_city !== undefined ? { current_city: data.current_city } : {}),
    ...(data.current_country !== undefined ? { current_country: data.current_country } : {}),
    ...(data.current_lat !== undefined ? { current_lat: data.current_lat } : {}),
    ...(data.current_lon !== undefined ? { current_lon: data.current_lon } : {}),
    ...(data.current_location_display !== undefined
      ? { current_location_display: data.current_location_display }
      : {}),
    ...(data.current_timezone !== undefined ? { current_timezone: data.current_timezone } : {}),
  }
}

export async function getBirthData(accessToken: string): Promise<BirthProfileData | null> {
  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/birth-data`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })

  if (response.status === 404) {
    return null
  }

  if (!response.ok) {
    let payload: { error: { code: string; message: string; request_id?: string } } | null = null
    try {
      payload = await response.json()
    } catch {
      payload = null
    }
    throw new BirthProfileApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `HTTP ${response.status}`,
      response.status,
      payload?.error?.request_id,
    )
  }

  const payload = (await response.json()) as {
    data: RawBirthProfileData
    meta: { request_id: string }
  }
  return normalizeBirthProfileData(payload.data)
}

export async function saveBirthData(accessToken: string, data: BirthProfileData): Promise<BirthProfileData> {
  const sanitizedPayload = serializeBirthProfileData(data)
  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/birth-data`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(sanitizedPayload),
  })

  if (!response.ok) {
    let payload: { error: { code: string; message: string; request_id?: string } } | null = null
    try {
      payload = await response.json()
    } catch {
      payload = null
    }
    throw new BirthProfileApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `HTTP ${response.status}`,
      response.status,
      payload?.error?.request_id,
    )
  }

  const payload = (await response.json()) as {
    data: RawBirthProfileData
    meta: { request_id: string }
  }
  return normalizeBirthProfileData(payload.data)
}

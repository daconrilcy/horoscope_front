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

  const payload = (await response.json()) as { data: BirthProfileData; meta: { request_id: string } }
  return payload.data
}

export async function saveBirthData(accessToken: string, data: BirthProfileData): Promise<BirthProfileData> {
  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/birth-data`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(data),
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

  const payload = (await response.json()) as { data: BirthProfileData; meta: { request_id: string } }
  return payload.data
}

import { useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"
import { getSubjectFromAccessToken, useAccessTokenSnapshot } from "../utils/authToken"
import { ANONYMOUS_SUBJECT } from "../utils/constants"

type PlanetPosition = {
  planet_code: string
  longitude: number
  sign_code: string
  house_number: number
  is_retrograde?: boolean
  speed_longitude?: number
}

type HouseResult = {
  number: number
  cusp_longitude: number
}

type AspectResult = {
  aspect_code: string
  planet_a: string
  planet_b: string
  angle: number
  orb: number
}

type NatalResult = {
  reference_version: string
  ruleset_version: string
  prepared_input: {
    birth_datetime_local: string
    birth_datetime_utc: string
    timestamp_utc: number
    julian_day: number
    birth_timezone: string
  }
  planet_positions: PlanetPosition[]
  houses: HouseResult[]
  aspects: AspectResult[]
}

export type LatestNatalChart = {
  chart_id: string
  result: NatalResult
  metadata: {
    reference_version: string
    ruleset_version: string
    engine: string
    house_system: string
    degraded_mode?: "no_location" | "no_time" | "no_location_no_time" | null
  }
  created_at: string
  astro_profile?: {
    sun_sign_code: string | null
    ascendant_sign_code: string | null
    missing_birth_time: boolean
  }
}

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    request_id?: string
  }
}

export class ApiError extends Error {
  readonly code: string
  readonly status: number
  readonly requestId?: string

  constructor(code: string, message: string, status: number, requestId?: string) {
    super(message)
    this.code = code
    this.status = status
    this.requestId = requestId
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: ErrorEnvelope | null = null
    try {
      const raw = (await response.json()) as Record<string, unknown>
      if (raw?.error) {
        // Format API standard : { error: { code, message, request_id? } }
        payload = raw as unknown as ErrorEnvelope
      } else if (Array.isArray(raw?.detail)) {
        // Format FastAPI natif 422 : { detail: [{ loc, msg, type }] }
        const firstDetail = (raw.detail as Array<{ msg?: string }>)[0]
        payload = {
          error: {
            code: "unprocessable_entity",
            message: firstDetail?.msg || "Données invalides",
          },
        }
      }
    } catch {
      payload = null
    }
    throw new ApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `Request failed with status ${response.status}`,
      response.status,
      payload?.error?.request_id,
    )
  }

  const payload = (await response.json()) as { data: T }
  return payload.data
}

async function fetchLatestNatalChart(accessToken: string): Promise<LatestNatalChart> {
  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/natal-chart/latest`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })

  return handleResponse<LatestNatalChart>(response)
}

export async function generateNatalChart(
  accessToken: string,
  accurate: boolean = false,
): Promise<LatestNatalChart> {
  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/natal-chart`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ accurate }),
  })

  return handleResponse<LatestNatalChart>(response)
}

export function useLatestNatalChart() {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT
  const fetchForCurrentUser = async () => {
    if (!accessToken) {
      throw new ApiError("unauthorized", "access token is required", 401)
    }
    return fetchLatestNatalChart(accessToken)
  }
  return useQuery({
    queryKey: ["latest-natal-chart", tokenSubject],
    queryFn: fetchForCurrentUser,
    enabled: Boolean(accessToken),
    retryOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        return false
      }
      return failureCount < 2
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

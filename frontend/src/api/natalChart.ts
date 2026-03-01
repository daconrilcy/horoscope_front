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
  orb_used?: number | null
}

type NatalResult = {
  reference_version: string
  ruleset_version: string
  engine?: string
  zodiac?: string
  frame?: string
  ayanamsa?: string | null
  altitude_m?: number | null
  ephemeris_path_version?: string | null
  ephemeris_path_hash?: string | null
  prepared_input: {
    birth_datetime_local: string
    birth_datetime_utc: string
    timestamp_utc: number
    julian_day: number
    birth_timezone: string
    jd_ut: number
    timezone_used: string
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
    ephemeris_path_version?: string | null
    ephemeris_path_hash?: string | null
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

// --- Interpretation ---

export type AstroSection = {
  key: string
  heading: string
  content: string
}

export type AstroInterpretation = {
  title: string
  summary: string
  sections: AstroSection[]
  highlights: string[]
  advice: string[]
  evidence: string[]
  disclaimers: string[]
}

export type InterpretationMeta = {
  level: "short" | "complete"
  use_case: string
  persona_id: string | null
  persona_name: string | null
  prompt_version_id: string | null
  validation_status: string
  repair_attempted: boolean
  fallback_triggered: boolean
  was_fallback: boolean
  latency_ms: number | null
  request_id: string | null
  persisted_at: string | null
}

export type NatalInterpretationResult = {
  chart_id: string
  use_case: string
  interpretation: AstroInterpretation
  meta: InterpretationMeta
  degraded_mode: string | null
}

async function fetchNatalInterpretation(
  accessToken: string,
  useCaseLevel: "short" | "complete",
  personaId?: string | null,
  locale?: string,
  question?: string,
  forceRefresh?: boolean,
): Promise<NatalInterpretationResult> {
  const response = await apiFetch(`${API_BASE_URL}/v1/natal/interpretation`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      use_case_level: useCaseLevel,
      persona_id: personaId,
      locale: locale || "fr-FR",
      question: question,
      force_refresh: forceRefresh || false,
    }),
  })

  return handleResponse<NatalInterpretationResult>(response)
}

export function useNatalInterpretation(options: {
  enabled: boolean
  useCaseLevel: "short" | "complete"
  personaId?: string | null
  locale?: string
  question?: string
  forceRefresh?: boolean
}) {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT

  return useQuery({
    queryKey: [
      "natal-interpretation",
      tokenSubject,
      options.useCaseLevel,
      options.personaId,
      options.locale,
      options.forceRefresh || false,
    ],
    queryFn: async () => {
      if (!accessToken) {
        throw new ApiError("unauthorized", "access token is required", 401)
      }
      return fetchNatalInterpretation(
        accessToken,
        options.useCaseLevel,
        options.personaId,
        options.locale,
        options.question,
        options.forceRefresh,
      )
    },
    enabled: options.enabled && Boolean(accessToken),
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        return false
      }
      return failureCount < 1
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

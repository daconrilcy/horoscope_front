import { useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch, ApiError } from "./client"
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

async function handleResponsePossiblyUnwrapped<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: ErrorEnvelope | null = null
    try {
      const raw = (await response.json()) as Record<string, unknown>
      if (raw?.error) {
        payload = raw as unknown as ErrorEnvelope
      } else if (Array.isArray(raw?.detail)) {
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

  const payload = (await response.json()) as T | { data: T }
  if (
    payload !== null &&
    typeof payload === "object" &&
    "data" in payload &&
    (payload as { data?: T }).data !== undefined
  ) {
    return (payload as { data: T }).data
  }
  return payload as T
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
  disclaimers?: string[]
}

export type InterpretationMeta = {
  id?: number | null
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

export type NatalInterpretationModule =
  | "NATAL_PSY_PROFILE"
  | "NATAL_SHADOW_INTEGRATION"
  | "NATAL_LEADERSHIP_WORKSTYLE"
  | "NATAL_CREATIVITY_JOY"
  | "NATAL_RELATIONSHIP_STYLE"
  | "NATAL_COMMUNITY_NETWORKS"
  | "NATAL_VALUES_SECURITY"
  | "NATAL_EVOLUTION_PATH"

export type NatalInterpretationResult = {
  chart_id: string
  use_case: string
  interpretation: AstroInterpretation
  meta: InterpretationMeta
  degraded_mode: string | null
  disclaimers?: string[]
}

export type NatalInterpretationListItem = {
  id: number
  chart_id: string
  level: "short" | "complete"
  persona_id: string | null
  persona_name: string | null
  module: string | null
  created_at: string
  use_case: string
  prompt_version_id: string | null
  was_fallback: boolean
}

export type NatalInterpretationListResponse = {
  items: NatalInterpretationListItem[]
  total: number
  limit: number
  offset: number
}

export type NatalPdfTemplateItem = {
  key: string
  name: string
  description: string | null
  locale: string
  is_default: boolean
}

export type NatalPdfTemplateListResponse = {
  items: NatalPdfTemplateItem[]
}

async function fetchNatalInterpretation(
  accessToken: string,
  useCaseLevel: "short" | "complete",
  personaId?: string | null,
  locale?: string,
  question?: string,
  forceRefresh?: boolean,
  module?: NatalInterpretationModule,
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
      module: module || null,
    }),
  })

  if (!response.ok) {
    let payload: ErrorEnvelope | null = null
    try {
      const raw = (await response.json()) as Record<string, unknown>
      if (raw?.error) {
        payload = raw as unknown as ErrorEnvelope
      } else if (Array.isArray(raw?.detail)) {
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

  const payload = (await response.json()) as {
    data: NatalInterpretationResult
    disclaimers?: string[]
  }

  // Story 30-8: for V3, disclaimers are API-level, not LLM payload-level.
  if (!payload.data.disclaimers && Array.isArray(payload.disclaimers)) {
    payload.data.disclaimers = payload.disclaimers
  }

  return payload.data
}

export async function deleteNatalInterpretation(
  accessToken: string,
  interpretationId: number,
): Promise<void> {
  const response = await apiFetch(`${API_BASE_URL}/v1/natal/interpretations/${interpretationId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${accessToken}` },
  })

  if (!response.ok && response.status !== 204) {
    throw new ApiError("delete_failed", "Failed to delete interpretation", response.status)
  }
}

export async function downloadNatalInterpretationPdf(
  accessToken: string,
  interpretationId: number,
  templateKey?: string,
  locale?: string,
): Promise<void> {
  const params = new URLSearchParams()
  if (templateKey) params.append("template_key", templateKey)
  if (locale) params.append("locale", locale)

  const response = await apiFetch(
    `${API_BASE_URL}/v1/natal/interpretations/${interpretationId}/pdf?${params.toString()}`,
    {
      headers: { Authorization: `Bearer ${accessToken}` },
    },
  )

  if (!response.ok) {
    throw new ApiError("download_failed", "Failed to download PDF", response.status)
  }

  const blob = await response.blob()
  const contentDisposition = response.headers.get("Content-Disposition")
  triggerBlobDownload(blob, `natal-interpretation-${interpretationId}.pdf`, contentDisposition)
}

function triggerBlobDownload(
  blob: Blob,
  defaultFilename: string,
  contentDisposition?: string | null,
): void {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  // Extract filename from header if possible, else default
  let filename = defaultFilename
  if (contentDisposition && contentDisposition.includes("filename=")) {
    filename = contentDisposition.split("filename=")[1].replace(/"/g, "")
  }
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

export async function previewNatalInterpretationPdf(
  accessToken: string,
  interpretationId: number,
  templateKey?: string,
  locale?: string,
): Promise<void> {
  const params = new URLSearchParams()
  if (templateKey) params.append("template_key", templateKey)
  if (locale) params.append("locale", locale)

  const response = await apiFetch(
    `${API_BASE_URL}/v1/natal/interpretations/${interpretationId}/pdf?${params.toString()}`,
    {
      headers: { Authorization: `Bearer ${accessToken}` },
    },
  )

  if (!response.ok) {
    throw new ApiError("preview_failed", "Failed to preview PDF", response.status)
  }

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const opened = window.open(url, "_blank", "noopener,noreferrer")
  if (!opened) {
    window.URL.revokeObjectURL(url)
    throw new ApiError("preview_blocked", "Popup blocked while opening PDF preview", 0)
  }

  // Leave enough time for the new tab to load the object URL before cleanup.
  window.setTimeout(() => {
    window.URL.revokeObjectURL(url)
  }, 60_000)
}

export function useNatalInterpretationsList(options: {
  enabled: boolean
  chartId?: string
  level?: "short" | "complete"
  limit?: number
  offset?: number
}) {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT

  return useQuery({
    queryKey: [
      "natal-interpretations-list",
      tokenSubject,
      options.chartId,
      options.level,
      options.limit,
      options.offset,
    ],
    queryFn: async () => {
      if (!accessToken) {
        throw new ApiError("unauthorized", "access token is required", 401)
      }
      const params = new URLSearchParams()
      if (options.chartId) params.append("chart_id", options.chartId)
      if (options.level) params.append("level", options.level)
      if (options.limit) params.append("limit", options.limit.toString())
      if (options.offset) params.append("offset", options.offset.toString())

      const response = await apiFetch(
        `${API_BASE_URL}/v1/natal/interpretations?${params.toString()}`,
        {
          headers: { Authorization: `Bearer ${accessToken}` },
        },
      )

      return handleResponsePossiblyUnwrapped<NatalInterpretationListResponse>(response)
    },
    enabled: options.enabled && Boolean(accessToken),
    staleTime: 1000 * 60 * 5,
  })
}

export function useNatalPdfTemplates(options: { enabled: boolean; locale?: string }) {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT
  return useQuery({
    queryKey: ["natal-pdf-templates", tokenSubject, options.locale],
    queryFn: async () => {
      if (!accessToken) {
        throw new ApiError("unauthorized", "access token is required", 401)
      }
      const params = new URLSearchParams()
      if (options.locale) params.append("locale", options.locale)
      const response = await apiFetch(`${API_BASE_URL}/v1/natal/pdf-templates?${params.toString()}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      return handleResponsePossiblyUnwrapped<NatalPdfTemplateListResponse>(response)
    },
    enabled: options.enabled && Boolean(accessToken),
    staleTime: 1000 * 60 * 10,
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        return false
      }
      return failureCount < 1
    },
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  })
}

export function useNatalInterpretationById(options: {
  enabled: boolean
  interpretationId?: number
  locale?: string
}) {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT

  return useQuery({
    queryKey: ["natal-interpretation-by-id", tokenSubject, options.interpretationId, options.locale],
    queryFn: async () => {
      if (!accessToken) {
        throw new ApiError("unauthorized", "access token is required", 401)
      }
      if (!options.interpretationId) {
        throw new Error("interpretationId is required")
      }
      const params = new URLSearchParams()
      if (options.locale) params.append("locale", options.locale)

      const response = await apiFetch(
        `${API_BASE_URL}/v1/natal/interpretations/${options.interpretationId}?${params.toString()}`,
        {
          headers: { Authorization: `Bearer ${accessToken}` },
        },
      )

      return handleResponse<NatalInterpretationResult>(response)
    },
    enabled: options.enabled && Boolean(accessToken) && Boolean(options.interpretationId),
    staleTime: 1000 * 60 * 10,
  })
}

export function useNatalInterpretation(options: {
  enabled: boolean
  useCaseLevel: "short" | "complete"
  personaId?: string | null
  locale?: string
  question?: string
  forceRefresh?: boolean
  refreshKey?: number
  module?: NatalInterpretationModule
}) {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT
  const canRunInterpretationQuery =
    options.enabled &&
    Boolean(accessToken) &&
    (options.useCaseLevel === "short" || Boolean(options.personaId))

  return useQuery({
    queryKey: [
      "natal-interpretation",
      tokenSubject,
      options.useCaseLevel,
      options.personaId,
      options.locale,
      options.forceRefresh || false,
      options.refreshKey || 0,
      options.module || null,
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
        options.module,
      )
    },
    enabled: canRunInterpretationQuery,
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        return false
      }
      return failureCount < 1
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

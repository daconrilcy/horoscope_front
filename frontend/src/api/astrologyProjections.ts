// Client API des projections astrologiques B2C consommees par les surfaces publiques.
import { useQueries } from "@tanstack/react-query"

import { API_BASE_URL, ApiError, apiFetch, parseApiErrorDetails } from "./client"
import { getSubjectFromAccessToken, useAccessTokenSnapshot } from "../utils/authToken"
import { ANONYMOUS_SUBJECT } from "../utils/constants"

export const ASTROLOGY_PROJECTION_VERSION = "v1"

export type AstrologyProjectionType =
  | "beginner_summary_v1"
  | "client_interpretation_projection_v1"

export type AstrologyProjectionRequest = {
  chart_id: string
  projection_type: AstrologyProjectionType
  projection_version?: string
  persist?: boolean
}

export type AstrologyProjectionMetadata = {
  source: "chart_id" | "birth_input"
  plan_code: "free" | "basic" | "premium"
  request_id: string
  persisted_id?: number | null
}

export type AstrologyProjectionResponse = {
  chart_id: string
  projection_type: AstrologyProjectionType
  projection_version: string
  persisted: boolean
  projection_hash: string
  payload: Record<string, unknown>
  metadata: AstrologyProjectionMetadata
}

export type AstrologyProjectionQueryState = {
  type: AstrologyProjectionType
  data?: AstrologyProjectionResponse
  isLoading: boolean
  error: unknown
  refetch: () => void
}

const B2C_PROJECTION_TYPES: AstrologyProjectionType[] = [
  "beginner_summary_v1",
  "client_interpretation_projection_v1",
]

/** Appelle le endpoint public de projections via le client HTTP central authentifie. */
export async function requestAstrologyProjection(
  accessToken: string,
  request: AstrologyProjectionRequest,
): Promise<AstrologyProjectionResponse> {
  const response = await apiFetch(`${API_BASE_URL}/v1/astrology/projections`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      chart_id: request.chart_id,
      projection_type: request.projection_type,
      projection_version: request.projection_version ?? ASTROLOGY_PROJECTION_VERSION,
      persist: request.persist ?? false,
    }),
  })

  if (!response.ok) {
    const error = await parseApiErrorDetails(response, {})
    throw new ApiError(
      error.code,
      error.message,
      response.status,
      error.requestId ?? undefined,
    )
  }

  return (await response.json()) as AstrologyProjectionResponse
}

/** Charge les deux projections B2C attendues pour un theme natal deja disponible. */
export function useAstrologyProjections(options: { enabled: boolean; chartId?: string }) {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT

  const queries = useQueries({
    queries: B2C_PROJECTION_TYPES.map((projectionType) => ({
      queryKey: ["astrology-projection", tokenSubject, options.chartId, projectionType, ASTROLOGY_PROJECTION_VERSION],
      queryFn: async () => {
        if (!accessToken) {
          throw new ApiError("unauthorized", "access token is required", 401)
        }
        if (!options.chartId) {
          throw new ApiError("chart_id_required", "chart_id is required", 400)
        }
        return requestAstrologyProjection(accessToken, {
          chart_id: options.chartId,
          projection_type: projectionType,
          projection_version: ASTROLOGY_PROJECTION_VERSION,
          persist: false,
        })
      },
      enabled: options.enabled && Boolean(accessToken) && Boolean(options.chartId),
      retry: (failureCount: number, error: unknown) => {
        if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
          return false
        }
        return failureCount < 1
      },
      refetchOnWindowFocus: false,
    })),
  })

  return B2C_PROJECTION_TYPES.map((type, index): AstrologyProjectionQueryState => ({
    type,
    data: queries[index]?.data,
    isLoading: Boolean(queries[index]?.isLoading),
    error: queries[index]?.error ?? null,
    refetch: () => {
      void queries[index]?.refetch()
    },
  }))
}

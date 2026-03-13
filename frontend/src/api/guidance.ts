import { useMutation } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

export type GuidanceErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
    request_id: string
  }
}

export type GuidancePeriod = "daily" | "weekly"

export type GuidanceRequest = {
  period: GuidancePeriod
  conversation_id?: number | null
}

export type ContextualGuidanceRequest = {
  situation: string
  objective: string
  time_horizon?: string | null
  conversation_id?: number | null
}

export type GuidanceRecoveryMetadata = {
  off_scope_detected: boolean
  off_scope_score: number
  recovery_strategy: string
  recovery_applied: boolean
  recovery_attempts: number
  recovery_reason: string | null
}

export type GuidanceData = {
  period: GuidancePeriod
  summary: string
  key_points: string[]
  actionable_advice: string[]
  disclaimer: string
  attempts: number
  fallback_used: boolean
  recovery: GuidanceRecoveryMetadata
  context_message_count: number
  generated_at: string
}

export type ContextualGuidanceData = {
  guidance_type: string
  situation: string
  objective: string
  time_horizon: string | null
  summary: string
  key_points: string[]
  actionable_advice: string[]
  disclaimer: string
  attempts: number
  fallback_used: boolean
  recovery: GuidanceRecoveryMetadata
  context_message_count: number
  generated_at: string
}

export type GuidanceApiResponse = {
  data: GuidanceData
  meta: {
    request_id: string
  }
}

export type ContextualGuidanceApiResponse = {
  data: ContextualGuidanceData
  meta: {
    request_id: string
  }
}

export class GuidanceApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, unknown>
  readonly request_id?: string

  constructor(
    code: string,
    message: string,
    status: number,
    details: Record<string, unknown> = {},
    request_id?: string
  ) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
    this.request_id = request_id
  }
}

function toTransportError(error: unknown): GuidanceApiError {
  if (error instanceof GuidanceApiError) {
    return error
  }
  if (error instanceof DOMException && error.name === "AbortError") {
    return new GuidanceApiError(
      "request_timeout",
      "La requête a expiré. Réessayez dans un instant.",
      408,
      {}
    )
  }
  return new GuidanceApiError("network_error", "Erreur réseau. Réessayez plus tard.", 0, {})
}

async function requestJson<TData>(path: string, payload: object): Promise<TData> {
  try {
    const response = await apiFetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      let errorPayload: GuidanceErrorEnvelope | null = null
      try {
        errorPayload = (await response.json()) as GuidanceErrorEnvelope
      } catch {
        errorPayload = null
      }

      throw new GuidanceApiError(
        errorPayload?.error?.code ?? "unknown_error",
        errorPayload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        errorPayload?.error?.details ?? {},
        errorPayload?.error?.request_id
      )
    }

    const result = (await response.json()) as { data: TData }
    return result.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function requestGuidance(payload: GuidanceRequest): Promise<GuidanceData> {
  return requestJson<GuidanceData>("/v1/guidance", payload)
}

export async function requestContextualGuidance(
  payload: ContextualGuidanceRequest
): Promise<ContextualGuidanceData> {
  return requestJson<ContextualGuidanceData>("/v1/guidance/contextual", payload)
}

export function useRequestGuidance() {
  return useMutation({
    mutationFn: requestGuidance,
  })
}

export function useRequestContextualGuidance() {
  return useMutation({
    mutationFn: requestContextualGuidance,
  })
}

export function useContextualGuidance() {
  return useMutation({
    mutationFn: requestContextualGuidance,
  })
}

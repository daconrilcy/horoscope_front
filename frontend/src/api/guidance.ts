import { useMutation } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

export type GuidancePeriod = "daily" | "weekly"
export type GuidanceRequestPayload = {
  period: GuidancePeriod
  conversation_id?: number
}

export type ContextualGuidanceRequestPayload = {
  situation: string
  objective: string
  time_horizon?: string
  conversation_id?: number
}

export type GuidanceResponse = {
  period: GuidancePeriod
  summary: string
  key_points: string[]
  actionable_advice: string[]
  disclaimer: string
  attempts: number
  fallback_used: boolean
  recovery: {
    off_scope_detected: boolean
    off_scope_score: number
    recovery_strategy: "none" | "reformulate" | "retry_once" | "safe_fallback"
    recovery_applied: boolean
    recovery_attempts: number
    recovery_reason: string | null
  }
  context_message_count: number
  generated_at: string
}

export type ContextualGuidanceResponse = {
  guidance_type: "contextual"
  situation: string
  objective: string
  time_horizon: string | null
  summary: string
  key_points: string[]
  actionable_advice: string[]
  disclaimer: string
  attempts: number
  fallback_used: boolean
  recovery: {
    off_scope_detected: boolean
    off_scope_score: number
    recovery_strategy: "none" | "reformulate" | "retry_once" | "safe_fallback"
    recovery_applied: boolean
    recovery_attempts: number
    recovery_reason: string | null
  }
  context_message_count: number
  generated_at: string
}

export class GuidanceApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, unknown>

  constructor(code: string, message: string, status: number, details: Record<string, unknown> = {}) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
  }
}

function toTransportError(error: unknown): GuidanceApiError {
  if (error instanceof GuidanceApiError) {
    return error
  }
  if (error instanceof DOMException && error.name === "AbortError") {
    return new GuidanceApiError(
      "request_timeout",
      "La requete a expire. Reessayez dans un instant.",
      408,
      {},
    )
  }
  return new GuidanceApiError("network_error", "Erreur reseau. Reessayez plus tard.", 0, {})
}

export async function requestGuidance(
  requestPayload: GuidanceRequestPayload,
): Promise<GuidanceResponse> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/guidance`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify(requestPayload),
    })

    if (!response.ok) {
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      throw new GuidanceApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }

    const payload = (await response.json()) as { data: GuidanceResponse }
    return payload.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function requestContextualGuidance(
  requestPayload: ContextualGuidanceRequestPayload,
): Promise<ContextualGuidanceResponse> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/guidance/contextual`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify(requestPayload),
    })

    if (!response.ok) {
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      throw new GuidanceApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }

    const payload = (await response.json()) as { data: ContextualGuidanceResponse }
    return payload.data
  } catch (error) {
    throw toTransportError(error)
  }
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

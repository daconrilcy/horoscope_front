import { useMutation, useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

export type OpsPersonaConfig = {
  id: number | null
  version: number
  tone: "calm" | "direct" | "empathetic"
  prudence_level: "standard" | "high"
  scope_policy: "strict" | "balanced"
  response_style: "concise" | "detailed"
  status: string
  rollback_from_id: number | null
  created_by_user_id: number | null
  created_at: string | null
  is_default: boolean
}

export type OpsPersonaUpdatePayload = {
  tone: "calm" | "direct" | "empathetic"
  prudence_level: "standard" | "high"
  scope_policy: "strict" | "balanced"
  response_style: "concise" | "detailed"
}

type OpsPersonaRollbackData = {
  active: OpsPersonaConfig
  rolled_back_version: number
}

export class OpsPersonaApiError extends Error {
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

function toTransportError(error: unknown): OpsPersonaApiError {
  if (error instanceof OpsPersonaApiError) {
    return error
  }
  if (error instanceof DOMException && error.name === "AbortError") {
    return new OpsPersonaApiError(
      "request_timeout",
      "La requete a expire. Reessayez dans un instant.",
      408,
      {},
    )
  }
  return new OpsPersonaApiError("network_error", "Erreur reseau. Reessayez plus tard.", 0, {})
}

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem("access_token")
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function getActivePersonaConfig(): Promise<OpsPersonaConfig> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/ops/persona/config`, {
      method: "GET",
      headers: getAuthHeader(),
    })
    if (!response.ok) {
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      throw new OpsPersonaApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }
    const payload = (await response.json()) as { data: OpsPersonaConfig }
    return payload.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function updateActivePersonaConfig(
  payload: OpsPersonaUpdatePayload,
): Promise<OpsPersonaConfig> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/ops/persona/config`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(payload),
    })
    if (!response.ok) {
      let errorPayload: ErrorEnvelope | null = null
      try {
        errorPayload = (await response.json()) as ErrorEnvelope
      } catch {
        errorPayload = null
      }
      throw new OpsPersonaApiError(
        errorPayload?.error?.code ?? "unknown_error",
        errorPayload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        errorPayload?.error?.details ?? {},
      )
    }
    const body = (await response.json()) as { data: OpsPersonaConfig }
    return body.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function rollbackPersonaConfig(): Promise<OpsPersonaRollbackData> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/ops/persona/rollback`, {
      method: "POST",
      headers: getAuthHeader(),
    })
    if (!response.ok) {
      let errorPayload: ErrorEnvelope | null = null
      try {
        errorPayload = (await response.json()) as ErrorEnvelope
      } catch {
        errorPayload = null
      }
      throw new OpsPersonaApiError(
        errorPayload?.error?.code ?? "unknown_error",
        errorPayload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        errorPayload?.error?.details ?? {},
      )
    }
    const body = (await response.json()) as { data: OpsPersonaRollbackData }
    return body.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export function useActivePersonaConfig() {
  return useQuery({
    queryKey: ["ops-persona-config"],
    queryFn: getActivePersonaConfig,
  })
}

export function useUpdatePersonaConfig() {
  return useMutation({
    mutationFn: updateActivePersonaConfig,
  })
}

export function useRollbackPersonaConfig() {
  return useMutation({
    mutationFn: rollbackPersonaConfig,
  })
}

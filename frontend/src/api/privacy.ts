import { useMutation, useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

export type PrivacyRequestStatus = {
  request_id: number
  request_kind: "export" | "delete"
  status: "requested" | "processing" | "completed" | "failed"
  requested_at: string
  completed_at: string | null
  result_data: Record<string, unknown>
  error_reason: string | null
}

export class PrivacyApiError extends Error {
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

function toTransportError(error: unknown): PrivacyApiError {
  if (error instanceof PrivacyApiError) {
    return error
  }
  if (error instanceof DOMException && error.name === "AbortError") {
    return new PrivacyApiError(
      "request_timeout",
      "La requete a expire. Reessayez dans un instant.",
      408,
      {},
    )
  }
  return new PrivacyApiError("network_error", "Erreur reseau. Reessayez plus tard.", 0, {})
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("access_token")
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function parseError(response: Response): Promise<never> {
  let payload: ErrorEnvelope | null = null
  try {
    payload = (await response.json()) as ErrorEnvelope
  } catch {
    payload = null
  }
  throw new PrivacyApiError(
    payload?.error?.code ?? "unknown_error",
    payload?.error?.message ?? `Request failed with status ${response.status}`,
    response.status,
    payload?.error?.details ?? {},
  )
}

export async function requestExport(): Promise<PrivacyRequestStatus> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/privacy/export`, {
      method: "POST",
      headers: getAuthHeaders(),
    })
    if (!response.ok) {
      return parseError(response)
    }
    const body = (await response.json()) as { data: PrivacyRequestStatus }
    return body.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function getExportStatus(): Promise<PrivacyRequestStatus | null> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/privacy/export`, {
      method: "GET",
      headers: getAuthHeaders(),
    })
    if (!response.ok) {
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      if (response.status === 404) {
        return null
      }
      throw new PrivacyApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }
    const body = (await response.json()) as { data: PrivacyRequestStatus }
    return body.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function requestDelete(): Promise<PrivacyRequestStatus> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/privacy/delete`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ confirmation: "DELETE" }),
    })
    if (!response.ok) {
      return parseError(response)
    }
    const body = (await response.json()) as { data: PrivacyRequestStatus }
    return body.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function getDeleteStatus(): Promise<PrivacyRequestStatus | null> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/privacy/delete`, {
      method: "GET",
      headers: getAuthHeaders(),
    })
    if (!response.ok) {
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      if (response.status === 404) {
        return null
      }
      throw new PrivacyApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }
    const body = (await response.json()) as { data: PrivacyRequestStatus }
    return body.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export function useRequestExport() {
  return useMutation({
    mutationFn: requestExport,
  })
}

export function useExportStatus(enabled = false) {
  return useQuery({
    queryKey: ["privacy-export-status"],
    queryFn: getExportStatus,
    enabled,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  })
}

export function useRequestDelete() {
  return useMutation({
    mutationFn: requestDelete,
  })
}

export function useDeleteStatus(enabled = false) {
  return useQuery({
    queryKey: ["privacy-delete-status"],
    queryFn: getDeleteStatus,
    enabled,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  })
}

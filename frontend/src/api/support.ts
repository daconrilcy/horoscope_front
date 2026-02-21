import { useMutation, useQuery } from "@tanstack/react-query"

import { API_BASE_URL } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, string>
  }
}

type ResponseEnvelope<TData> = {
  data: TData
}

export type SupportUserContext = {
  user: {
    user_id: number
    email: string
    role: string
    created_at: string
  }
  subscription: {
    status: "inactive" | "active"
    plan: {
      code: string
      display_name: string
      monthly_price_cents: number
      currency: string
      daily_message_limit: number
      is_active: boolean
    } | null
    failure_reason: string | null
    updated_at: string | null
  }
  privacy_requests: Array<{
    request_id: number
    request_kind: "export" | "delete"
    status: "requested" | "processing" | "completed" | "failed"
    requested_at: string
    completed_at: string | null
    error_reason: string | null
  }>
  incidents: SupportIncident[]
  audit_events: Array<{
    event_id: number
    action: string
    status: "success" | "failed"
    target_type: "user" | "incident" | string
    target_id: string | null
    created_at: string
  }>
}

export type SupportIncident = {
  incident_id: number
  user_id: number
  created_by_user_id: number | null
  assigned_to_user_id: number | null
  category: "account" | "subscription" | "content"
  title: string
  description: string
  status: "open" | "in_progress" | "resolved" | "closed"
  priority: "low" | "medium" | "high"
  resolved_at: string | null
  created_at: string
  updated_at: string
}

type SupportIncidentList = {
  incidents: SupportIncident[]
  total: number
  limit: number
  offset: number
}

export type CreateSupportIncidentPayload = {
  user_id: number
  category: "account" | "subscription" | "content"
  title: string
  description: string
  priority: "low" | "medium" | "high"
  assigned_to_user_id?: number
}

export type UpdateSupportIncidentPayload = {
  status?: "open" | "in_progress" | "resolved" | "closed"
  priority?: "low" | "medium" | "high"
  description?: string
  assigned_to_user_id?: number
}

export class SupportApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, string>

  constructor(code: string, message: string, status: number, details: Record<string, string> = {}) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
  }
}

async function parseError(response: Response): Promise<never> {
  let payload: ErrorEnvelope | null = null
  try {
    payload = (await response.json()) as ErrorEnvelope
  } catch {
    payload = null
  }
  throw new SupportApiError(
    payload?.error?.code ?? "unknown_error",
    payload?.error?.message ?? `Request failed with status ${response.status}`,
    response.status,
    payload?.error?.details ?? {},
  )
}

async function getSupportContext(userId: number): Promise<SupportUserContext> {
  const response = await fetch(`${API_BASE_URL}/v1/support/users/${userId}/context`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ResponseEnvelope<SupportUserContext>
  return body.data
}

type IncidentFilters = {
  user_id?: number
  status?: "open" | "in_progress" | "resolved" | "closed"
  priority?: "low" | "medium" | "high"
}

async function listSupportIncidents(filters: IncidentFilters): Promise<SupportIncidentList> {
  const params = new URLSearchParams()
  if (filters.user_id !== undefined) {
    params.set("user_id", String(filters.user_id))
  }
  if (filters.status !== undefined) {
    params.set("status", filters.status)
  }
  if (filters.priority !== undefined) {
    params.set("priority", filters.priority)
  }
  const suffix = params.toString() ? `?${params.toString()}` : ""
  const response = await fetch(`${API_BASE_URL}/v1/support/incidents${suffix}`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ResponseEnvelope<SupportIncidentList>
  return body.data
}

async function createSupportIncident(payload: CreateSupportIncidentPayload): Promise<SupportIncident> {
  const response = await fetch(`${API_BASE_URL}/v1/support/incidents`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAccessTokenAuthHeader(),
    },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ResponseEnvelope<SupportIncident>
  return body.data
}

async function updateSupportIncident(
  incidentId: number,
  payload: UpdateSupportIncidentPayload,
): Promise<SupportIncident> {
  const response = await fetch(`${API_BASE_URL}/v1/support/incidents/${incidentId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...getAccessTokenAuthHeader(),
    },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ResponseEnvelope<SupportIncident>
  return body.data
}

export function useSupportContext(userId: number, enabled = true) {
  return useQuery({
    queryKey: ["support-context", userId],
    queryFn: () => getSupportContext(userId),
    enabled: enabled && userId > 0,
  })
}

export function useSupportIncidents(filters: IncidentFilters, enabled = true) {
  return useQuery({
    queryKey: ["support-incidents", filters.user_id ?? null, filters.status ?? null, filters.priority ?? null],
    queryFn: () => listSupportIncidents(filters),
    enabled,
  })
}

export function useCreateSupportIncident() {
  return useMutation({
    mutationFn: createSupportIncident,
  })
}

export function useUpdateSupportIncident() {
  return useMutation({
    mutationFn: ({ incidentId, payload }: { incidentId: number; payload: UpdateSupportIncidentPayload }) =>
      updateSupportIncident(incidentId, payload),
  })
}

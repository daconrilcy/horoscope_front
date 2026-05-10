import { useMutation, useQuery } from "@tanstack/react-query"

import { apiFetch, parseApiErrorDetails, type ApiResponseEnvelope } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

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
  readonly requestId: string | null

  constructor(
    code: string,
    message: string,
    status: number,
    details: Record<string, string> = {},
    requestId: string | null = null,
  ) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
    this.requestId = requestId
  }
}

async function parseError(response: Response): Promise<never> {
  const error = await parseApiErrorDetails<Record<string, string>>(response, {})
  throw new SupportApiError(error.code, error.message, response.status, error.details, error.requestId)
}

async function getSupportContext(userId: number): Promise<SupportUserContext> {
  const response = await apiFetch(`/v1/support/users/${userId}/context`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ApiResponseEnvelope<SupportUserContext>
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
  const response = await apiFetch(`/v1/support/incidents${suffix}`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ApiResponseEnvelope<SupportIncidentList>
  return body.data
}

async function createSupportIncident(payload: CreateSupportIncidentPayload): Promise<SupportIncident> {
  const response = await apiFetch("/v1/support/incidents", {
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
  const body = (await response.json()) as ApiResponseEnvelope<SupportIncident>
  return body.data
}

async function updateSupportIncident(
  incidentId: number,
  payload: UpdateSupportIncidentPayload,
): Promise<SupportIncident> {
  const response = await apiFetch(`/v1/support/incidents/${incidentId}`, {
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
  const body = (await response.json()) as ApiResponseEnvelope<SupportIncident>
  return body.data
}

export function useOpsSearchUser(email: string) {
  return useQuery({
    queryKey: ["support-search-user", email],
    queryFn: async () => {
      const response = await apiFetch(`/v1/support/users/context?email=${encodeURIComponent(email)}`, {
        method: "GET",
        headers: getAccessTokenAuthHeader(),
      })
      if (!response.ok) {
        return parseError(response)
      }
      const body = (await response.json()) as ApiResponseEnvelope<SupportUserContext>
      return body.data
    },
    enabled: email.length > 0,
  })
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

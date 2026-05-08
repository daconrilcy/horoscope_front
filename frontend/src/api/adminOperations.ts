// Centralise les appels API admin restants pour garder les pages hors du client HTTP bas niveau.
import { useMutation, useQuery } from "@tanstack/react-query"

import { getAccessTokenAuthHeader } from "../utils/authToken"
import { apiFetch } from "./client"

type AdminEnvelope<T> = {
  data: T
}

export type AdminAiUseCaseMetrics = {
  use_case: string
  display_name: string
  call_count: number
  total_tokens: number
  estimated_cost_usd: number
  avg_latency_ms: number
  error_rate: number
  retry_rate: number
}

export type AdminAiTrendPoint = {
  date: string
  call_count: number
  error_count: number
}

export type AdminAiFailedCall = {
  id: string
  timestamp: string
  error_code: string
  request_id_masked: string | null
}

export type AdminAiUseCaseDetail = {
  use_case: string
  metrics: AdminAiUseCaseMetrics
  trend_data: AdminAiTrendPoint[]
  recent_failed_calls: AdminAiFailedCall[]
}

export type EntitlementPlan = {
  id: number
  code: string
  name: string
  audience: string
}

export type EntitlementFeature = {
  id: number
  code: string
  name: string
  is_metered: boolean
}

export type EntitlementCell = {
  access_mode: string
  is_enabled: boolean
  variant_code: string | null
  quota_limit: number | null
  period: string | null
  is_incoherent: boolean
}

export type EntitlementsMatrixResponse = {
  plans: EntitlementPlan[]
  features: EntitlementFeature[]
  cells: Record<string, EntitlementCell>
}

export type EntitlementUpdatePayload = Partial<{
  access_mode: string
  quota_limit: number
  is_enabled: boolean
}>

export type AdminExportType = "users" | "generations" | "billing"

export type AdminExportPayload = {
  period: {
    start: string | null
    end: string | null
  } | null
  format?: string
}

export type SupportTicket = {
  id: number
  user_id: number
  user_email: string
  category: string
  title: string
  status: string
  priority: string
  created_at: string
}

export type FlaggedContent = {
  id: number
  user_id: number
  user_email: string
  content_type: string
  content_ref_id: string
  excerpt: string
  reason: string | null
  reported_at: string
  status: string
}

async function readJson<T>(response: Response, fallbackMessage: string): Promise<T> {
  if (!response.ok) {
    throw new Error(fallbackMessage)
  }
  return response.json() as Promise<T>
}

async function fetchAdminJson<T>(path: string, init: RequestInit = {}, fallbackMessage = "Admin request failed"): Promise<T> {
  const response = await apiFetch(path, {
    ...init,
    headers: {
      ...getAccessTokenAuthHeader(),
      ...init.headers,
    },
  })
  return readJson<T>(response, fallbackMessage)
}

export const adminOperationsQueryKeys = {
  aiMetrics: (period: string) => ["admin-ai-metrics", period] as const,
  aiUseCaseDetail: (useCase: string | null, period: string) => ["admin-ai-use-case-detail", useCase, period] as const,
  entitlementsMatrix: ["admin-entitlements-matrix"] as const,
  supportTickets: (status: string) => ["admin-support-tickets", status] as const,
  flaggedContent: ["admin-flagged-content"] as const,
}

export function useAdminAiMetrics(period: string, enabled: boolean) {
  return useQuery<AdminEnvelope<AdminAiUseCaseMetrics[]>>({
    queryKey: adminOperationsQueryKeys.aiMetrics(period),
    queryFn: () =>
      fetchAdminJson(`/v1/admin/ai/metrics?period=${encodeURIComponent(period)}`, {}, "Failed to fetch AI metrics"),
    enabled,
  })
}

export function useAdminAiUseCaseDetail(useCase: string | null, period: string, enabled: boolean) {
  return useQuery<AdminAiUseCaseDetail>({
    queryKey: adminOperationsQueryKeys.aiUseCaseDetail(useCase, period),
    queryFn: () =>
      fetchAdminJson(
        `/v1/admin/ai/metrics/${encodeURIComponent(useCase ?? "")}?period=${encodeURIComponent(period)}`,
        {},
        "Failed to fetch detail",
      ),
    enabled: enabled && Boolean(useCase),
  })
}

export function useAdminEntitlementsMatrix(enabled: boolean) {
  return useQuery<EntitlementsMatrixResponse>({
    queryKey: adminOperationsQueryKeys.entitlementsMatrix,
    queryFn: () => fetchAdminJson("/v1/admin/entitlements/matrix", {}, "Failed to fetch matrix"),
    enabled,
  })
}

export function updateAdminEntitlement(
  planId: number,
  featureId: number,
  payload: EntitlementUpdatePayload,
): Promise<unknown> {
  return fetchAdminJson(`/v1/admin/entitlements/${planId}/${featureId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  }, "Update failed")
}

export function exportAdminData(type: AdminExportType, payload: AdminExportPayload): Promise<Response> {
  return apiFetch(`/v1/admin/exports/${type}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAccessTokenAuthHeader(),
    },
    body: JSON.stringify(payload),
  })
}

export function useAdminSupportTickets(statusFilter: string, enabled: boolean) {
  return useQuery<AdminEnvelope<SupportTicket[]>>({
    queryKey: adminOperationsQueryKeys.supportTickets(statusFilter),
    queryFn: () =>
      fetchAdminJson(
        `/v1/admin/support/tickets?status=${encodeURIComponent(statusFilter)}`,
        {},
        "Failed to fetch support tickets",
      ),
    enabled,
  })
}

export function useAdminFlaggedContent(enabled: boolean) {
  return useQuery<AdminEnvelope<FlaggedContent[]>>({
    queryKey: adminOperationsQueryKeys.flaggedContent,
    queryFn: () =>
      fetchAdminJson(
        "/v1/admin/support/flagged-content?status=pending",
        {},
        "Failed to fetch flagged content",
      ),
    enabled,
  })
}

export function useReviewFlaggedContent() {
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      fetchAdminJson(`/v1/admin/support/flagged-content/${id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status }),
      }),
  })
}

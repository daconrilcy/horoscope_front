// Centralise les contrats et hooks des journaux admin pour eviter les appels API directs en page.
import { useMutation, useQuery } from "@tanstack/react-query"

import { apiFetch } from "./client"

export type AdminQuotaAlert = {
  user_id: number
  user_email_masked: string
  plan_code: string
  feature_code: string
  used: number
  limit: number
  consumption_rate: number
}

export type AdminAuditLog = {
  id: number
  timestamp: string
  actor_email_masked: string | null
  actor_role: string
  action: string
  target_type: string | null
  target_id_masked: string | null
  status: string
  details: Record<string, unknown>
}

export type AdminAuditLogsResponse = {
  data: AdminAuditLog[]
  total: number
  page: number
  per_page: number
}

export type AdminStripeEvent = {
  id: number
  stripe_event_id: string
  event_type: string
  status: string
  received_at: string
  last_error: string | null
}

function adminAuthHeaders(token: string | null, contentType?: string): HeadersInit {
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(contentType ? { "Content-Type": contentType } : {}),
  }
}

export function buildAdminAuditLogsPath(actorFilter: string, actionFilter: string, periodFilter: string) {
  const params = new URLSearchParams()
  if (actorFilter.trim()) {
    params.set("actor", actorFilter.trim())
  }
  if (actionFilter !== "all") {
    params.set("action", actionFilter)
  }
  if (periodFilter !== "all") {
    params.set("period", periodFilter)
  }
  const query = params.toString()
  return query ? `/v1/admin/audit?${query}` : "/v1/admin/audit"
}

async function readAdminJson<T>(response: Response, fallbackMessage: string): Promise<T> {
  if (!response.ok) {
    throw new Error(await extractAdminApiErrorMessage(response, fallbackMessage))
  }
  return response.json() as Promise<T>
}

export async function extractAdminApiErrorMessage(response: Response, fallback: string) {
  try {
    const payload = (await response.clone().json()) as { error?: { message?: string } }
    return payload?.error?.message ?? fallback
  } catch {
    return fallback
  }
}

export const adminLogsQueryKeys = {
  quotaAlerts: ["admin-logs", "quota-alerts"] as const,
  audit: (actor: string, action: string, period: string) => ["admin-logs", "audit", actor, action, period] as const,
  stripe: ["admin-logs", "stripe"] as const,
}

export function useAdminQuotaAlertsQuery(token: string | null) {
  return useQuery<{ data: AdminQuotaAlert[] }>({
    queryKey: adminLogsQueryKeys.quotaAlerts,
    queryFn: async () =>
      readAdminJson(
        await apiFetch("/v1/admin/logs/quota-alerts", {
          headers: adminAuthHeaders(token),
        }),
        "Chargement des alertes quota impossible.",
      ),
    enabled: Boolean(token),
  })
}

export function useAdminAuditLogsQuery(
  token: string | null,
  actorFilter: string,
  actionFilter: string,
  periodFilter: string,
  enabled: boolean,
) {
  return useQuery<AdminAuditLogsResponse>({
    queryKey: adminLogsQueryKeys.audit(actorFilter, actionFilter, periodFilter),
    queryFn: async () =>
      readAdminJson(
        await apiFetch(buildAdminAuditLogsPath(actorFilter, actionFilter, periodFilter), {
          headers: adminAuthHeaders(token),
        }),
        "Chargement des audits impossible.",
      ),
    enabled: Boolean(token) && enabled,
  })
}

export function useAdminStripeLogsQuery(token: string | null, enabled: boolean) {
  return useQuery<{ data: AdminStripeEvent[] }>({
    queryKey: adminLogsQueryKeys.stripe,
    queryFn: async () =>
      readAdminJson(
        await apiFetch("/v1/admin/logs/stripe", {
          headers: adminAuthHeaders(token),
        }),
        "Chargement des logs Stripe impossible.",
      ),
    enabled: Boolean(token) && enabled,
  })
}

export function useExportAdminAuditMutation(token: string | null) {
  return useMutation({
    mutationFn: async ({
      actor,
      action,
      period,
    }: {
      actor: string | null
      action: string | null
      period: string
    }) => {
      const response = await apiFetch("/v1/admin/audit/export", {
        method: "POST",
        headers: adminAuthHeaders(token, "application/json"),
        body: JSON.stringify({ actor, action, period }),
      })
      if (!response.ok) {
        throw new Error(await extractAdminApiErrorMessage(response, "Export CSV impossible."))
      }
      return response
    },
  })
}

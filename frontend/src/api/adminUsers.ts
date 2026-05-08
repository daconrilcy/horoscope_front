// Centralise les contrats et hooks des utilisateurs admin pour garder les pages hors du transport HTTP.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiFetch } from "./client"

export type AdminUserSearchItem = {
  id: number
  email: string
  role: string
  plan_code: string | null
  subscription_status: string | null
  created_at: string
}

export type AdminUserDetail = {
  id: number
  email: string
  role: string
  created_at: string
  is_active: boolean
  is_suspended: boolean
  is_locked: boolean
  plan_code: string | null
  subscription_status: string | null
  stripe_customer_id_masked: string | null
  payment_method_summary: string | null
  last_invoice_amount_cents: number | null
  last_invoice_date: string | null
  activity_summary: {
    total_tokens: number
    tokens_in: number
    tokens_out: number
    messages_count: number
    natal_charts_total: number
    natal_charts_short: number
    natal_charts_complete: number
  }
  quotas: Array<{
    feature_code: string
    used: number
    limit: number | null
    period: string
  }>
  recent_tickets: Array<{
    id: number
    title: string
    status: string
    created_at: string
  }>
  recent_audit_events: Array<{
    id: number
    action: string
    actor_role: string
    created_at: string
  }>
}

export type AdminUserActionBody = Record<string, string | number>

type AdminApiEnvelope<T> = {
  data: T
}

function adminAuthHeaders(token: string | null, contentType?: string): HeadersInit {
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(contentType ? { "Content-Type": contentType } : {}),
  }
}

async function readAdminJson<T>(response: Response, fallbackMessage: string): Promise<T> {
  if (!response.ok) {
    throw new Error(fallbackMessage)
  }
  return response.json() as Promise<T>
}

export const adminUsersQueryKeys = {
  search: (query: string) => ["admin-users", "search", query] as const,
  detail: (userId: string | undefined) => ["admin-users", "detail", userId] as const,
}

export function useAdminUsersSearchQuery(token: string | null, query: string) {
  return useQuery<{ data: AdminUserSearchItem[]; total: number }>({
    queryKey: adminUsersQueryKeys.search(query),
    queryFn: async () =>
      readAdminJson(
        await apiFetch(`/v1/admin/users?q=${encodeURIComponent(query)}`, {
          headers: adminAuthHeaders(token),
        }),
        "Search failed",
      ),
    enabled: Boolean(token),
  })
}

export function useAdminUserDetailQuery(token: string | null, userId: string | undefined) {
  return useQuery<AdminApiEnvelope<AdminUserDetail>>({
    queryKey: adminUsersQueryKeys.detail(userId),
    queryFn: async () =>
      readAdminJson(
        await apiFetch(`/v1/admin/users/${userId}`, {
          headers: adminAuthHeaders(token),
        }),
        "Failed to fetch user detail",
      ),
    enabled: Boolean(token && userId),
  })
}

export function useAdminUserActionMutation(token: string | null, userId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ action, body }: { action: string; body?: AdminUserActionBody }) =>
      readAdminJson(
        await apiFetch(`/v1/admin/users/${userId}/${action}`, {
          method: "POST",
          headers: adminAuthHeaders(token, "application/json"),
          body: body ? JSON.stringify(body) : undefined,
        }),
        `${action} failed`,
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminUsersQueryKeys.detail(userId) })
    },
  })
}

export function useRevealAdminUserStripeIdMutation(token: string | null, userId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation<{ stripe_customer_id: string }>({
    mutationFn: async () =>
      readAdminJson(
        await apiFetch(`/v1/admin/users/${userId}/reveal-stripe-id`, {
          method: "POST",
          headers: adminAuthHeaders(token),
        }),
        "Reveal failed",
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminUsersQueryKeys.detail(userId) })
    },
  })
}

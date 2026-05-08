// Centralise les contrats et hooks du tableau de bord admin pour eviter les appels API dans les pages.
import { useQuery } from "@tanstack/react-query"

import { apiFetch } from "./client"

export type AdminDashboardKpisSnapshot = {
  total_users: number
  active_users_7j: number
  active_users_30j: number
  subscriptions_by_plan: Record<string, number>
  mrr_cents: number
  arr_cents: number
  trials_count: number
  last_updated: string
}

export type AdminDashboardTrendPoint = {
  date: string
  new_users: number
}

export type AdminDashboardKpisFlux = {
  period: string
  plan: string
  new_users: number
  churn_count: number
  upgrades_count: number
  downgrades_count: number
  payment_failures_count: number
  revenue_cents: number
  trend_data: AdminDashboardTrendPoint[]
  last_updated: string
}

export type AdminDashboardKpisBilling = {
  period: string
  plan: string
  payment_failures: number
  estimated_total_revenue_cents: number
  revenue_by_plan: Array<{
    plan_code: string
    count: number
    mrr_cents: number
    estimated_period_revenue_cents: number
  }>
  last_updated: string
}

type AdminApiEnvelope<T> = {
  data: T
}

function adminAuthHeaders(token: string | null): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function readAdminJson<T>(response: Response, fallbackMessage: string): Promise<T> {
  if (!response.ok) {
    throw new Error(fallbackMessage)
  }
  return response.json() as Promise<T>
}

export const adminDashboardQueryKeys = {
  snapshot: ["admin-dashboard", "kpis-snapshot"] as const,
  flux: (period: string, plan: string) => ["admin-dashboard", "kpis-flux", period, plan] as const,
  billing: (period: string, plan: string) => ["admin-dashboard", "kpis-billing", period, plan] as const,
}

export function useAdminDashboardSnapshotQuery(token: string | null) {
  return useQuery<AdminApiEnvelope<AdminDashboardKpisSnapshot>>({
    queryKey: adminDashboardQueryKeys.snapshot,
    queryFn: async () =>
      readAdminJson(
        await apiFetch("/v1/admin/dashboard/kpis-snapshot", {
          headers: adminAuthHeaders(token),
        }),
        "Failed to fetch snapshot KPIs",
      ),
    enabled: Boolean(token),
  })
}

export function useAdminDashboardFluxQuery(token: string | null, period: string, plan: string) {
  return useQuery<AdminApiEnvelope<AdminDashboardKpisFlux>>({
    queryKey: adminDashboardQueryKeys.flux(period, plan),
    queryFn: async () =>
      readAdminJson(
        await apiFetch(`/v1/admin/dashboard/kpis-flux?period=${period}&plan=${plan}`, {
          headers: adminAuthHeaders(token),
        }),
        "Failed to fetch flux KPIs",
      ),
    enabled: Boolean(token),
  })
}

export function useAdminDashboardBillingQuery(token: string | null, period: string, plan: string) {
  return useQuery<AdminApiEnvelope<AdminDashboardKpisBilling>>({
    queryKey: adminDashboardQueryKeys.billing(period, plan),
    queryFn: async () =>
      readAdminJson(
        await apiFetch(`/v1/admin/dashboard/kpis-billing?period=${period}&plan=${plan}`, {
          headers: adminAuthHeaders(token),
        }),
        "Failed to fetch billing KPIs",
      ),
    enabled: Boolean(token),
  })
}

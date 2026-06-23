import { useQuery } from "@tanstack/react-query"

import { apiFetch, parseApiErrorDetails } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

export type MonitoringWindow = "1h" | "24h" | "7d"

export type OpsMonitoringAlert = {
  code: string
  severity: string
  status: string
  message: string
  context: Record<string, number | string>
}

export type OpsMonitoringOperationalSummary = {
  window: MonitoringWindow
  aggregation_scope: "instance_local"
  requests_total: number
  errors_4xx_total: number
  errors_5xx_total: number
  error_5xx_rate: number
  availability_percent: number
  p95_latency_ms: number
  quota_exceeded_total: number
  privacy_failures_total: number
  b2b_auth_failures_total: number
  alerts: OpsMonitoringAlert[]
}

export class OpsMonitoringApiError extends Error {
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

async function getOperationalSummary(window: MonitoringWindow): Promise<OpsMonitoringOperationalSummary> {
  const params = new URLSearchParams({ window })
  const response = await apiFetch(`/v1/ops/monitoring/operational-summary?${params.toString()}`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    const error = await parseApiErrorDetails<Record<string, string>>(response, {})
    throw new OpsMonitoringApiError(error.code, error.message, response.status, error.details, error.requestId)
  }
  const payload = (await response.json()) as { data: OpsMonitoringOperationalSummary }
  return payload.data
}

export function useOpsMonitoring(windowMinutes: number, enabled = true) {
  const window: MonitoringWindow = windowMinutes >= 1440 ? "24h" : windowMinutes >= 60 ? "1h" : "1h" // Simplified mapping
  return useQuery({
    queryKey: ["ops-monitoring-kpis", window],
    queryFn: () => getOperationalSummary(window),
    enabled,
  })
}

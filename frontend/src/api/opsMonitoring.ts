import { useQuery } from "@tanstack/react-query"

import { apiFetch, parseApiErrorDetails } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

export type MonitoringWindow = "1h" | "24h" | "7d"

export type OpsMonitoringKpis = {
  window: MonitoringWindow
  aggregation_scope: "instance_local"
  messages_total: number
  out_of_scope_count: number
  out_of_scope_rate: number
  llm_error_count: number
  llm_error_rate: number
  p95_latency_ms: number
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

async function getConversationKpis(window: MonitoringWindow): Promise<OpsMonitoringKpis> {
  const params = new URLSearchParams({ window })
  const response = await apiFetch(`/v1/ops/monitoring/conversation-kpis?${params.toString()}`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    const error = await parseApiErrorDetails<Record<string, string>>(response, {})
    throw new OpsMonitoringApiError(error.code, error.message, response.status, error.details, error.requestId)
  }
  const payload = (await response.json()) as { data: OpsMonitoringKpis }
  return payload.data
}

export function useOpsMonitoring(windowMinutes: number, enabled = true) {
  const window: MonitoringWindow = windowMinutes >= 1440 ? "24h" : windowMinutes >= 60 ? "1h" : "1h" // Simplified mapping
  return useQuery({
    queryKey: ["ops-monitoring-kpis", window],
    queryFn: () => getConversationKpis(window),
    enabled,
  })
}

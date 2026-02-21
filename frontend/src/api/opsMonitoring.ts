import { useQuery } from "@tanstack/react-query"

import { API_BASE_URL } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, string>
  }
}

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

  constructor(code: string, message: string, status: number, details: Record<string, string> = {}) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
  }
}

async function getConversationKpis(window: MonitoringWindow): Promise<OpsMonitoringKpis> {
  const params = new URLSearchParams({ window })
  const response = await fetch(`${API_BASE_URL}/v1/ops/monitoring/conversation-kpis?${params.toString()}`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    let payload: ErrorEnvelope | null = null
    try {
      payload = (await response.json()) as ErrorEnvelope
    } catch {
      payload = null
    }
    throw new OpsMonitoringApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `Request failed with status ${response.status}`,
      response.status,
      payload?.error?.details ?? {},
    )
  }
  const payload = (await response.json()) as { data: OpsMonitoringKpis }
  return payload.data
}

export function useConversationKpis(window: MonitoringWindow, enabled = true) {
  return useQuery({
    queryKey: ["ops-monitoring-kpis", window],
    queryFn: () => getConversationKpis(window),
    enabled,
  })
}

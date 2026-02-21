import { useMutation } from "@tanstack/react-query"

import { API_BASE_URL } from "./client"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, string>
    request_id?: string
  }
}

export type B2BUsageSummaryData = {
  account_id: number
  credential_id: number
  usage_date: string
  month_start: string
  month_end: string
  daily_limit: number
  daily_consumed: number
  daily_remaining: number
  monthly_limit: number
  monthly_consumed: number
  monthly_remaining: number
  limit_mode: "block" | "overage"
  blocked: boolean
  overage_applied: boolean
}

export class B2BUsageApiError extends Error {
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

async function getB2BUsageSummary(apiKey: string): Promise<B2BUsageSummaryData> {
  const response = await fetch(`${API_BASE_URL}/v1/b2b/usage/summary`, {
    method: "GET",
    headers: { "X-API-Key": apiKey },
  })

  if (!response.ok) {
    let payload: ErrorEnvelope | null = null
    try {
      payload = (await response.json()) as ErrorEnvelope
    } catch {
      payload = null
    }
    throw new B2BUsageApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `Request failed with status ${response.status}`,
      response.status,
      payload?.error?.details ?? {},
      payload?.error?.request_id ?? null,
    )
  }

  const payload = (await response.json()) as { data: B2BUsageSummaryData }
  return payload.data
}

export function useB2BUsageSummary() {
  return useMutation({
    mutationFn: getB2BUsageSummary,
  })
}

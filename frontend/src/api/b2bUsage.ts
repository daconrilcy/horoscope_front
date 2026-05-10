import { useMutation } from "@tanstack/react-query"

import { apiFetch, parseApiErrorDetails } from "./client"

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
  const response = await apiFetch("/v1/b2b/usage/summary", {
    method: "GET",
    headers: { "X-API-Key": apiKey },
  })

  if (!response.ok) {
    const error = await parseApiErrorDetails<Record<string, string>>(response, {})
    throw new B2BUsageApiError(
      error.code,
      error.message,
      response.status,
      error.details,
      error.requestId,
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

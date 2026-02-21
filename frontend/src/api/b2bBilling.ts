import { useMutation } from "@tanstack/react-query"

import { API_BASE_URL } from "./client"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
    request_id?: string
  }
}

export type B2BBillingCycle = {
  cycle_id: number
  account_id: number
  plan_id: number
  plan_code: string
  plan_display_name: string
  period_start: string
  period_end: string
  status: string
  currency: string
  fixed_amount_cents: number
  included_units: number
  consumed_units: number
  billable_units: number
  unit_price_cents: number
  variable_amount_cents: number
  total_amount_cents: number
  limit_mode: "block" | "overage"
  overage_applied: boolean
  calculation_snapshot: Record<string, unknown>
  closed_by_user_id: number | null
  created_at: string
  updated_at: string
}

export type B2BBillingCycleList = {
  items: B2BBillingCycle[]
  total: number
  limit: number
  offset: number
}

export class B2BBillingApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, unknown>
  readonly requestId: string | null

  constructor(
    code: string,
    message: string,
    status: number,
    details: Record<string, unknown> = {},
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
  let payload: ErrorEnvelope | null = null
  try {
    payload = (await response.json()) as ErrorEnvelope
  } catch {
    payload = null
  }
  throw new B2BBillingApiError(
    payload?.error?.code ?? "unknown_error",
    payload?.error?.message ?? `Request failed with status ${response.status}`,
    response.status,
    payload?.error?.details ?? {},
    payload?.error?.request_id ?? null,
  )
}

async function getLatestB2BBillingCycle(apiKey: string): Promise<B2BBillingCycle | null> {
  const response = await fetch(`${API_BASE_URL}/v1/b2b/billing/cycles/latest`, {
    method: "GET",
    headers: { "X-API-Key": apiKey },
  })
  if (!response.ok) {
    return parseError(response)
  }
  const payload = (await response.json()) as { data: B2BBillingCycle | null }
  return payload.data
}

async function listB2BBillingCycles(input: {
  apiKey: string
  limit?: number
  offset?: number
}): Promise<B2BBillingCycleList> {
  const limit = input.limit ?? 20
  const offset = input.offset ?? 0
  const response = await fetch(
    `${API_BASE_URL}/v1/b2b/billing/cycles?limit=${encodeURIComponent(limit)}&offset=${encodeURIComponent(offset)}`,
    {
      method: "GET",
      headers: { "X-API-Key": input.apiKey },
    },
  )
  if (!response.ok) {
    return parseError(response)
  }
  const payload = (await response.json()) as { data: B2BBillingCycleList }
  return payload.data
}

export function useB2BBillingLatestCycle() {
  return useMutation({
    mutationFn: getLatestB2BBillingCycle,
  })
}

export function useB2BBillingCycles() {
  return useMutation({
    mutationFn: listB2BBillingCycles,
  })
}

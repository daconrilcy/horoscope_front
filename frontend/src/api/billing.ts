import { useMutation, useQuery } from "@tanstack/react-query"

import { API_BASE_URL } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, string>
  }
}

export type BillingPlan = {
  code: string
  display_name: string
  monthly_price_cents: number
  currency: string
  daily_message_limit: number
  is_active: boolean
}

export type BillingSubscriptionStatus = {
  status: "inactive" | "active"
  plan: BillingPlan | null
  failure_reason: string | null
  updated_at: string | null
}

export type BillingCheckoutPayload = {
  plan_code?: string
  payment_method_token?: string
  idempotency_key?: string
}

export type BillingCheckoutData = {
  subscription: BillingSubscriptionStatus
  payment_status: "pending" | "succeeded" | "failed"
  payment_attempt_id: number
  idempotency_key: string
}

export type BillingPlanChangePayload = {
  target_plan_code: string
  idempotency_key?: string
}

export type BillingPlanChangeData = {
  subscription: BillingSubscriptionStatus
  previous_plan_code: string
  target_plan_code: string
  plan_change_status: "pending" | "succeeded" | "failed"
  plan_change_id: number
  idempotency_key: string
}

export type BillingQuotaStatus = {
  quota_date: string
  limit: number
  consumed: number
  remaining: number
  reset_at: string
  blocked: boolean
}

export class BillingApiError extends Error {
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

async function parseError(response: Response): Promise<never> {
  let payload: ErrorEnvelope | null = null
  try {
    payload = (await response.json()) as ErrorEnvelope
  } catch {
    payload = null
  }
  throw new BillingApiError(
    payload?.error?.code ?? "unknown_error",
    payload?.error?.message ?? `Request failed with status ${response.status}`,
    response.status,
    payload?.error?.details ?? {},
  )
}

async function fetchSubscriptionStatus(): Promise<BillingSubscriptionStatus> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/subscription`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: BillingSubscriptionStatus }
  return body.data
}

async function postCheckout(payload: BillingCheckoutPayload): Promise<BillingCheckoutData> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/checkout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAccessTokenAuthHeader(),
    },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: BillingCheckoutData }
  return body.data
}

async function postRetry(payload: BillingCheckoutPayload): Promise<BillingCheckoutData> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/retry`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAccessTokenAuthHeader(),
    },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: BillingCheckoutData }
  return body.data
}

async function fetchQuotaStatus(): Promise<BillingQuotaStatus> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/quota`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: BillingQuotaStatus }
  return body.data
}

async function postPlanChange(payload: BillingPlanChangePayload): Promise<BillingPlanChangeData> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/plan-change`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAccessTokenAuthHeader(),
    },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: BillingPlanChangeData }
  return body.data
}

export function useBillingSubscription() {
  return useQuery({
    queryKey: ["billing-subscription"],
    queryFn: fetchSubscriptionStatus,
  })
}

export function useCheckoutEntryPlan() {
  return useMutation({
    mutationFn: postCheckout,
  })
}

export function useRetryCheckout() {
  return useMutation({
    mutationFn: postRetry,
  })
}

export function useBillingQuota() {
  return useQuery({
    queryKey: ["billing-quota"],
    queryFn: fetchQuotaStatus,
  })
}

export function useChangePlan() {
  return useMutation({
    mutationFn: postPlanChange,
  })
}

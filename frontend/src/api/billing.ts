import { useMutation, useQuery } from "@tanstack/react-query"
import { getAccessTokenAuthHeader } from "./auth"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export type BillingPlan = {
  code: string
  name: string
  monthly_price_cents: number
}

export type BillingSubscription = {
  status: "active" | "canceled" | "past_due" | "incomplete"
  plan: BillingPlan | null
  current_period_end: string | null
}

export type BillingSubscriptionStatus = {
  is_active: boolean
  subscription: BillingSubscription
  can_checkout: boolean
  can_change_plan: boolean
  available_plans: BillingPlan[]
}

export type BillingCheckoutPayload = {
  plan_code: string
  payment_method_token: string
  idempotency_key: string
}

export type BillingCheckoutData = {
  checkout_id: number
  status: "pending" | "succeeded" | "failed"
  payment_status: "pending" | "succeeded" | "failed"
  client_secret: string | null
  subscription: BillingSubscription
}

export type BillingPlanChangePayload = {
  target_plan_code: string
  idempotency_key: string
}

export type BillingPlanChangeData = {
  previous_plan_code: string
  target_plan_code: string
  plan_change_status: "pending" | "succeeded" | "failed"
  plan_change_id: number
  idempotency_key: string
}

export type ChatEntitlementUsageStatus = {
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

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details: Record<string, string>
    request_id: string
  }
}

type EntitlementUsageState = {
  quota_key: string
  quota_limit: number
  used: number
  remaining: number
  exhausted: boolean
  period_unit: string
  period_value: number
  reset_mode: string
  window_start: string | null
  window_end: string | null
}

type FeatureEntitlementResponse = {
  feature_code: string
  final_access: boolean
  reason: string
  usage_states: EntitlementUsageState[]
}

type EntitlementsMeResponse = {
  data: {
    features: FeatureEntitlementResponse[]
  }
}

const CHAT_QUOTA_FEATURE_CODE = "astrologer_chat"

function toChatEntitlementUsage(feature: FeatureEntitlementResponse | undefined): ChatEntitlementUsageStatus | null {
  const usage = feature?.usage_states[0]
  if (!usage) {
    return null
  }

  return {
    quota_date: usage.window_start ?? "",
    limit: usage.quota_limit,
    consumed: usage.used,
    remaining: usage.remaining,
    reset_at: usage.window_end ?? "",
    blocked: usage.exhausted || feature?.final_access === false,
  }
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

async function fetchChatEntitlementUsage(): Promise<ChatEntitlementUsageStatus | null> {
  const response = await fetch(`${API_BASE_URL}/v1/entitlements/me`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as EntitlementsMeResponse
  const chatEntitlement = body.data.features.find(
    (feature) => feature.feature_code === CHAT_QUOTA_FEATURE_CODE,
  )
  return toChatEntitlementUsage(chatEntitlement)
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

export function useRetryPayment() {
  return useMutation({
    mutationFn: postRetry,
  })
}

export function useChatEntitlementUsage() {
  return useQuery({
    queryKey: ["chat-entitlement-usage"],
    queryFn: fetchChatEntitlementUsage,
    retry: (failureCount, error) => {
      if (error instanceof BillingApiError && error.status === 403) return false
      return failureCount < 1
    },
  })
}

export function useChangePlan() {
  return useMutation({
    mutationFn: postPlanChange,
  })
}

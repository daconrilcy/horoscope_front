import { useMutation, useQuery } from "@tanstack/react-query"

import { API_BASE_URL } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

export type BillingPlan = {
  code: string
  display_name: string
  monthly_price_cents: number
  currency: string
  daily_message_limit: number
  is_active: boolean
}

export type CurrentQuota = {
  feature_code: string
  quota_limit: number
  consumed: number
  remaining: number
  period_unit: string
  period_value: number
  reset_mode: string
  window_start: string | null
  window_end: string | null
}

export type BillingSubscriptionStatus = {
  status: "inactive" | "active"
  subscription_status: string | null
  plan: BillingPlan | null
  scheduled_plan: BillingPlan | null
  change_effective_at: string | null
  cancel_at_period_end: boolean
  current_period_end: string | null
  failure_reason: string | null
  current_quota: CurrentQuota | null
  updated_at: string | null
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

async function fetchBillingPlans(): Promise<BillingPlan[]> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/plans`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: BillingPlan[] }
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

export function useBillingSubscription() {
  return useQuery({
    queryKey: ["billing-subscription"],
    queryFn: fetchSubscriptionStatus,
  })
}

export function useBillingPlans() {
  return useQuery({
    queryKey: ["billing-plans"],
    queryFn: fetchBillingPlans,
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

// --- Stripe-first endpoints ---

export type StripeCheckoutSessionData = { checkout_url: string }
export type StripePortalSessionData = { url: string }

async function postStripeCheckoutSession(plan: "basic" | "premium"): Promise<StripeCheckoutSessionData> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/stripe-checkout-session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAccessTokenAuthHeader(),
    },
    body: JSON.stringify({ plan }),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: StripeCheckoutSessionData }
  return body.data
}

async function postStripePortalSession(): Promise<StripePortalSessionData> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/stripe-customer-portal-session`, {
    method: "POST",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: StripePortalSessionData }
  return body.data
}

async function postStripePortalSubscriptionUpdateSession(): Promise<StripePortalSessionData> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/stripe-customer-portal-subscription-update-session`, {
    method: "POST",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: StripePortalSessionData }
  return body.data
}

async function postStripePortalSubscriptionCancelSession(): Promise<StripePortalSessionData> {
  const response = await fetch(
    `${API_BASE_URL}/v1/billing/stripe-customer-portal-subscription-cancel-session`,
    {
      method: "POST",
      headers: getAccessTokenAuthHeader(),
    },
  )
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: StripePortalSessionData }
  return body.data
}

export function useStripeCheckoutSession() {
  return useMutation({
    mutationFn: postStripeCheckoutSession,
  })
}

export function useStripePortalSession() {
  return useMutation({
    mutationFn: postStripePortalSession,
  })
}

export function useStripePortalSubscriptionUpdateSession() {
  return useMutation({
    mutationFn: postStripePortalSubscriptionUpdateSession,
  })
}

export function useStripePortalSubscriptionCancelSession() {
  return useMutation({
    mutationFn: postStripePortalSubscriptionCancelSession,
  })
}

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

export type PlanFeatureQuota = {
  quota_key: string
  quota_limit: number
  period_unit: string
  period_value: number
  reset_mode: string
}

export type PlanFeature = {
  feature_code: string
  feature_name: string
  is_enabled: boolean
  access_mode: string
  quotas: PlanFeatureQuota[]
}

export type PlanCatalog = {
  plan_code: string
  plan_name: string
  monthly_price_cents: number
  currency: string
  is_active: boolean
  features: PlanFeature[]
}

export type ChatEntitlementUsageStatus = {
  quota_date: string
  quota_key: string
  limit: number
  consumed: number
  remaining: number
  reset_at: string
  blocked: boolean
}

export type ChatEntitlementUsageState = {
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

export type ChatEntitlementFeatureStatus = {
  feature_code: string
  granted: boolean
  reason_code: string
  access_mode: string | null
  quota_limit: number | null
  quota_remaining: number | null
  variant_code: string | null
  usage_states: ChatEntitlementUsageState[]
}

export type TokenUsagePeriod = {
  unit: string
  window_start: string
  window_end: string | null
}

export type TokenUsageSummary = {
  tokens_total: number
  tokens_in: number
  tokens_out: number
}

export type TokenUsageStatus = {
  period: TokenUsagePeriod
  summary: TokenUsageSummary
}

export type TokenUsageBreakdown = {
  current_day: TokenUsageStatus
  current_week: TokenUsageStatus
  current_month: TokenUsageStatus
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

type TokenUsageApiResponse = {
  data: TokenUsageStatus
}

const CHAT_QUOTA_FEATURE_CODE = "astrologer_chat"

function toChatEntitlementUsage(feature: FeatureEntitlementResponse | undefined): ChatEntitlementUsageStatus | null {
  const usage = feature?.usage_states[0]
  if (!usage) {
    return null
  }

  return {
    quota_date: usage.window_start ?? "",
    quota_key: usage.quota_key,
    limit: usage.quota_limit,
    consumed: usage.used,
    remaining: usage.remaining,
    reset_at: usage.window_end ?? "",
    blocked: usage.exhausted || feature?.final_access === false,
  }
}

function toChatEntitlementFeature(feature: FeatureEntitlementResponse | undefined): ChatEntitlementFeatureStatus | null {
  if (!feature) {
    return null
  }

  return {
    feature_code: feature.feature_code,
    granted: feature.final_access,
    reason_code: feature.reason,
    access_mode: feature.final_access ? "quota" : null,
    quota_limit: feature.usage_states[0]?.quota_limit ?? null,
    quota_remaining: feature.usage_states[0]?.remaining ?? null,
    variant_code: null,
    usage_states: feature.usage_states.map((state) => ({
      quota_key: state.quota_key,
      quota_limit: state.quota_limit,
      used: state.used,
      remaining: state.remaining,
      exhausted: state.exhausted,
      period_unit: state.period_unit,
      period_value: state.period_value,
      reset_mode: state.reset_mode,
      window_start: state.window_start,
      window_end: state.window_end,
    })),
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

async function fetchEntitlementsPlans(): Promise<PlanCatalog[]> {
  const response = await fetch(`${API_BASE_URL}/v1/entitlements/plans`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: PlanCatalog[] }
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

async function fetchChatEntitlementFeature(): Promise<ChatEntitlementFeatureStatus | null> {
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
  return toChatEntitlementFeature(chatEntitlement)
}

async function fetchTokenUsagePeriod(period: "current_day" | "current_week" | "current_month"): Promise<TokenUsageStatus> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/token-usage?period=${period}`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as TokenUsageApiResponse
  return body.data
}

async function fetchTokenUsageBreakdown(): Promise<TokenUsageBreakdown> {
  const [current_day, current_week, current_month] = await Promise.all([
    fetchTokenUsagePeriod("current_day"),
    fetchTokenUsagePeriod("current_week"),
    fetchTokenUsagePeriod("current_month"),
  ])

  return { current_day, current_week, current_month }
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

export function useEntitlementsPlans() {
  return useQuery({
    queryKey: ["entitlements-plans"],
    queryFn: fetchEntitlementsPlans,
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

export function useTokenUsageBreakdown() {
  return useQuery({
    queryKey: ["token-usage-breakdown"],
    queryFn: fetchTokenUsageBreakdown,
    retry: (failureCount, error) => {
      if (error instanceof BillingApiError && error.status === 403) return false
      return failureCount < 1
    },
  })
}

export function useChatEntitlementFeature() {
  return useQuery({
    queryKey: ["chat-entitlement-feature"],
    queryFn: fetchChatEntitlementFeature,
    retry: (failureCount, error) => {
      if (error instanceof BillingApiError && error.status === 403) return false
      return failureCount < 1
    },
  })
}

// --- Stripe-first endpoints ---

export type StripeCheckoutSessionData = { checkout_url: string }
export type StripePortalSessionData = { url: string }
export type StripeSubscriptionUpgradeData = {
  checkout_url: string | null
  invoice_status: string | null
  amount_due_cents: number
  currency: string | null
}

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

async function postStripeSubscriptionReactivate(): Promise<BillingSubscriptionStatus> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/stripe-subscription-reactivate`, {
    method: "POST",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: BillingSubscriptionStatus }
  return body.data
}

async function postStripeSubscriptionUpgrade(
  plan: "basic" | "premium",
): Promise<StripeSubscriptionUpgradeData> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/stripe-subscription-upgrade`, {
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
  const body = (await response.json()) as { data: StripeSubscriptionUpgradeData }
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

export function useStripeSubscriptionReactivate() {
  return useMutation({
    mutationFn: postStripeSubscriptionReactivate,
  })
}

export function useStripeSubscriptionUpgrade() {
  return useMutation({
    mutationFn: postStripeSubscriptionUpgrade,
  })
}

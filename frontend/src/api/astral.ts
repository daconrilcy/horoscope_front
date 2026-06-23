// Client centralise de la facade backend Astral, sans contact navigateur avec Astral Docker.
import { useEffect } from "react"
import { useMutation, useQuery } from "@tanstack/react-query"

import {
  ApiError,
  apiFetch,
  parseApiErrorDetails,
  type ApiResponseEnvelope,
} from "./client"
import { hasUsableAccessToken } from "../utils/authToken"

export type AstralPlan = "free" | "basic" | "premium"
export type AstralProduct = "natal_simplified" | "natal_full" | "horoscope_daily" | "horoscope_period"
export type AstralPeriod = "daily" | "next_7_days"

export type AstralJobRequest = {
  product: AstralProduct
  plan: AstralPlan
  period?: AstralPeriod
  birth_profile_id?: number
  chart_calculation_id?: string
  client_request_id: string
  target_language_code?: string
  audience_level?: string
}

export type AstralJobStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "safety_rejected"
  | "cancelled"
  | "expired"
  | string

export type AstralJobResult = {
  schema_version?: string
  contract_version?: string
  metadata?: Record<string, unknown>
  quality?: Record<string, unknown>
  reading?: unknown
  [key: string]: unknown
}

export type AstralJobResponse = {
  run_id: string
  status: AstralJobStatus
  service_code?: string
  poll_url?: string
  poll_after_ms?: number
  events_path?: string
  token_usage?: Record<string, unknown>
  result?: AstralJobResult | null
  error?: Record<string, unknown> | null
  [key: string]: unknown
}

export type AstralJobEvent = Partial<AstralJobResponse> & {
  event?: string
}

export const ASTRAL_CLIENT_VERSION = "astral-auth-guard-v3"

function resolveAstralClientSource(): string {
  if (typeof window === "undefined") {
    return "server"
  }
  return `${window.location.pathname}${window.location.search}`
}

function authHeaders(accessToken: string, request?: AstralJobRequest) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${accessToken}`,
    "X-Astral-Client-Version": ASTRAL_CLIENT_VERSION,
    "X-Astral-Client-Source": resolveAstralClientSource(),
    ...(request?.client_request_id ? { "X-Client-Request-Id": request.client_request_id } : {}),
  }
}

async function readAstralResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await parseApiErrorDetails(response, {})
    throw new ApiError(
      error.code,
      error.message,
      response.status,
      error.requestId ?? undefined,
    )
  }
  const payload = (await response.json()) as ApiResponseEnvelope<T>
  return payload.data
}

export async function submitAstralJob(
  accessToken: string,
  request: AstralJobRequest,
): Promise<AstralJobResponse> {
  if (!hasUsableAccessToken(accessToken)) {
    throw new ApiError("unauthorized", "access token is required", 401)
  }
  const response = await apiFetch("/v1/astral/jobs", {
    method: "POST",
    headers: authHeaders(accessToken, request),
    body: JSON.stringify(request),
    timeoutMs: 30000,
  })
  return readAstralResponse<AstralJobResponse>(response)
}

export async function getAstralJobStatus(
  accessToken: string,
  runId: string,
): Promise<AstralJobResponse> {
  if (!hasUsableAccessToken(accessToken)) {
    throw new ApiError("unauthorized", "access token is required", 401)
  }
  const response = await apiFetch(`/v1/astral/jobs/${encodeURIComponent(runId)}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    timeoutMs: 15000,
  })
  return readAstralResponse<AstralJobResponse>(response)
}

export function useSubmitAstralJob(accessToken: string | null) {
  return useMutation({
    mutationFn: (request: AstralJobRequest) => {
      if (!hasUsableAccessToken(accessToken)) {
        throw new ApiError("unauthorized", "access token is required", 401)
      }
      return submitAstralJob(accessToken, request)
    },
  })
}

export function useAstralJobStatus(accessToken: string | null, runId: string | null) {
  return useQuery({
    queryKey: ["astral-job", runId],
    queryFn: () => getAstralJobStatus(accessToken!, runId!),
    enabled: hasUsableAccessToken(accessToken) && Boolean(runId),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === "queued" || status === "running" ? 2500 : false
    },
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        return false
      }
      return failureCount < 2
    },
  })
}

function parseSseMessage(rawMessage: string): AstralJobEvent | null {
  const data = rawMessage
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice("data:".length).trim())
    .join("\n")
  if (!data) return null
  try {
    return JSON.parse(data) as AstralJobEvent
  } catch {
    return null
  }
}

export function useAstralJobEvents(
  accessToken: string | null,
  runId: string | null,
  onEvent: (event: AstralJobEvent) => void,
) {
  useEffect(() => {
    if (!hasUsableAccessToken(accessToken) || !runId) return undefined
    const controller = new AbortController()

    async function consumeEvents() {
      const response = await apiFetch(`/v1/astral/jobs/${encodeURIComponent(runId!)}/events`, {
        headers: { Authorization: `Bearer ${accessToken}` },
        signal: controller.signal,
        timeoutMs: 300000,
      })
      if (!response.ok || !response.body) return

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

      while (!controller.signal.aborted) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const messages = buffer.split("\n\n")
        buffer = messages.pop() ?? ""
        for (const message of messages) {
          const event = parseSseMessage(message)
          if (event) onEvent(event)
        }
      }
    }

    void consumeEvents().catch(() => undefined)
    return () => controller.abort()
  }, [accessToken, runId, onEvent])
}

export function buildAstralClientRequestId(prefix: string): string {
  const randomId =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`
  return `${prefix}-${randomId}`
}

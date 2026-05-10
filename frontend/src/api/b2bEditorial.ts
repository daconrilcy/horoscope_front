import { useMutation } from "@tanstack/react-query"

import { apiFetch, parseApiErrorDetails } from "./client"

export type B2BEditorialConfig = {
  config_id: number | null
  account_id: number
  version_number: number
  is_active: boolean
  tone: "neutral" | "friendly" | "premium"
  length_style: "short" | "medium" | "long"
  output_format: "paragraph" | "bullet"
  preferred_terms: string[]
  avoided_terms: string[]
  created_by_credential_id: number | null
  created_at: string | null
  updated_at: string | null
}

export type B2BEditorialUpdatePayload = {
  tone: "neutral" | "friendly" | "premium"
  length_style: "short" | "medium" | "long"
  output_format: "paragraph" | "bullet"
  preferred_terms: string[]
  avoided_terms: string[]
}

export class B2BEditorialApiError extends Error {
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
  const error = await parseApiErrorDetails<Record<string, unknown>>(response, {})
  throw new B2BEditorialApiError(
    error.code,
    error.message,
    response.status,
    error.details,
    error.requestId,
  )
}

async function getB2BEditorialConfig(apiKey: string): Promise<B2BEditorialConfig> {
  const response = await apiFetch("/v1/b2b/editorial/config", {
    method: "GET",
    headers: { "X-API-Key": apiKey },
  })
  if (!response.ok) {
    return parseError(response)
  }
  const payload = (await response.json()) as { data: B2BEditorialConfig }
  return payload.data
}

async function updateB2BEditorialConfig(input: {
  apiKey: string
  payload: B2BEditorialUpdatePayload
}): Promise<B2BEditorialConfig> {
  const response = await apiFetch("/v1/b2b/editorial/config", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": input.apiKey,
    },
    body: JSON.stringify(input.payload),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const payload = (await response.json()) as { data: B2BEditorialConfig }
  return payload.data
}

export function useB2BEditorialConfig() {
  return useMutation({
    mutationFn: getB2BEditorialConfig,
  })
}

export function useUpdateB2BEditorialConfig() {
  return useMutation({
    mutationFn: updateB2BEditorialConfig,
  })
}

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

export type B2BWeeklyBySignItem = {
  sign_code: string
  sign_name: string
  weekly_summary: string
}

export type B2BWeeklyBySignData = {
  api_version: string
  reference_version: string
  generated_at: string
  items: B2BWeeklyBySignItem[]
}

export class B2BAstrologyApiError extends Error {
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

async function getWeeklyBySign(apiKey: string): Promise<B2BWeeklyBySignData> {
  const response = await fetch(`${API_BASE_URL}/v1/b2b/astrology/weekly-by-sign`, {
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
    throw new B2BAstrologyApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `Request failed with status ${response.status}`,
      response.status,
      payload?.error?.details ?? {},
      payload?.error?.request_id ?? null,
    )
  }
  const payload = (await response.json()) as { data: B2BWeeklyBySignData }
  return payload.data
}

export function useB2BWeeklyBySign() {
  return useMutation({
    mutationFn: getWeeklyBySign,
  })
}

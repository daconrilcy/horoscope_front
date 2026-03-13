import { useMutation } from "@tanstack/react-query"
import { API_BASE_URL, apiFetch } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

export type PrecisionLevel = "high" | "medium" | "limited" | "blocked"
export type ConsultationStatus = "nominal" | "degraded" | "blocked"
export type UserProfileQuality = "complete" | "incomplete" | "missing"

export type FallbackMode =
  | "user_no_birth_time"
  | "other_no_birth_time"
  | "relation_user_only"
  | "timing_degraded"
  | "blocking_missing_data"
  | "safeguard_reframed"
  | "safeguard_refused"

export type SafeguardIssue =
  | "health"
  | "emotional_distress"
  | "obsessive_relation"
  | "pregnancy"
  | "death"
  | "legal_finance"
  | "third_party_manipulation"

export interface OtherPersonData {
  birth_date: string
  birth_time?: string
  birth_time_known: boolean
  birth_place: string
  birth_city?: string
  birth_country?: string
  place_resolved_id?: number
  birth_lat?: number
  birth_lon?: number
}

export interface ConsultationPrecheckRequest {
  consultation_type: string
  question?: string
  horizon?: string
  other_person?: OtherPersonData
}

export interface ConsultationPrecheckData {
  consultation_type: string
  user_profile_quality: UserProfileQuality
  precision_level: PrecisionLevel
  status: ConsultationStatus
  missing_fields: string[]
  available_modes: string[]
  fallback_mode: FallbackMode | null
  safeguard_issue: SafeguardIssue | null
  blocking_reasons: string[]
}

export interface ConsultationPrecheckResponse {
  data: ConsultationPrecheckData
  meta: {
    request_id: string
    contract_version: string
  }
}

export interface ConsultationGenerateRequest {
  consultation_type: string
  question: string
  objective?: string
  horizon?: string
  other_person?: OtherPersonData
  astrologer_id?: string
}

export interface ConsultationSection {
  id: string
  title: string
  content: string
}

export interface ConsultationGenerateData {
  consultation_id: string
  contract_version: string
  consultation_type: string
  status: ConsultationStatus
  precision_level: PrecisionLevel
  fallback_mode: FallbackMode | null
  safeguard_issue: SafeguardIssue | null
  route_key: string | null
  summary: string
  sections: ConsultationSection[]
  chat_prefill: string
  metadata: any
}

export interface ConsultationGenerateResponse {
  data: ConsultationGenerateData
  meta: {
    request_id: string
    contract_version: string
  }
}

export class ConsultationApiError extends Error {
  code: string
  status: number
  details: any

  constructor(
    code: string,
    message: string,
    status: number,
    details: any = {}
  ) {
    super(message)
    this.name = "ConsultationApiError"
    this.code = code
    this.status = status
    this.details = details
  }
}

export async function precheckConsultation(
  payload: ConsultationPrecheckRequest
): Promise<ConsultationPrecheckResponse> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/consultations/precheck`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify(payload),
    })

    const json = await response.json()

    if (!response.ok) {
      throw new ConsultationApiError(
        json.error?.code || "unknown_error",
        json.error?.message || "An unknown error occurred",
        response.status,
        json.error?.details
      )
    }

    return json
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ConsultationApiError(
        "request_timeout",
        "The consultation request timed out",
        0
      )
    }
    throw error
  }
}

export function useConsultationPrecheck() {
  return useMutation({
    mutationFn: precheckConsultation,
  })
}

export async function generateConsultation(
  payload: ConsultationGenerateRequest
): Promise<ConsultationGenerateResponse> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/consultations/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify(payload),
    })

    const json = await response.json()

    if (!response.ok) {
      throw new ConsultationApiError(
        json.error?.code || "unknown_error",
        json.error?.message || "An unknown error occurred",
        response.status,
        json.error?.details
      )
    }

    return json
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ConsultationApiError(
        "request_timeout",
        "The consultation request timed out",
        0
      )
    }
    throw error
  }
}

export function useConsultationGenerate() {
  return useMutation({
    mutationFn: generateConsultation,
  })
}

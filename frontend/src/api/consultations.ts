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
}

export function useConsultationPrecheck() {
  return useMutation({
    mutationFn: precheckConsultation,
  })
}

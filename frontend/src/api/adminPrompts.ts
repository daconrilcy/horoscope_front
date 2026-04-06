import { useMutation, useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

type ErrorEnvelope = {
  error?: {
    code?: string
    message?: string
    details?: Record<string, unknown>
  }
}

type ResponseEnvelope<T> = {
  data: T
}

export type AdminLlmPersona = {
  id: string
  name: string
  enabled: boolean
}

export type AdminLlmUseCase = {
  key: string
  display_name: string
  description: string
  persona_strategy: string
  safety_profile: string
  allowed_persona_ids: string[]
  active_prompt_version_id: string | null
}

export type AdminPromptVersion = {
  id: string
  use_case_key: string
  status: "draft" | "published" | "archived"
  developer_prompt: string
  model: string
  temperature: number
  max_output_tokens: number
  fallback_use_case_key: string | null
  created_by: string
  created_at: string
  published_at: string | null
}

export class AdminPromptsApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, unknown>

  constructor(code: string, message: string, status: number, details: Record<string, unknown> = {}) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
  }
}

function toTransportError(error: unknown): AdminPromptsApiError {
  if (error instanceof AdminPromptsApiError) {
    return error
  }
  if (error instanceof DOMException && error.name === "AbortError") {
    return new AdminPromptsApiError(
      "request_timeout",
      "La requete a expire. Reessayez dans un instant.",
      408,
      {},
    )
  }
  return new AdminPromptsApiError("network_error", "Erreur reseau. Reessayez plus tard.", 0, {})
}

async function decodeResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: ErrorEnvelope | null = null
    try {
      payload = (await response.json()) as ErrorEnvelope
    } catch {
      payload = null
    }
    throw new AdminPromptsApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `Request failed with status ${response.status}`,
      response.status,
      payload?.error?.details ?? {},
    )
  }
  const payload = (await response.json()) as ResponseEnvelope<T>
  return payload.data
}

export async function listAdminLlmUseCases(): Promise<AdminLlmUseCase[]> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/use-cases`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<AdminLlmUseCase[]>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function listAdminLlmPersonas(): Promise<AdminLlmPersona[]> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/personas`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<AdminLlmPersona[]>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function listPromptHistory(useCaseKey: string): Promise<AdminPromptVersion[]> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/use-cases/${useCaseKey}/prompts`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<AdminPromptVersion[]>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function rollbackPromptVersion(params: {
  useCaseKey: string
  targetVersionId: string
}): Promise<AdminPromptVersion> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/use-cases/${params.useCaseKey}/rollback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify({ target_version_id: params.targetVersionId }),
    })
    return decodeResponse<AdminPromptVersion>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export function useAdminLlmUseCases() {
  return useQuery({
    queryKey: ["admin-llm-use-cases"],
    queryFn: listAdminLlmUseCases,
  })
}

export function useAdminLlmPersonas() {
  return useQuery({
    queryKey: ["admin-llm-personas"],
    queryFn: listAdminLlmPersonas,
  })
}

export function useAdminPromptHistory(useCaseKey: string, enabled = true) {
  return useQuery({
    queryKey: ["admin-llm-prompt-history", useCaseKey],
    queryFn: () => listPromptHistory(useCaseKey),
    enabled,
  })
}

export function useRollbackPromptVersion() {
  return useMutation({
    mutationFn: rollbackPromptVersion,
  })
}

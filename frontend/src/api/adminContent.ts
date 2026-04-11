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

export type AdminContentText = {
  key: string
  value: string
  category: string
  updated_at: string
  updated_by_user_id: number | null
}

export type AdminContentFeatureFlag = {
  key: string
  description: string
  enabled: boolean
  target_roles: string[]
  target_user_ids: number[]
  updated_by_user_id: number | null
  updated_at: string
  scope: string
}

export type EditorialTemplateSummary = {
  template_code: string
  title: string
  active_version_id: string | null
  active_version_number: number | null
  published_at: string | null
}

export type EditorialTemplateVersion = {
  id: string
  template_code: string
  version_number: number
  title: string
  content: string
  expected_tags: string[]
  example_render: string | null
  status: string
  created_at: string
  published_at: string | null
  created_by_user_id: number | null
}

export type EditorialTemplateDetail = {
  template_code: string
  active_version_id: string | null
  versions: EditorialTemplateVersion[]
}

export type CalibrationRule = {
  rule_code: string
  value: string
  data_type: string
  description: string
  ruleset_version: string
}

export class AdminContentApiError extends Error {
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

function toTransportError(error: unknown): AdminContentApiError {
  if (error instanceof AdminContentApiError) {
    return error
  }
  if (error instanceof DOMException && error.name === "AbortError") {
    return new AdminContentApiError("request_timeout", "La requete a expire.", 408, {})
  }
  return new AdminContentApiError("network_error", "Erreur reseau.", 0, {})
}

async function decodeResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: ErrorEnvelope | null = null
    try {
      payload = (await response.json()) as ErrorEnvelope
    } catch {
      payload = null
    }
    throw new AdminContentApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `Request failed with status ${response.status}`,
      response.status,
      payload?.error?.details ?? {},
    )
  }
  const payload = (await response.json()) as ResponseEnvelope<T>
  return payload.data
}

export async function listContentTexts(category: string): Promise<AdminContentText[]> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/content/texts?category=${encodeURIComponent(category)}`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<AdminContentText[]>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function updateContentText(key: string, value: string): Promise<AdminContentText> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/content/texts/${encodeURIComponent(key)}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify({ value }),
    })
    return decodeResponse<AdminContentText>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function listContentFeatureFlags(): Promise<AdminContentFeatureFlag[]> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/content/feature-flags`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<AdminContentFeatureFlag[]>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function updateContentFeatureFlag(
  key: string,
  enabled: boolean,
  targetRoles: string[],
  targetUserIds: number[],
): Promise<AdminContentFeatureFlag> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/content/feature-flags/${encodeURIComponent(key)}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify({ enabled, target_roles: targetRoles, target_user_ids: targetUserIds }),
    })
    return decodeResponse<AdminContentFeatureFlag>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function listEditorialTemplates(): Promise<EditorialTemplateSummary[]> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/content/editorial-templates`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<EditorialTemplateSummary[]>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function getEditorialTemplate(templateCode: string): Promise<EditorialTemplateDetail> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/content/editorial-templates/${encodeURIComponent(templateCode)}`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<EditorialTemplateDetail>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function createEditorialTemplateVersion(
  templateCode: string,
  payload: { title: string; content: string; expected_tags: string[]; example_render: string },
): Promise<EditorialTemplateDetail> {
  try {
    const response = await apiFetch(
      `${API_BASE_URL}/v1/admin/content/editorial-templates/${encodeURIComponent(templateCode)}/versions`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...getAccessTokenAuthHeader(),
        },
        body: JSON.stringify(payload),
      },
    )
    return decodeResponse<EditorialTemplateDetail>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function rollbackEditorialTemplate(
  templateCode: string,
  versionId: string,
): Promise<EditorialTemplateDetail> {
  try {
    const response = await apiFetch(
      `${API_BASE_URL}/v1/admin/content/editorial-templates/${encodeURIComponent(templateCode)}/rollback`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...getAccessTokenAuthHeader(),
        },
        body: JSON.stringify({ version_id: versionId }),
      },
    )
    return decodeResponse<EditorialTemplateDetail>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function listCalibrationRules(): Promise<CalibrationRule[]> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/content/calibration-rules`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<CalibrationRule[]>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function updateCalibrationRule(ruleCode: string, value: string): Promise<CalibrationRule> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/content/calibration-rules/${encodeURIComponent(ruleCode)}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify({ value }),
    })
    return decodeResponse<CalibrationRule>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export function useAdminContentTexts(category: string) {
  return useQuery({
    queryKey: ["admin-content-texts", category],
    queryFn: () => listContentTexts(category),
  })
}

export function useUpdateAdminContentText() {
  return useMutation({
    mutationFn: ({ key, value }: { key: string; value: string }) => updateContentText(key, value),
  })
}

export function useAdminContentFeatureFlags() {
  return useQuery({
    queryKey: ["admin-content-feature-flags"],
    queryFn: listContentFeatureFlags,
  })
}

export function useUpdateAdminContentFeatureFlag() {
  return useMutation({
    mutationFn: (params: {
      key: string
      enabled: boolean
      targetRoles: string[]
      targetUserIds: number[]
    }) => updateContentFeatureFlag(params.key, params.enabled, params.targetRoles, params.targetUserIds),
  })
}

export function useEditorialTemplates() {
  return useQuery({
    queryKey: ["admin-editorial-templates"],
    queryFn: listEditorialTemplates,
  })
}

export function useEditorialTemplate(templateCode: string | null, enabled = true) {
  return useQuery({
    queryKey: ["admin-editorial-template", templateCode],
    queryFn: () => getEditorialTemplate(templateCode!),
    enabled: enabled && !!templateCode,
  })
}

export function useCreateEditorialTemplateVersion() {
  return useMutation({
    mutationFn: (params: {
      templateCode: string
      title: string
      content: string
      expected_tags: string[]
      example_render: string
    }) =>
      createEditorialTemplateVersion(params.templateCode, {
        title: params.title,
        content: params.content,
        expected_tags: params.expected_tags,
        example_render: params.example_render,
      }),
  })
}

export function useRollbackEditorialTemplate() {
  return useMutation({
    mutationFn: ({ templateCode, versionId }: { templateCode: string; versionId: string }) =>
      rollbackEditorialTemplate(templateCode, versionId),
  })
}

export function useCalibrationRules() {
  return useQuery({
    queryKey: ["admin-calibration-rules"],
    queryFn: listCalibrationRules,
  })
}

export function useUpdateCalibrationRule() {
  return useMutation({
    mutationFn: ({ ruleCode, value }: { ruleCode: string; value: string }) =>
      updateCalibrationRule(ruleCode, value),
  })
}

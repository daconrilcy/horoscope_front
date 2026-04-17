import { useMutation, useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query"

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

function normalizeUtcDateTimeParam(value: string): string {
  const trimmed = value.trim()
  if (!trimmed) return trimmed
  const hasExplicitTimezone = /([zZ]|[+\-]\d{2}:\d{2})$/.test(trimmed)
  const asDate = new Date(trimmed)
  if (Number.isNaN(asDate.getTime())) {
    return trimmed
  }
  if (hasExplicitTimezone) {
    return asDate.toISOString()
  }
  // datetime-local values do not contain timezone information.
  // Interpret them as local time then convert to UTC ISO for backend contract.
  return new Date(
    asDate.getFullYear(),
    asDate.getMonth(),
    asDate.getDate(),
    asDate.getHours(),
    asDate.getMinutes(),
    asDate.getSeconds(),
    asDate.getMilliseconds(),
  ).toISOString()
}

export function toUtcIsoFromDateTimeInput(value: string): string {
  return normalizeUtcDateTimeParam(value)
}

export type AdminLlmPersona = {
  id: string
  name: string
  enabled: boolean
  description: string | null
  tone: string
  verbosity: string
  style_markers: string[]
  boundaries: string[]
  allowed_topics: string[]
  disallowed_topics: string[]
  formatting: Record<string, boolean>
  created_at: string
  updated_at: string
}

export type AdminLlmPersonaDetail = {
  persona: AdminLlmPersona
  use_cases: string[]
  affected_users_count: number
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

export type AdminLlmCatalogEntry = {
  manifest_entry_id: string
  feature: string
  subfeature: string | null
  plan: string | null
  locale: string | null
  assembly_id: string | null
  assembly_status: string
  execution_profile_id: string | null
  execution_profile_ref: string | null
  output_contract_ref: string | null
  active_snapshot_id: string | null
  active_snapshot_version: string | null
  provider: string | null
  model: string | null
  source_of_truth_status: string
  release_health_status: string
  catalog_visibility_status: string
  runtime_signal_status: string
  execution_path_kind: string | null
  context_compensation_status: string | null
  max_output_tokens_source: string | null
}

export type AdminLlmCatalogResponse = {
  data: AdminLlmCatalogEntry[]
  meta: {
    total: number
    page: number
    page_size: number
    sort_by: string
    sort_order: "asc" | "desc"
    freshness_window_minutes: number
    facets?: {
      feature?: string[]
      subfeature?: string[]
      plan?: string[]
      locale?: string[]
      provider?: string[]
      source_of_truth_status?: string[]
      assembly_status?: string[]
      release_health_status?: string[]
      catalog_visibility_status?: string[]
    }
  }
}

export type AdminResolvedPlaceholder = {
  name: string
  status:
    | "resolved"
    | "optional_missing"
    | "fallback_used"
    | "blocking_missing"
    | "expected_missing_in_preview"
    | "unknown"
  classification: string | null
  resolution_source: string | null
  reason: string | null
  safe_to_display: boolean
  value_preview: string | null
}

export type AdminInspectionMode = "assembly_preview" | "runtime_preview" | "live_execution"

export type AdminLlmSamplePayload = {
  id: string
  name: string
  feature: string
  locale: string
  payload_json: Record<string, unknown>
  description: string | null
  is_default: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export type AdminLlmSamplePayloadSummary = {
  id: string
  name: string
  feature: string
  locale: string
  description: string | null
  is_default: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export type AdminLlmSamplePayloadList = {
  items: AdminLlmSamplePayloadSummary[]
  recommended_default_id: string | null
}

export type AdminLlmSamplePayloadCreateInput = {
  name: string
  feature: string
  locale: string
  payload_json: Record<string, unknown>
  description?: string | null
  is_default?: boolean
  is_active?: boolean
}

export type AdminLlmSamplePayloadUpdateInput = {
  name?: string
  locale?: string
  payload_json?: Record<string, unknown>
  description?: string | null
  is_default?: boolean
  is_active?: boolean
}

export type AdminResolvedAssemblyView = {
  manifest_entry_id: string
  feature: string
  subfeature: string | null
  plan: string | null
  locale: string | null
  assembly_id: string | null
  inspection_mode: AdminInspectionMode
  source_of_truth_status: string
  active_snapshot_id: string | null
  active_snapshot_version: string | null
  composition_sources: {
    feature_template: { id: string; content: string }
    subfeature_template: { id: string; content: string } | null
    plan_rules: { ref: string | null; content: string | null } | null
    persona_block: { id: string | null; name: string | null; content: string | null } | null
    hard_policy: { safety_profile: string; content: string }
    execution_profile: {
      id: string | null
      name: string | null
      provider: string
      model: string
      reasoning: string | null
      verbosity: string | null
      provider_params: Record<string, unknown>
    }
  }
  transformation_pipeline: {
    assembled_prompt: string
    post_injectors_prompt: string
    rendered_prompt: string
  }
  resolved_result: {
    provider_messages: {
      render_error?: string | null
      render_error_kind?: "execution_failure" | "static_preview_incomplete" | null
    } & Record<string, unknown>
    placeholders: AdminResolvedPlaceholder[]
    context_quality_handled_by_template: boolean
    context_quality_instruction_injected: boolean
    context_compensation_status: string
    source_of_truth_status: string
    active_snapshot_id: string | null
    active_snapshot_version: string | null
    manifest_entry_id: string
  }
}

export type ProofSummary = {
  proof_type: "qualification" | "golden" | "smoke" | "readiness"
  status: string
  verdict: string | null
  generated_at: string | null
  manifest_entry_id: string | null
  correlated: boolean
}

export type SnapshotTimelineItem = {
  event_type: "created" | "validated" | "activated" | "monitoring" | "degraded" | "rollback_recommended" | "rolled_back" | "backend_unmapped"
  snapshot_id: string
  snapshot_version: string
  occurred_at: string
  current_status: string
  release_health_status: string
  status_history: Array<Record<string, unknown>>
  reason: string | null
  from_snapshot_id: string | null
  to_snapshot_id: string | null
  manifest_entry_count: number
  proof_summaries: ProofSummary[]
}

export type SnapshotDiffEntry = {
  manifest_entry_id: string
  category: "added" | "removed" | "changed" | "unchanged"
  assembly_changed: boolean
  execution_profile_changed: boolean
  output_contract_changed: boolean
  from_snapshot_id: string
  to_snapshot_id: string
}

export type SnapshotDiffResponse = {
  from_snapshot_id: string
  to_snapshot_id: string
  entries: SnapshotDiffEntry[]
}

export type AdminConsumptionView = "user" | "subscription" | "feature"
export type AdminConsumptionGranularity = "day" | "month"

export type AdminConsumptionRow = {
  period_start_utc: string
  granularity: AdminConsumptionGranularity
  user_id: number | null
  user_email: string | null
  subscription_plan: string | null
  feature: string | null
  subfeature: string | null
  request_count: number
  input_tokens: number
  output_tokens: number
  total_tokens: number
  estimated_cost: number
  avg_latency_ms: number
  error_rate: number
}

export type AdminConsumptionResponse = {
  data: AdminConsumptionRow[]
  meta: {
    view: AdminConsumptionView
    granularity: AdminConsumptionGranularity
    count: number
    page: number
    page_size: number
    sort_by: string
    sort_order: "asc" | "desc"
    timezone: string
    default_granularity_behavior: string
  }
}

export type AdminConsumptionDrilldownRow = {
  request_id: string
  timestamp: string
  feature: string | null
  subfeature: string | null
  provider: string | null
  active_snapshot_version: string | null
  manifest_entry_id: string | null
  validation_status: string
}

export type AdminConsumptionDrilldownResponse = {
  data: AdminConsumptionDrilldownRow[]
  meta: {
    count: number
    limit: number
    order: string
  }
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

export async function listAdminLlmCatalog(
  params: {
    page?: number
    pageSize?: number
    search?: string
    feature?: string
    subfeature?: string
    plan?: string
    locale?: string
    provider?: string
    sourceOfTruthStatus?: string
    assemblyStatus?: string
    releaseHealthStatus?: string
    catalogVisibilityStatus?: string
    sortBy?: string
    sortOrder?: "asc" | "desc"
  } = {},
): Promise<AdminLlmCatalogResponse> {
  try {
    const query = new URLSearchParams()
    if (params.page) query.set("page", String(params.page))
    if (params.pageSize) query.set("page_size", String(params.pageSize))
    if (params.search) query.set("search", params.search)
    if (params.feature) query.set("feature", params.feature)
    if (params.subfeature) query.set("subfeature", params.subfeature)
    if (params.plan) query.set("plan", params.plan)
    if (params.locale) query.set("locale", params.locale)
    if (params.provider) query.set("provider", params.provider)
    if (params.sourceOfTruthStatus) query.set("source_of_truth_status", params.sourceOfTruthStatus)
    if (params.assemblyStatus) query.set("assembly_status", params.assemblyStatus)
    if (params.releaseHealthStatus) query.set("release_health_status", params.releaseHealthStatus)
    if (params.catalogVisibilityStatus) query.set("catalog_visibility_status", params.catalogVisibilityStatus)
    if (params.sortBy) query.set("sort_by", params.sortBy)
    if (params.sortOrder) query.set("sort_order", params.sortOrder)

    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/catalog?${query.toString()}`, {
      headers: getAccessTokenAuthHeader(),
    })

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

    const payload = (await response.json()) as AdminLlmCatalogResponse
    return payload
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function getAdminPersonaDetail(personaId: string): Promise<AdminLlmPersonaDetail> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/personas/${personaId}`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<AdminLlmPersonaDetail>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function getAdminResolvedAssembly(
  manifestEntryId: string,
  options: { inspectionMode?: AdminInspectionMode; samplePayloadId?: string } = {},
): Promise<AdminResolvedAssemblyView> {
  try {
    const query = new URLSearchParams()
    if (options.inspectionMode) {
      query.set("inspection_mode", options.inspectionMode)
    }
    if (options.samplePayloadId) {
      query.set("sample_payload_id", options.samplePayloadId)
    }
    const qs = query.toString()
    const response = await apiFetch(
      `${API_BASE_URL}/v1/admin/llm/catalog/${encodeURIComponent(manifestEntryId)}/resolved${qs ? `?${qs}` : ""}`,
      {
        headers: getAccessTokenAuthHeader(),
      },
    )
    return decodeResponse<AdminResolvedAssemblyView>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function listAdminLlmSamplePayloads(
  feature: string,
  locale: string,
  options: { includeInactive?: boolean } = {},
): Promise<AdminLlmSamplePayloadList> {
  try {
    const query = new URLSearchParams()
    query.set("feature", feature)
    query.set("locale", locale)
    if (options.includeInactive) {
      query.set("include_inactive", "true")
    }
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/sample-payloads?${query.toString()}`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<AdminLlmSamplePayloadList>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function getAdminLlmSamplePayload(samplePayloadId: string): Promise<AdminLlmSamplePayload> {
  try {
    const response = await apiFetch(
      `${API_BASE_URL}/v1/admin/llm/sample-payloads/${encodeURIComponent(samplePayloadId)}`,
      {
        headers: getAccessTokenAuthHeader(),
      },
    )
    return decodeResponse<AdminLlmSamplePayload>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function createAdminLlmSamplePayload(
  payload: AdminLlmSamplePayloadCreateInput,
): Promise<AdminLlmSamplePayload> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/sample-payloads`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify(payload),
    })
    return decodeResponse<AdminLlmSamplePayload>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function updateAdminLlmSamplePayload(
  samplePayloadId: string,
  payload: AdminLlmSamplePayloadUpdateInput,
): Promise<AdminLlmSamplePayload> {
  try {
    const response = await apiFetch(
      `${API_BASE_URL}/v1/admin/llm/sample-payloads/${encodeURIComponent(samplePayloadId)}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          ...getAccessTokenAuthHeader(),
        },
        body: JSON.stringify(payload),
      },
    )
    return decodeResponse<AdminLlmSamplePayload>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function deleteAdminLlmSamplePayload(samplePayloadId: string): Promise<{ id: string }> {
  try {
    const response = await apiFetch(
      `${API_BASE_URL}/v1/admin/llm/sample-payloads/${encodeURIComponent(samplePayloadId)}`,
      {
        method: "DELETE",
        headers: getAccessTokenAuthHeader(),
      },
    )
    return decodeResponse<{ id: string }>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function listReleaseSnapshotsTimeline(): Promise<SnapshotTimelineItem[]> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/release-snapshots/timeline`, {
      headers: getAccessTokenAuthHeader(),
    })
    return decodeResponse<SnapshotTimelineItem[]>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function getReleaseSnapshotDiff(
  fromSnapshotId: string,
  toSnapshotId: string,
): Promise<SnapshotDiffResponse> {
  try {
    const response = await apiFetch(
      `${API_BASE_URL}/v1/admin/llm/release-snapshots/diff?from_snapshot_id=${encodeURIComponent(fromSnapshotId)}&to_snapshot_id=${encodeURIComponent(toSnapshotId)}`,
      {
        headers: getAccessTokenAuthHeader(),
      },
    )
    return decodeResponse<SnapshotDiffResponse>(response)
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function getAdminConsumption(params: {
  view: AdminConsumptionView
  granularity: AdminConsumptionGranularity
  fromUtc?: string
  toUtc?: string
  search?: string
  page?: number
  pageSize?: number
  sortBy?: string
  sortOrder?: "asc" | "desc"
}): Promise<AdminConsumptionResponse> {
  try {
    const query = new URLSearchParams()
    query.set("view", params.view)
    query.set("granularity", params.granularity)
    if (params.fromUtc) query.set("from_utc", normalizeUtcDateTimeParam(params.fromUtc))
    if (params.toUtc) query.set("to_utc", normalizeUtcDateTimeParam(params.toUtc))
    if (params.search) query.set("search", params.search)
    if (params.page) query.set("page", String(params.page))
    if (params.pageSize) query.set("page_size", String(params.pageSize))
    if (params.sortBy) query.set("sort_by", params.sortBy)
    if (params.sortOrder) query.set("sort_order", params.sortOrder)
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/consumption/canonical?${query.toString()}`, {
      headers: getAccessTokenAuthHeader(),
    })
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
    return (await response.json()) as AdminConsumptionResponse
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function getAdminConsumptionDrilldown(params: {
  view: AdminConsumptionView
  granularity: AdminConsumptionGranularity
  periodStartUtc: string
  userId?: number | null
  subscriptionPlan?: string | null
  feature?: string | null
  subfeature?: string | null
}): Promise<AdminConsumptionDrilldownResponse> {
  try {
    const query = new URLSearchParams()
    query.set("view", params.view)
    query.set("granularity", params.granularity)
    query.set("period_start_utc", params.periodStartUtc)
    if (params.userId !== undefined && params.userId !== null) query.set("user_id", String(params.userId))
    if (params.subscriptionPlan) query.set("subscription_plan", params.subscriptionPlan)
    if (params.feature) query.set("feature", params.feature)
    if (params.subfeature) query.set("subfeature", params.subfeature)
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/consumption/canonical/drilldown?${query.toString()}`, {
      headers: getAccessTokenAuthHeader(),
    })
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
    return (await response.json()) as AdminConsumptionDrilldownResponse
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function downloadAdminConsumptionCsv(params: {
  view: AdminConsumptionView
  granularity: AdminConsumptionGranularity
  fromUtc?: string
  toUtc?: string
  search?: string
}): Promise<Blob> {
  try {
    const query = new URLSearchParams()
    query.set("view", params.view)
    query.set("granularity", params.granularity)
    query.set("export", "csv")
    if (params.fromUtc) query.set("from_utc", normalizeUtcDateTimeParam(params.fromUtc))
    if (params.toUtc) query.set("to_utc", normalizeUtcDateTimeParam(params.toUtc))
    if (params.search) query.set("search", params.search)
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/consumption/canonical?${query.toString()}`, {
      headers: getAccessTokenAuthHeader(),
    })
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
    return await response.blob()
  } catch (error) {
    throw toTransportError(error)
  }
}

export async function updateAdminPersona(
  personaId: string,
  payload: Partial<Pick<AdminLlmPersona, "enabled">>,
): Promise<AdminLlmPersona> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/admin/llm/personas/${personaId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify(payload),
    })
    return decodeResponse<AdminLlmPersona>(response)
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

export function useAdminPersonaDetail(personaId: string | null, enabled = true) {
  return useQuery({
    queryKey: ["admin-llm-persona-detail", personaId],
    queryFn: () => getAdminPersonaDetail(personaId ?? ""),
    enabled: enabled && Boolean(personaId),
  })
}

export function useRollbackPromptVersion() {
  return useMutation({
    mutationFn: rollbackPromptVersion,
  })
}

export function useAdminLlmCatalog(
  params: Parameters<typeof listAdminLlmCatalog>[0],
  enabled = true,
) {
  return useQuery({
    queryKey: ["admin-llm-catalog", params],
    queryFn: () => listAdminLlmCatalog(params),
    enabled,
  })
}

export function useUpdateAdminPersona() {
  return useMutation({
    mutationFn: ({ personaId, payload }: { personaId: string; payload: Partial<Pick<AdminLlmPersona, "enabled">> }) =>
      updateAdminPersona(personaId, payload),
  })
}

export function useAdminResolvedAssembly(
  manifestEntryId: string | null,
  inspectionMode: AdminInspectionMode,
  samplePayloadId: string | null,
  enabled = true,
) {
  return useQuery({
    queryKey: ["admin-llm-catalog-resolved", manifestEntryId, inspectionMode, samplePayloadId],
    queryFn: () =>
      getAdminResolvedAssembly(manifestEntryId ?? "", {
        inspectionMode,
        samplePayloadId: samplePayloadId ?? undefined,
      }),
    enabled: enabled && Boolean(manifestEntryId),
  })
}

export function useAdminLlmSamplePayloads(
  feature: string | null,
  locale: string | null,
  options: { enabled?: boolean; includeInactive?: boolean } = {},
) {
  const { enabled = true, includeInactive = false } = options
  return useQuery({
    queryKey: ["admin-llm-sample-payloads", feature, locale, includeInactive],
    queryFn: () => listAdminLlmSamplePayloads(feature ?? "", locale ?? "", { includeInactive }),
    enabled: enabled && Boolean(feature) && Boolean(locale),
  })
}

export function useAdminLlmSamplePayloadDetail(samplePayloadId: string | null, enabled = true) {
  return useQuery({
    queryKey: ["admin-llm-sample-payload-detail", samplePayloadId],
    queryFn: () => getAdminLlmSamplePayload(samplePayloadId ?? ""),
    enabled: enabled && Boolean(samplePayloadId),
  })
}

async function invalidateAdminLlmSamplePayloadQueries(queryClient: QueryClient) {
  await queryClient.invalidateQueries({ queryKey: ["admin-llm-sample-payloads"] })
  await queryClient.invalidateQueries({ queryKey: ["admin-llm-sample-payload-detail"] })
  await queryClient.invalidateQueries({ queryKey: ["admin-llm-catalog-resolved"] })
}

export function useCreateAdminLlmSamplePayload() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createAdminLlmSamplePayload,
    onSuccess: async () => {
      await invalidateAdminLlmSamplePayloadQueries(queryClient)
    },
  })
}

export function useUpdateAdminLlmSamplePayload() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ samplePayloadId, payload }: { samplePayloadId: string; payload: AdminLlmSamplePayloadUpdateInput }) =>
      updateAdminLlmSamplePayload(samplePayloadId, payload),
    onSuccess: async () => {
      await invalidateAdminLlmSamplePayloadQueries(queryClient)
    },
  })
}

export function useDeleteAdminLlmSamplePayload() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteAdminLlmSamplePayload,
    onSuccess: async () => {
      await invalidateAdminLlmSamplePayloadQueries(queryClient)
    },
  })
}

export function useReleaseSnapshotsTimeline(enabled = true) {
  return useQuery({
    queryKey: ["admin-llm-release-snapshots-timeline"],
    queryFn: listReleaseSnapshotsTimeline,
    enabled,
  })
}

export function useReleaseSnapshotDiff(fromSnapshotId: string | null, toSnapshotId: string | null, enabled = true) {
  return useQuery({
    queryKey: ["admin-llm-release-snapshots-diff", fromSnapshotId, toSnapshotId],
    queryFn: () => getReleaseSnapshotDiff(fromSnapshotId ?? "", toSnapshotId ?? ""),
    enabled: enabled && Boolean(fromSnapshotId) && Boolean(toSnapshotId),
  })
}

export function useAdminConsumption(
  params: Parameters<typeof getAdminConsumption>[0],
  enabled = true,
) {
  return useQuery({
    queryKey: ["admin-llm-consumption", params],
    queryFn: () => getAdminConsumption(params),
    enabled,
  })
}

export function useAdminConsumptionDrilldown(
  params: Parameters<typeof getAdminConsumptionDrilldown>[0] | null,
  enabled = true,
) {
  return useQuery({
    queryKey: ["admin-llm-consumption-drilldown", params],
    queryFn: () =>
      getAdminConsumptionDrilldown(
        params ?? {
          view: "user",
          granularity: "day",
          periodStartUtc: new Date().toISOString(),
        },
      ),
    enabled: enabled && Boolean(params),
  })
}

export function useDownloadAdminConsumptionCsv() {
  return useMutation({
    mutationFn: downloadAdminConsumptionCsv,
  })
}

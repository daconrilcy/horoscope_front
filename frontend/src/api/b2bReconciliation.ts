import { useMutation, useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
    request_id?: string
  }
}

export type ReconciliationSeverity = "none" | "minor" | "major"
export type ReconciliationStatus = "open" | "investigating" | "resolved"
export type ReconciliationAction = "recalculate" | "resync" | "mark_investigated" | "annotate"

export type ReconciliationActionHint = {
  code: ReconciliationAction
  label: string
  description: string
}

export type ReconciliationLastAction = {
  action: ReconciliationAction
  at: string
  actor_user_id: number | null
  note: string | null
}

export type ReconciliationIssue = {
  issue_id: string
  account_id: number
  period_start: string
  period_end: string
  mismatch_type: string
  severity: ReconciliationSeverity
  status: ReconciliationStatus
  usage_measured_units: number
  billing_consumed_units: number
  delta_units: number
  billing_cycle_id: number | null
  billable_units: number | null
  total_amount_cents: number | null
  source_trace: Record<string, unknown>
  recommended_actions: ReconciliationActionHint[]
  last_action: ReconciliationLastAction | null
}

export type ReconciliationIssueList = {
  items: ReconciliationIssue[]
  total: number
  limit: number
  offset: number
}

export type ReconciliationIssueDetail = {
  issue: ReconciliationIssue
  action_log: ReconciliationLastAction[]
}

export type ReconciliationActionResult = {
  issue_id: string
  action: ReconciliationAction
  status: string
  message: string
  correction_state: ReconciliationStatus
}

export class B2BReconciliationApiError extends Error {
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

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem("access_token")
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function parseError(response: Response): Promise<never> {
  let payload: ErrorEnvelope | null = null
  try {
    payload = (await response.json()) as ErrorEnvelope
  } catch {
    payload = null
  }
  throw new B2BReconciliationApiError(
    payload?.error?.code ?? "unknown_error",
    payload?.error?.message ?? `Request failed with status ${response.status}`,
    response.status,
    payload?.error?.details ?? {},
    payload?.error?.request_id ?? null,
  )
}

export type ListReconciliationInput = {
  accountId?: number
  periodStart?: string
  periodEnd?: string
  severity?: ReconciliationSeverity
  limit?: number
  offset?: number
}

async function listReconciliationIssues(input: ListReconciliationInput): Promise<ReconciliationIssueList> {
  const params = new URLSearchParams()
  if (
    input.accountId !== undefined &&
    Number.isFinite(input.accountId) &&
    Number.isInteger(input.accountId) &&
    input.accountId > 0
  ) {
    params.set("account_id", String(input.accountId))
  }
  if (input.periodStart) params.set("period_start", input.periodStart)
  if (input.periodEnd) params.set("period_end", input.periodEnd)
  if (input.severity) params.set("severity", input.severity)
  params.set("limit", String(input.limit ?? 20))
  params.set("offset", String(input.offset ?? 0))

  const response = await apiFetch(`${API_BASE_URL}/v1/ops/b2b/reconciliation/issues?${params.toString()}`, {
    method: "GET",
    headers: getAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const payload = (await response.json()) as { data: ReconciliationIssueList }
  return payload.data
}

async function getReconciliationIssueDetail(issueId: string): Promise<ReconciliationIssueDetail> {
  const response = await apiFetch(`${API_BASE_URL}/v1/ops/b2b/reconciliation/issues/${encodeURIComponent(issueId)}`, {
    method: "GET",
    headers: getAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const payload = (await response.json()) as { data: ReconciliationIssueDetail }
  return payload.data
}

export type ExecuteReconciliationActionInput = {
  issueId: string
  action: ReconciliationAction
  note?: string
}

async function executeReconciliationAction(
  input: ExecuteReconciliationActionInput,
): Promise<ReconciliationActionResult> {
  const response = await apiFetch(
    `${API_BASE_URL}/v1/ops/b2b/reconciliation/issues/${encodeURIComponent(input.issueId)}/actions`,
    {
      method: "POST",
      headers: {
        ...getAuthHeader(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ action: input.action, note: input.note ?? null }),
    },
  )
  if (!response.ok) {
    return parseError(response)
  }
  const payload = (await response.json()) as { data: ReconciliationActionResult }
  return payload.data
}

export function useB2BReconciliationIssues(filters: ListReconciliationInput, enabled: boolean) {
  return useQuery({
    queryKey: ["b2b-reconciliation-issues", filters],
    queryFn: () => listReconciliationIssues(filters),
    enabled,
  })
}

export function useB2BReconciliationIssueDetail(issueId: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ["b2b-reconciliation-detail", issueId],
    queryFn: () => getReconciliationIssueDetail(issueId ?? ""),
    enabled: enabled && Boolean(issueId),
  })
}

export function useB2BReconciliationAction() {
  return useMutation({
    mutationFn: executeReconciliationAction,
  })
}

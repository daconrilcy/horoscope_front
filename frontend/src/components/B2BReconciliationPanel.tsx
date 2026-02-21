import { useMemo, useState } from "react"

import {
  B2BReconciliationApiError,
  type ReconciliationAction,
  type ReconciliationIssue,
  useB2BReconciliationAction,
  useB2BReconciliationIssueDetail,
  useB2BReconciliationIssues,
} from "../api/b2bReconciliation"

function getRoleFromAccessToken(): string | null {
  const token = localStorage.getItem("access_token")
  if (!token) {
    return null
  }
  const parts = token.split(".")
  if (parts.length !== 3) {
    return null
  }
  try {
    const base64Url = parts[1].replace(/-/g, "+").replace(/_/g, "/")
    const padding = "=".repeat((4 - (base64Url.length % 4)) % 4)
    const payload = JSON.parse(atob(`${base64Url}${padding}`)) as { role?: string }
    return payload.role ?? null
  } catch {
    return null
  }
}

function describeIssue(issue: ReconciliationIssue): string {
  return `A${issue.account_id} ${issue.period_start} -> ${issue.period_end} (${issue.severity})`
}

function parseAccountId(value: string): number | undefined {
  const trimmed = value.trim()
  if (trimmed === "") {
    return undefined
  }
  if (!/^\d+$/.test(trimmed)) {
    return undefined
  }
  const parsed = Number(trimmed)
  if (!Number.isInteger(parsed) || parsed <= 0) {
    return undefined
  }
  return parsed
}

export function B2BReconciliationPanel() {
  const role = getRoleFromAccessToken()
  if (role !== "ops") {
    return null
  }
  return <B2BReconciliationPanelContent />
}

function B2BReconciliationPanelContent() {
  const [accountIdText, setAccountIdText] = useState("")
  const [severity, setSeverity] = useState<"" | "none" | "minor" | "major">("")
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null)
  const [note, setNote] = useState("")
  const [submittedFilters, setSubmittedFilters] = useState(false)

  const filters = useMemo(
    () => ({
      accountId: parseAccountId(accountIdText),
      severity: severity || undefined,
      limit: 50,
      offset: 0,
    }),
    [accountIdText, severity],
  )

  const issuesQuery = useB2BReconciliationIssues(filters, submittedFilters)
  const detailQuery = useB2BReconciliationIssueDetail(selectedIssueId, submittedFilters && selectedIssueId !== null)
  const actionMutation = useB2BReconciliationAction()
  const listError = issuesQuery.error as B2BReconciliationApiError | null
  const detailError = detailQuery.error as B2BReconciliationApiError | null
  const actionError = actionMutation.error as B2BReconciliationApiError | null
  const activeIssue = detailQuery.data?.issue

  const isLoading = issuesQuery.isPending || detailQuery.isPending
  const isEmpty =
    submittedFilters &&
    !isLoading &&
    !listError &&
    (issuesQuery.data?.items.length ?? 0) === 0

  const runAction = (action: ReconciliationAction) => {
    if (!selectedIssueId) return
    actionMutation.mutate(
      { issueId: selectedIssueId, action, note: note.trim() || undefined },
      {
        onSuccess: () => {
          void issuesQuery.refetch()
          void detailQuery.refetch()
        },
      },
    )
  }

  return (
    <section className="panel">
      <h2>Reconciliation B2B Ops</h2>
      <p>Compare usage mesure et facturation afin de detecter les ecarts avant impact client.</p>

      <label htmlFor="reco-account">Compte entreprise (optionnel)</label>
      <input
        id="reco-account"
        value={accountIdText}
        onChange={(event) => setAccountIdText(event.target.value)}
        placeholder="42"
      />

      <label htmlFor="reco-severity">Severite</label>
      <select
        id="reco-severity"
        value={severity}
        onChange={(event) => setSeverity(event.target.value as "" | "none" | "minor" | "major")}
      >
        <option value="">Toutes</option>
        <option value="major">major</option>
        <option value="minor">minor</option>
        <option value="none">none</option>
      </select>

      <button
        type="button"
        onClick={() => {
          setSubmittedFilters(true)
          void issuesQuery.refetch()
        }}
        disabled={issuesQuery.isFetching}
      >
        Charger la reconciliation
      </button>

      {isLoading ? <p aria-busy="true">Chargement reconciliation...</p> : null}
      {listError ? (
        <p role="alert">
          Erreur reconciliation liste: {listError.message} ({listError.code})
          {listError.requestId ? ` [request_id=${listError.requestId}]` : ""}
        </p>
      ) : null}
      {detailError ? (
        <p role="alert">
          Erreur reconciliation detail: {detailError.message} ({detailError.code})
          {detailError.requestId ? ` [request_id=${detailError.requestId}]` : ""}
        </p>
      ) : null}
      {isEmpty ? <p>Aucun ecart de reconciliation pour ces filtres.</p> : null}

      {issuesQuery.data && issuesQuery.data.items.length > 0 ? (
        <>
          <h3>Ecarts identifies ({issuesQuery.data.total})</h3>
          <ul className="chat-list">
            {issuesQuery.data.items.map((issue) => (
              <li key={issue.issue_id} className="chat-item">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedIssueId(issue.issue_id)
                  }}
                >
                  {describeIssue(issue)}
                </button>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {activeIssue ? (
        <>
          <h3>Detail ecart</h3>
          <ul className="chat-list">
            <li className="chat-item">Issue: {activeIssue.issue_id}</li>
            <li className="chat-item">Type: {activeIssue.mismatch_type}</li>
            <li className="chat-item">Delta units: {activeIssue.delta_units}</li>
            <li className="chat-item">Etat correction: {activeIssue.status}</li>
            <li className="chat-item">Trace source: usage_rows={(activeIssue.source_trace.usage_rows as number) ?? 0}</li>
          </ul>

          <label htmlFor="reco-note">Note action (optionnel)</label>
          <input
            id="reco-note"
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="commentaire ops"
          />

          <div>
            {activeIssue.recommended_actions.map((hint) => (
              <button
                key={hint.code}
                type="button"
                disabled={actionMutation.isPending}
                onClick={() => runAction(hint.code)}
              >
                {hint.label}
              </button>
            ))}
          </div>

          {actionMutation.isSuccess ? (
            <p>
              Action executee: {actionMutation.data.action} ({actionMutation.data.correction_state})
            </p>
          ) : null}
          {actionError ? (
            <p role="alert">
              Erreur action reconciliation: {actionError.message} ({actionError.code})
              {actionError.requestId ? ` [request_id=${actionError.requestId}]` : ""}
            </p>
          ) : null}
        </>
      ) : null}
    </section>
  )
}

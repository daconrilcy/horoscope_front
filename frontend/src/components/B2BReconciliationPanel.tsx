import { useMemo, useState } from "react"

import {
  B2BReconciliationApiError,
  type ReconciliationAction,
  type ReconciliationIssue,
  useB2BReconciliationAction,
  useB2BReconciliationIssueDetail,
  useB2BReconciliationIssues,
} from "../api/b2bReconciliation"
import { useTranslation } from "../i18n"

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
  return <B2BReconciliationPanelContent />
}

function B2BReconciliationPanelContent() {
  const t = useTranslation("admin").b2b.reconciliation
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
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      <label htmlFor="reco-account">{t.accountLabel}</label>
      <input
        id="reco-account"
        value={accountIdText}
        onChange={(event) => setAccountIdText(event.target.value)}
        placeholder="42"
      />

      <label htmlFor="reco-severity">{t.severityLabel}</label>
      <select
        id="reco-severity"
        value={severity}
        onChange={(event) => setSeverity(event.target.value as "" | "none" | "minor" | "major")}
      >
        <option value="">{t.severities.all}</option>
        <option value="major">{t.severities.major}</option>
        <option value="minor">{t.severities.minor}</option>
        <option value="none">{t.severities.none}</option>
      </select>

      <div className="action-row">
        <button
          type="button"
          onClick={() => {
            setSubmittedFilters(true)
            void issuesQuery.refetch()
          }}
          disabled={issuesQuery.isFetching}
        >
          {t.submit}
        </button>
      </div>

      {isLoading ? (
        <p aria-busy="true" className="state-line state-loading">
          {t.loading}
        </p>
      ) : null}
      {listError ? (
        <p role="alert" className="chat-error">
          {t.errorList(listError.message, listError.code)}
          {listError.requestId ? ` [request_id=${listError.requestId}]` : ""}
        </p>
      ) : null}
      {detailError ? (
        <p role="alert" className="chat-error">
          {t.errorDetail(detailError.message, detailError.code)}
          {detailError.requestId ? ` [request_id=${detailError.requestId}]` : ""}
        </p>
      ) : null}
      {isEmpty ? <p className="state-line state-empty">{t.empty}</p> : null}

      {issuesQuery.data && issuesQuery.data.items.length > 0 ? (
        <>
          <h3>{t.resultsTitle(issuesQuery.data.total)}</h3>
          <ul className="chat-list compact-list">
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
          <h3>{t.detailTitle}</h3>
          <ul className="chat-list compact-list">
            <li className="chat-item">Issue: {activeIssue.issue_id}</li>
            <li className="chat-item">Type: {activeIssue.mismatch_type}</li>
            <li className="chat-item">Delta unités: {activeIssue.delta_units}</li>
            <li className="chat-item">État correction: {activeIssue.status}</li>
            <li className="chat-item">Trace source: usage_rows={(activeIssue.source_trace.usage_rows as number) ?? 0}</li>
          </ul>

          <label htmlFor="reco-note">{t.noteLabel}</label>
          <input
            id="reco-note"
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="commentaire ops"
          />

          <div className="action-row">
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
            <p className="state-line state-success">
              {t.actionExecuted(actionMutation.data.action, actionMutation.data.correction_state)}
            </p>
          ) : null}
          {actionError ? (
            <p role="alert" className="chat-error">
              {t.errorAction(actionError.message, actionError.code)}
              {actionError.requestId ? ` [request_id=${actionError.requestId}]` : ""}
            </p>
          ) : null}
        </>
      ) : null}
    </section>
  )
}

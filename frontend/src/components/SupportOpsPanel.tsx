import { useState } from "react"

import { useOpsSearchUser, useOpsRollbackPersona } from "@api"
import { useTranslation } from "../i18n"

export function SupportOpsPanel() {
  const t = useTranslation("admin").b2b.support
  const [targetEmail, setTargetUser] = useState("")
  const supportContext = useOpsSearchUser(targetEmail)
  const rollbackPersona = useOpsRollbackPersona()

  return (
    <section className="panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      <label htmlFor="support-target-user">{t.targetUserLabel}</label>
      <div className="action-row">
        <input
          id="support-target-user"
          value={targetEmail}
          onChange={(event) => setTargetUser(event.target.value)}
          placeholder="user@example.com"
        />
        <button
          type="button"
          disabled={supportContext.isPending}
          onClick={() => supportContext.refetch()}
        >
          Search
        </button>
      </div>

      {supportContext.data && (
        <div className="support-results mt-6">
          <p className="state-line">{t.privacyRequests(supportContext.data.privacy_requests.length)}</p>
          <ul className="chat-list compact-list">
            {supportContext.data.privacy_requests.map((req: any) => (
              <li key={req.request_id} className="chat-item">
                {req.type} - {req.status} ({new Date(req.created_at).toLocaleDateString()})
              </li>
            ))}
          </ul>
          {supportContext.data.privacy_requests.length === 0 && (
            <p className="state-line state-empty">{t.noPrivacyRequests}</p>
          )}

          <h3>{t.recentAuditTitle}</h3>
          <ul className="chat-list compact-list">
            {supportContext.data.audit_log.map((entry: any) => (
              <li key={entry.event_id} className="chat-item">
                {entry.action} - {new Date(entry.timestamp).toLocaleString()}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="action-row mt-8 border-t pt-6">
        <button
          type="button"
          className="button-danger"
          onClick={() => rollbackPersona.mutate()}
          disabled={rollbackPersona.isPending}
        >
          Global System Rollback
        </button>
      </div>
    </section>
  )
}

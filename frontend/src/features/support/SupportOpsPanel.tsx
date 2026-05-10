// Panneau admin pour rechercher un utilisateur support et declencher les actions ops.
import { useState } from "react"

import { useRollbackOpsPersonaConfig } from "../../api/opsPersona"
import { type SupportUserContext, useOpsSearchUser } from "../../api/support"
import { useTranslation } from "../../i18n"

type PrivacyRequestView = SupportUserContext["privacy_requests"][number] & {
  type?: string
  created_at?: string
}

type AuditEventView = SupportUserContext["audit_events"][number] & {
  timestamp?: string
}

type SupportUserContextView = SupportUserContext & {
  audit_log?: AuditEventView[]
}

export function SupportOpsPanel() {
  const t = useTranslation("admin").b2b.support
  const [targetEmail, setTargetUser] = useState("")
  const supportContext = useOpsSearchUser(targetEmail)
  const rollbackPersona = useRollbackOpsPersonaConfig()
  const supportData = supportContext.data as SupportUserContextView | undefined
  const auditEvents = supportData?.audit_events ?? supportData?.audit_log ?? []

  return (
    <section className="app-panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      <label htmlFor="support-target-user">{t.targetUserLabel}</label>
      <div className="app-actions">
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

      {supportData && (
        <div className="support-results mt-6">
          <p className="app-state">{t.privacyRequests(supportData.privacy_requests.length)}</p>
          <ul className="chat-list app-list app-list--compact">
            {supportData.privacy_requests.map((req: PrivacyRequestView) => (
              <li key={req.request_id} className="chat-item">
                {req.type ?? req.request_kind} - {req.status} ({new Date(req.created_at ?? req.requested_at).toLocaleDateString()})
              </li>
            ))}
          </ul>
          {supportData.privacy_requests.length === 0 && (
            <p className="app-state app-state--empty">{t.noPrivacyRequests}</p>
          )}

          <h3>{t.recentAuditTitle}</h3>
          <ul className="chat-list app-list app-list--compact">
            {auditEvents.map((entry: AuditEventView) => (
              <li key={entry.event_id} className="chat-item">
                {entry.action} - {new Date(entry.timestamp ?? entry.created_at).toLocaleString()}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="app-actions mt-8 border-t pt-6">
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


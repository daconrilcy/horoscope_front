import { useState } from "react"

import { B2BUsageApiError, useB2BUsageSummary } from "@api"
import { useTranslation } from "../i18n"

export function B2BUsagePanel() {
  const t = useTranslation("admin").b2b.usage
  const [apiKey, setApiKey] = useState("")
  const usageSummary = useB2BUsageSummary()
  const error = usageSummary.error as B2BUsageApiError | null
  const isEmpty =
    usageSummary.isSuccess &&
    usageSummary.data.daily_consumed === 0 &&
    usageSummary.data.monthly_consumed === 0

  return (
    <section className="panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      <label htmlFor="b2b-usage-api-key">{t.apiKeyLabel}</label>
      <div className="action-row">
        <input
          id="b2b-usage-api-key"
          value={apiKey}
          onChange={(event) => setApiKey(event.target.value)}
          placeholder="b2b_xxxxx"
        />
        <button
          type="button"
          disabled={usageSummary.isPending}
          onClick={() => usageSummary.mutate(apiKey.trim())}
        >
          {t.submit}
        </button>
      </div>

      {usageSummary.isPending ? (
        <p aria-busy="true" className="state-line state-loading">
          {t.loading}
        </p>
      ) : null}
      {error ? (
        <p role="alert" className="chat-error">
          {t.error(error.message, error.code)}
          {error.requestId ? ` [request_id=${error.requestId}]` : ""}
        </p>
      ) : null}
      {isEmpty ? <p className="state-line state-empty">{t.empty}</p> : null}

      {usageSummary.data && !isEmpty ? (
        <ul className="chat-list compact-list">
          <li className="chat-item">
            {t.daily(usageSummary.data.daily_consumed, usageSummary.data.daily_limit, usageSummary.data.daily_remaining)}
          </li>
          <li className="chat-item">
            {t.monthly(usageSummary.data.monthly_consumed, usageSummary.data.monthly_limit, usageSummary.data.monthly_remaining)}
          </li>
          <li className="chat-item">{t.limitMode(usageSummary.data.limit_mode)}</li>
          <li className="chat-item">{t.blocking(usageSummary.data.blocked)}</li>
        </ul>
      ) : null}
    </section>
  )
}


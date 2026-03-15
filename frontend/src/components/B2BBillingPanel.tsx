import { useState } from "react"

import {
  B2BBillingApiError,
  useB2BBillingCycles,
  useB2BBillingLatestCycle,
} from "../api/b2bBilling"
import type { B2BBillingCycle } from "../api/b2bBilling"
import { useTranslation } from "../i18n"

function formatEuro(cents: number): string {
  return `${(cents / 100).toFixed(2)} EUR`
}

function formatErrorDetails(details: Record<string, unknown>): string {
  const entries = Object.entries(details)
  if (entries.length === 0) {
    return ""
  }
  return entries
    .map(([key, value]) => `${key}=${typeof value === "string" ? value : JSON.stringify(value)}`)
    .join(" | ")
}

export function B2BBillingPanel() {
  const t = useTranslation("admin").b2b.billing
  const [apiKey, setApiKey] = useState("")
  const [historyItems, setHistoryItems] = useState<B2BBillingCycle[]>([])
  const billingLatest = useB2BBillingLatestCycle()
  const billingHistory = useB2BBillingCycles()
  const latestError = billingLatest.error as B2BBillingApiError | null
  const historyError = billingHistory.error as B2BBillingApiError | null
  const error = latestError ?? historyError
  const isBusy = billingLatest.isPending || billingHistory.isPending
  const isEmpty = !isBusy && !error && billingLatest.isSuccess && billingLatest.data === null && historyItems.length === 0

  return (
    <section className="panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      <label htmlFor="b2b-billing-api-key">{t.apiKeyLabel}</label>
      <div className="action-row">
        <input
          id="b2b-billing-api-key"
          value={apiKey}
          onChange={(event) => setApiKey(event.target.value)}
          placeholder="b2b_xxxxx"
        />
        <button
          type="button"
          disabled={isBusy}
          onClick={async () => {
            const key = apiKey.trim()
            const latest = await billingLatest.mutateAsync(key)
            const history = await billingHistory.mutateAsync({ apiKey: key, limit: 10, offset: 0 })
            setHistoryItems(history.items)
            if (latest === null) {
              return
            }
          }}
        >
          {t.submit}
        </button>
      </div>

      {isBusy ? (
        <p aria-busy="true" className="state-line state-loading">
          {t.loading}
        </p>
      ) : null}
      {error ? (
        <p role="alert" className="chat-error">
          {t.error(error.message, error.code)}
          {error.requestId ? ` [request_id=${error.requestId}]` : ""}
          {Object.keys(error.details).length > 0 ? ` [details=${formatErrorDetails(error.details)}]` : ""}
        </p>
      ) : null}
      {isEmpty ? <p className="state-line state-empty">{t.empty}</p> : null}

      {billingLatest.data ? (
        <ul className="chat-list compact-list">
          <li className="chat-item">
            {t.period(billingLatest.data.period_start, billingLatest.data.period_end)}
          </li>
          <li className="chat-item">{t.plan(billingLatest.data.plan_display_name)}</li>
          <li className="chat-item">{t.fixed(formatEuro(billingLatest.data.fixed_amount_cents))}</li>
          <li className="chat-item">{t.variable(formatEuro(billingLatest.data.variable_amount_cents))}</li>
          <li className="chat-item">{t.total(formatEuro(billingLatest.data.total_amount_cents))}</li>
        </ul>
      ) : null}

      {historyItems.length > 0 ? (
        <>
          <h3>{t.historyTitle}</h3>
          <ul className="chat-list compact-list">
            {historyItems.map((item) => (
              <li key={item.cycle_id} className="chat-item">
                {item.period_start} {"->"} {item.period_end}: {formatEuro(item.total_amount_cents)}
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </section>
  )
}

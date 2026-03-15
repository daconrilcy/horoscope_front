import { useState } from "react"

import { B2BAstrologyApiError, useB2BWeeklyBySign } from "@api"
import { useTranslation } from "../i18n"

export function B2BAstrologyPanel() {
  const t = useTranslation("admin").b2b.astrology
  const [apiKey, setApiKey] = useState("")
  const weeklyBySign = useB2BWeeklyBySign()
  const error = weeklyBySign.error as B2BAstrologyApiError | null
  const isEmpty =
    weeklyBySign.isSuccess && Array.isArray(weeklyBySign.data?.items) && weeklyBySign.data.items.length === 0

  return (
    <section className="panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      <label htmlFor="b2b-api-key">{t.apiKeyLabel}</label>
      <div className="action-row">
        <input
          id="b2b-api-key"
          value={apiKey}
          onChange={(event) => setApiKey(event.target.value)}
          placeholder="b2b_xxxxx"
        />
        <button
          type="button"
          disabled={weeklyBySign.isPending}
          onClick={() => weeklyBySign.mutate(apiKey.trim())}
        >
          {t.submit}
        </button>
      </div>

      {weeklyBySign.isPending ? (
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

      {weeklyBySign.data && !isEmpty ? (
        <>
          <p className="state-line state-success">
            {t.apiVersion(weeklyBySign.data.api_version, weeklyBySign.data.reference_version)}
          </p>
          <ul className="chat-list compact-list">
            {weeklyBySign.data.items.map((item) => (
              <li key={item.sign_code} className="chat-item">
                <strong>{item.sign_name}</strong> ({item.sign_code}) - {item.weekly_summary}
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </section>
  )
}


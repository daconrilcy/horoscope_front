import { useState } from "react"

import { B2BAstrologyApiError, useB2BWeeklyBySign } from "../api/b2bAstrology"

export function B2BAstrologyPanel() {
  const [apiKey, setApiKey] = useState("")
  const weeklyBySign = useB2BWeeklyBySign()
  const error = weeklyBySign.error as B2BAstrologyApiError | null
  const isEmpty =
    weeklyBySign.isSuccess && Array.isArray(weeklyBySign.data?.items) && weeklyBySign.data.items.length === 0

  return (
    <section className="panel">
      <h2>API B2B Astrologie</h2>
      <p>Testez l'endpoint contractuel hebdomadaire par signe avec une clé API entreprise.</p>

      <label htmlFor="b2b-api-key">Clé API B2B</label>
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
          Récupérer weekly-by-sign
        </button>
      </div>

      {weeklyBySign.isPending ? (
        <p aria-busy="true" className="state-line state-loading">
          Chargement weekly-by-sign...
        </p>
      ) : null}
      {error ? (
        <p role="alert" className="chat-error">
          Erreur API B2B: {error.message} ({error.code})
          {error.requestId ? ` [request_id=${error.requestId}]` : ""}
        </p>
      ) : null}
      {isEmpty ? <p className="state-line state-empty">Aucun contenu astrologique disponible pour cette période.</p> : null}

      {weeklyBySign.data && !isEmpty ? (
        <>
          <p className="state-line state-success">
            Version API: {weeklyBySign.data.api_version} · Référence: {weeklyBySign.data.reference_version}
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

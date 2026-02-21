import { useState } from "react"

import { B2BUsageApiError, useB2BUsageSummary } from "../api/b2bUsage"

export function B2BUsagePanel() {
  const [apiKey, setApiKey] = useState("")
  const usageSummary = useB2BUsageSummary()
  const error = usageSummary.error as B2BUsageApiError | null
  const isEmpty =
    usageSummary.isSuccess &&
    usageSummary.data.daily_consumed === 0 &&
    usageSummary.data.monthly_consumed === 0

  return (
    <section className="panel">
      <h2>Consommation B2B</h2>
      <p>Consultez limites contractuelles et volumes utilises pour votre credential API.</p>

      <label htmlFor="b2b-usage-api-key">Cle API B2B</label>
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
        Recuperer le resume de consommation
      </button>

      {usageSummary.isPending ? <p aria-busy="true">Chargement consommation B2B...</p> : null}
      {error ? (
        <p role="alert">
          Erreur consommation B2B: {error.message} ({error.code})
          {error.requestId ? ` [request_id=${error.requestId}]` : ""}
        </p>
      ) : null}
      {isEmpty ? <p>Aucune consommation enregistree pour cette periode.</p> : null}

      {usageSummary.data && !isEmpty ? (
        <ul className="chat-list">
          <li className="chat-item">
            Quotidien: {usageSummary.data.daily_consumed}/{usageSummary.data.daily_limit} (
            {usageSummary.data.daily_remaining} restant)
          </li>
          <li className="chat-item">
            Mensuel: {usageSummary.data.monthly_consumed}/{usageSummary.data.monthly_limit} (
            {usageSummary.data.monthly_remaining} restant)
          </li>
          <li className="chat-item">Mode de limite: {usageSummary.data.limit_mode}</li>
          <li className="chat-item">Blocage actif: {usageSummary.data.blocked ? "oui" : "non"}</li>
        </ul>
      ) : null}
    </section>
  )
}

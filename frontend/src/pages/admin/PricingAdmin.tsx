import { useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "../../api/client"
import { getAccessTokenAuthHeader } from "../../utils/authToken"
import { detectLang } from "../../i18n/astrology"
import { adminTranslations } from "../../i18n/admin"
import { getLocale } from "../../utils/locale"

type BillingPlan = {
  code: string
  display_name: string
  monthly_price_cents: number
  currency: string
  daily_message_limit: number
  is_active: boolean
}

type PlansResponse = {
  data: BillingPlan[]
}

async function fetchPlans(): Promise<BillingPlan[]> {
  const response = await apiFetch(`${API_BASE_URL}/v1/billing/plans`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    throw new Error(`Erreur ${response.status}: ${response.statusText}`)
  }
  const json = (await response.json()) as PlansResponse
  return json.data
}

function formatPrice(cents: number, currency: string, locale: string): string {
  const amount = cents / 100
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: currency,
  }).format(amount)
}

export function PricingAdmin() {
  const lang = detectLang()
  const t = adminTranslations.pricing[lang]
  const locale = getLocale(lang)

  const plansQuery = useQuery({
    queryKey: ["admin", "billing-plans"],
    queryFn: fetchPlans,
    staleTime: 60_000,
  })

  return (
    <section className="pricing-admin" aria-labelledby="pricing-admin-title">
      <h2 id="pricing-admin-title" data-testid="pricing-admin-title">{t.title}</h2>
      <p>{t.description}</p>

      {plansQuery.isPending && (
        <p className="state-line state-loading" aria-busy="true">
          {t.loading}
        </p>
      )}

      {plansQuery.isError && (
        <div role="alert" className="chat-error">
          <p>{t.errorLoading}</p>
          <p className="error-detail">
            {plansQuery.error instanceof Error
              ? plansQuery.error.message
              : t.unknownError}
          </p>
          <p className="info-note">{t.apiNote}</p>
        </div>
      )}

      {plansQuery.data && plansQuery.data.length === 0 && (
        <p className="state-line state-empty">{t.emptyState}</p>
      )}

      {plansQuery.data && plansQuery.data.length > 0 && (
        <table className="pricing-table" aria-label={t.tableLabel}>
          <thead>
            <tr>
              <th scope="col">{t.colCode}</th>
              <th scope="col">{t.colName}</th>
              <th scope="col">{t.colPrice}</th>
              <th scope="col">{t.colLimit}</th>
              <th scope="col">{t.colStatus}</th>
            </tr>
          </thead>
          <tbody>
            {plansQuery.data.map((plan) => (
              <tr key={plan.code}>
                <td>{plan.code}</td>
                <td>{plan.display_name}</td>
                <td>{formatPrice(plan.monthly_price_cents, plan.currency, locale)}</td>
                <td>{plan.daily_message_limit}</td>
                <td>
                  <span className={plan.is_active ? "status-active" : "status-inactive"}>
                    {plan.is_active ? t.statusActive : t.statusInactive}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="admin-notice">
        <h3>{t.upcomingTitle}</h3>
        <ul>
          <li>{t.upcomingModify}</li>
          <li>{t.upcomingCreate}</li>
          <li>{t.upcomingActivate}</li>
        </ul>
        <p className="info-note">{t.upcomingNote}</p>
      </div>
    </section>
  )
}

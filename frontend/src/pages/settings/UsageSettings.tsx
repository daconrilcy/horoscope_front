import { useBillingQuota, type BillingApiError } from "../../api/billing"
import { detectLang, type AstrologyLang } from "../../i18n/astrology"
import { settingsTranslations } from "../../i18n/settings"
import { getLocale } from "../../utils/locale"

function getErrorMessage(error: BillingApiError | null, lang: AstrologyLang): string {
  const errorMessages = settingsTranslations.usageErrors

  if (!error) {
    return errorMessages.default[lang]
  }

  if (error.status === 0 || error.code === "network_error") {
    return errorMessages.network_error[lang]
  }

  if (error.status === 401 || error.code === "unauthorized") {
    return errorMessages.unauthorized[lang]
  }

  if (error.status >= 500) {
    return errorMessages.server_error[lang]
  }

  return error.message || errorMessages.default[lang]
}

export function UsageSettings() {
  const lang = detectLang()
  const t = settingsTranslations.usage[lang]
  const quota = useBillingQuota()

  const quotaError = quota.error as BillingApiError | null

  return (
    <section className="usage-settings">
      <h2 className="settings-section-title">{t.title}</h2>

      {quota.isLoading && (
        <p aria-busy="true" className="state-line state-loading">
          {t.loading}
        </p>
      )}

      {quota.isError && (
        <div role="alert" className="chat-error">
          <p>
            {t.error}: {getErrorMessage(quotaError, lang)}
          </p>
          <button type="button" onClick={() => void quota.refetch()}>
            {t.retry}
          </button>
        </div>
      )}

      {quota.data && (
        <div className="panel">
          <h3>{t.dailyUsage}</h3>
          <div className="usage-stats-grid">
            <div className="usage-stat-item">
              <span className="usage-stat-label">{t.messagesUsed}</span>
              <span className="usage-stat-value">{quota.data.consumed}</span>
            </div>
            <div className="usage-stat-item">
              <span className="usage-stat-label">{t.limit}</span>
              <span className="usage-stat-value">{quota.data.limit}</span>
            </div>
            <div className="usage-stat-item">
              <span className="usage-stat-label">{t.remaining}</span>
              <span className="usage-stat-value">{quota.data.remaining}</span>
            </div>
            {quota.data.reset_at && (
              <div className="usage-stat-item">
                <span className="usage-stat-label">{t.resetAt}</span>
                <span className="usage-stat-value">
                  {new Date(quota.data.reset_at).toLocaleTimeString(getLocale(lang))}
                </span>
              </div>
            )}
          </div>
          <div
            className="usage-progress-bar"
            role="progressbar"
            aria-label={t.dailyUsage}
            aria-valuenow={quota.data.consumed}
            aria-valuemin={0}
            aria-valuemax={quota.data.limit}
            style={
              {
                "--usage-progress":
                  quota.data.limit > 0
                    ? Math.min((quota.data.consumed / quota.data.limit) * 100, 100)
                    : 0,
              } as React.CSSProperties
            }
          >
            <div className="usage-progress-fill" />
          </div>
        </div>
      )}

      {!quota.isLoading && !quota.isError && !quota.data && (
        <p className="state-line state-empty">{t.noData}</p>
      )}
    </section>
  )
}

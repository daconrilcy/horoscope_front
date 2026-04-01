import { useChatEntitlementUsage, type BillingApiError } from "@api/billing"
import { detectLang, type AstrologyLang } from "@i18n/astrology"
import { settingsTranslations } from "@i18n/settings"
import { getLocale } from "@utils/locale"
import "./Settings.css"

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
  const quota = useChatEntitlementUsage()

  const quotaError = quota.error as BillingApiError | null

  return (
    <div className="usage-settings">
      <section className="settings-card">
        <h2 className="settings-section-title settings-section-title--decorated">
          {t.title}
        </h2>

        {quota.isLoading && (
          <p aria-busy="true" className="settings-save-feedback settings-save-feedback--saving">
            {t.loading}
          </p>
        )}

        {quota.isError && (
          <div role="alert" className="settings-save-feedback settings-save-feedback--error">
            <p>
              {t.error}: {getErrorMessage(quotaError, lang)}
            </p>
            <button type="button" className="settings-tab" onClick={() => void quota.refetch()}>
              {t.retry}
            </button>
          </div>
        )}

        {quota.data && (
          <>
            <h3 className="settings-section-title settings-section-title--usage">
              {t.dailyUsage}
            </h3>

            <div className="usage-stats-premium">
              <div className="usage-stat-item">
                <span className="usage-stat-label">
                  {quota.data.quota_key === "tokens" ? "Tokens utilisés" : t.messagesUsed}
                </span>
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
                  <span className="usage-stat-value usage-stat-value--time">
                    {new Date(quota.data.reset_at).toLocaleTimeString(getLocale(lang), { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              )}
            </div>

            <div className="settings-card--soft">
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
              <p className="default-astrologer-option__style usage-progress-label">
                {Math.round(Math.min((quota.data.consumed / quota.data.limit) * 100, 100))}% de votre quota {quota.data.quota_key === "tokens" ? "mensuel" : "quotidien"} utilisé
              </p>
            </div>
          </>
        )}

        {!quota.isLoading && !quota.isError && !quota.data && (
          <p className="state-line state-empty">{t.noData}</p>
        )}
      </section>
    </div>
  )
}

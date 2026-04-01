import {
  useChatEntitlementFeature,
  type BillingApiError,
  type ChatEntitlementUsageState,
} from "@api/billing"
import { detectLang, type AstrologyLang } from "@i18n/astrology"
import { settingsTranslations } from "@i18n/settings"
import { getLocale } from "@utils/locale"
import "./Settings.css"

function formatUsageNumber(value: number): string {
  return value.toLocaleString("fr-FR").replace(/[\u202f\u00a0]/g, " ")
}

function formatResetDate(value: string, lang: AstrologyLang): string {
  return new Intl.DateTimeFormat(getLocale(lang), {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value))
}

function formatUsageRatio(consumed: number, total: number, totalLabel: string): string {
  return `${formatUsageNumber(consumed)} tokens / ${formatUsageNumber(total)} tokens ${totalLabel}`
}

type UsageRowProps = {
  label: string
  consumed: number
  total: number
  totalLabel: string
  resetAtLabel: string
  resetAt: string | null
  lang: AstrologyLang
}

function UsageWaterlineRow({
  label,
  consumed,
  total,
  totalLabel,
  resetAtLabel,
  resetAt,
  lang,
}: UsageRowProps) {
  const safeMax = Math.max(total, 1)

  return (
    <article className="usage-waterline-row">
      <div className="usage-waterline-row__header">
        <h3 className="usage-waterline-row__title">{label}</h3>
      </div>
      <progress className="usage-waterline-row__meter" value={Math.min(consumed, safeMax)} max={safeMax}>
        {consumed}
      </progress>
      <div className="usage-waterline-row__meta">
        <p className="usage-waterline-row__detail">{formatUsageRatio(consumed, total, totalLabel)}</p>
        {resetAt && (
          <p className="usage-waterline-row__detail">
            {resetAtLabel} : {formatResetDate(resetAt, lang)}
          </p>
        )}
      </div>
    </article>
  )
}

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
  const chatFeature = useChatEntitlementFeature()

  const pageError = chatFeature.error as BillingApiError | null
  const isLoading = chatFeature.isLoading
  const isError = chatFeature.isError

  const usageRows: Array<{ key: string; label: string; data: ChatEntitlementUsageState }> =
    chatFeature.data == null
      ? []
      : chatFeature.data.usage_states
          .filter((state) => state.quota_key === "tokens")
          .map((state) => ({
            key: `${state.period_unit}:${state.period_value}`,
            label:
              state.period_unit === "day"
                ? t.day
                : state.period_unit === "week"
                  ? t.week
                  : state.period_unit === "month"
                    ? t.month
                    : state.period_unit,
            data: state,
          }))
  return (
    <div className="usage-settings">
      <section className="settings-card">
        <h2 className="settings-section-title settings-section-title--decorated">
          {t.title}
        </h2>

        {isLoading && (
          <p aria-busy="true" className="settings-save-feedback settings-save-feedback--saving">
            {t.loading}
          </p>
        )}

        {isError && (
          <div role="alert" className="settings-save-feedback settings-save-feedback--error">
            <p>
              {t.error}: {getErrorMessage(pageError, lang)}
            </p>
            <button
              type="button"
              className="settings-tab"
              onClick={() => {
                void chatFeature.refetch()
              }}
            >
              {t.retry}
            </button>
          </div>
        )}

        {chatFeature.data && (
          <>
            <h3 className="settings-section-title settings-section-title--usage">
              {t.dailyUsage}
            </h3>

            <div className="settings-card--soft usage-waterline-panel">
              <p className="default-astrologer-option__style usage-waterline-panel__hint">{t.resetHint}</p>
              <div className="usage-waterline-list">
                {usageRows.map((row) => (
                  <UsageWaterlineRow
                    key={row.key}
                    label={row.label}
                    consumed={row.data.used}
                    total={row.data.quota_limit}
                    totalLabel={t.totalLabel}
                    resetAtLabel={t.resetAt}
                    resetAt={row.data.window_end}
                    lang={lang}
                  />
                ))}
              </div>
            </div>
          </>
        )}

        {!isLoading && !isError && !chatFeature.data && (
          <p className="state-line state-empty">{t.noData}</p>
        )}
      </section>
    </div>
  )
}

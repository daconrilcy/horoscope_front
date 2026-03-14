import { detectLang } from "@i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import { type ConsultationPrecheckData } from "@api/consultations"

type ConsultationFallbackBannerProps = {
  precheck: ConsultationPrecheckData
}

export function ConsultationFallbackBanner({ precheck }: ConsultationFallbackBannerProps) {
  const lang = detectLang()

  if (precheck.status === "nominal") {
    return (
      <div className="consultation-banner consultation-banner--nominal">
        <span className="banner-icon">✨</span>
        <div className="banner-content">
          <p className="banner-title">{t("precision_high", lang)}</p>
          <p className="banner-text">{t("nominal_mode_desc", lang)}</p>
        </div>
      </div>
    )
  }

  if (precheck.status === "degraded") {
    return (
      <div className="consultation-banner consultation-banner--degraded">
        <span className="banner-icon">⚠️</span>
        <div className="banner-content">
          <p className="banner-title">{t(`precision_${precheck.precision_level}`, lang)}</p>
          <p className="banner-text">
            {t("degraded_mode_info", lang)}: {t(precheck.fallback_mode ?? "", lang)}
          </p>
        </div>
      </div>
    )
  }

  if (precheck.status === "blocked") {
    return (
      <div className="consultation-banner consultation-banner--blocked">
        <span className="banner-icon">🚫</span>
        <div className="banner-content">
          <p className="banner-title">{t("precision_blocked", lang)}</p>
          <p className="banner-text">
            {precheck.blocking_reasons.map(reason => t(reason, lang)).join(". ")}
          </p>
        </div>
      </div>
    )
  }

  return null
}




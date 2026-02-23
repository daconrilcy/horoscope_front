import { Link } from "react-router-dom"

import { useConsultation } from "../state/consultationStore"
import { detectLang } from "../i18n/astrology"
import { t } from "../i18n/consultations"
import { CONSULTATION_TYPES, CONTEXT_TRUNCATE_LENGTH, getConsultationTypeConfig } from "../types/consultation"
import { formatDate } from "../utils/formatDate"

export function ConsultationsPage() {
  const { state } = useConsultation()
  const lang = detectLang()

  return (
    <div className="panel consultations-page">
      <header className="consultations-page-header">
        <h1>{t("page_title", lang)}</h1>
        <p>{t("page_subtitle", lang)}</p>
      </header>

      <section className="consultations-types-section">
        <Link to="/consultations/new" className="btn consultations-cta">
          {t("start_consultation", lang)}
        </Link>

        <div className="consultations-types-preview">
          {CONSULTATION_TYPES.map((typeConfig) => (
            <Link
              key={typeConfig.id}
              to={`/consultations/new?type=${typeConfig.id}`}
              className="consultations-type-preview-card"
            >
              <span className="consultations-type-preview-icon" aria-hidden="true">
                {typeConfig.icon}
              </span>
              <span className="consultations-type-preview-label">
                {t(typeConfig.labelKey, lang)}
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section className="consultations-history-section" aria-live="polite">
        <h2>{t("history_title", lang)}</h2>
        {state.history.length === 0 ? (
          <div className="state-line state-empty">{t("no_history", lang)}</div>
        ) : (
          <ul className="consultations-history-list">
            {state.history.map((consultation) => {
              const typeConfig = getConsultationTypeConfig(consultation.type)
              return (
              <li key={consultation.id} className="consultations-history-item">
                <Link
                  to={`/consultations/result?id=${consultation.id}`}
                  className="consultations-history-link"
                >
                  <span className="consultations-history-icon" aria-hidden="true">
                    {typeConfig?.icon}
                  </span>
                  <div className="consultations-history-info">
                    <span className="consultations-history-type">
                      {t(typeConfig?.labelKey ?? "", lang)}
                    </span>
                    <span className="consultations-history-date">
                      {formatDate(consultation.createdAt, lang)}
                    </span>
                  </div>
                  <span className="consultations-history-context">
                    {consultation.context.length > CONTEXT_TRUNCATE_LENGTH
                      ? `${consultation.context.slice(0, CONTEXT_TRUNCATE_LENGTH)}...`
                      : consultation.context}
                  </span>
                </Link>
              </li>
              )
            })}
          </ul>
        )}
      </section>
    </div>
  )
}

import { Link } from "react-router-dom"
import { useConsultations } from "@hooks/useConsultations"
import { detectLang } from "../i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import { CONTEXT_TRUNCATE_LENGTH, getConsultationTypeConfig } from "../types/consultation"
import { formatDate } from "../utils/formatDate"
import { PageLayout } from "../layouts"
import { useConsultationCatalogue } from "../api/consultations"

export function ConsultationsPage() {
  const { history, isLoading: isHistoryLoading } = useConsultations()
  const { data: catalogue, isLoading: isCatalogueLoading } = useConsultationCatalogue()
  const lang = detectLang()

  return (
    <PageLayout className="consultations-page premium-page-layout">
      <div className="premium-hero-section">
        <Link to="/dashboard" className="premium-back-link">
          <span className="premium-back-icon">←</span>
          {t("back_to_dashboard", lang)}
        </Link>
        <h1 className="premium-hero-title">{t("page_title", lang)}</h1>
        <p className="premium-hero-subtitle">{t("page_subtitle", lang)}</p>
      </div>

      <section className="consultations-catalogue-section">
        {isCatalogueLoading ? (
          <div className="premium-loading-state">
            <div className="premium-spinner"></div>
            <span>{t("loading_catalogue", lang)}</span>
          </div>
        ) : (
          <div className="consultation-cards-container">
            {catalogue?.items.map((item) => (
              <Link
                key={item.key}
                to={`/consultations/new?type=${item.key}`}
                className="consultation-card-premium"
              >
                <div className="consultation-card-premium-icon" aria-hidden="true">
                  {item.icon_ref}
                </div>
                <div className="consultation-card-premium-main">
                  <h3 className="consultation-card-premium-title">{item.title}</h3>
                  <p className="consultation-card-premium-subtitle">{item.subtitle}</p>
                  <div className="consultation-card-premium-tags">
                    {item.metadata_config.tags?.map((tag: string) => (
                      <span key={tag} className="consultation-premium-tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="consultation-card-premium-action">
                  <span className="premium-cta-inline">{t("choose_consultation", lang)}</span>
                </div>
              </Link>
            ))}

            {/* Fallback card if needed or generic start */}
            <Link
              to="/consultations/new"
              className="consultation-card-premium consultation-card-premium--alt"
            >
              <div className="consultation-card-premium-icon" aria-hidden="true">
                ✨
              </div>
              <div className="consultation-card-premium-main">
                <h3 className="consultation-card-premium-title">{t("no_preference_title", lang)}</h3>
                <p className="consultation-card-premium-subtitle">
                  {t("no_preference_subtitle", lang)}
                </p>
              </div>
              <div className="consultation-card-premium-action">
                <span className="premium-cta-inline">{t("start_now", lang)}</span>
              </div>
            </Link>
          </div>
        )}
      </section>

      <section className="consultations-history-section-premium" aria-live="polite">
        <h2 className="premium-section-title">{t("history_title", lang)}</h2>
        {isHistoryLoading ? (
          <div className="premium-loading-state-inline">{t("loading", lang)}</div>
        ) : history.length === 0 ? (
          <div className="premium-empty-state-inline">{t("no_history", lang)}</div>
        ) : (
          <div className="consultations-history-list-premium">
            {history.map((consultation) => {
              const typeConfig = getConsultationTypeConfig(consultation.type)
              return (
                <Link
                  key={consultation.id}
                  to={`/consultations/result?id=${consultation.id}`}
                  className="consultation-history-card-premium"
                >
                  <div className="consultation-history-card-header">
                    <span className="consultation-history-card-icon" aria-hidden="true">
                      {typeConfig?.icon}
                    </span>
                    <div className="consultation-history-card-meta">
                      <span className="consultation-history-card-type">
                        {t(typeConfig?.labelKey ?? "", lang)}
                      </span>
                      <span className="consultation-history-card-date">
                        {formatDate(consultation.createdAt, lang)}
                      </span>
                    </div>
                  </div>
                  <p className="consultation-history-card-context">
                    {consultation.context.length > CONTEXT_TRUNCATE_LENGTH
                      ? `${consultation.context.slice(0, CONTEXT_TRUNCATE_LENGTH)}...`
                      : consultation.context}
                  </p>
                </Link>
              )
            })}
          </div>
        )}
      </section>
    </PageLayout>
  )
}

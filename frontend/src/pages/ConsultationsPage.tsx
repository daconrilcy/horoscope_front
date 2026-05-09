import { Link } from "react-router-dom"
import { useConsultations } from "@hooks/useConsultations"
import { detectLang } from "../i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import { CONTEXT_TRUNCATE_LENGTH, getConsultationTypeConfig } from "../types/consultation"
import { formatDate } from "../utils/formatDate"
import { PageLayout } from "../layouts"
import { useConsultationCatalogue } from "../api/consultations"
import { useFeatureAccess } from "../hooks/useEntitlementSnapshot"
import { UpgradeCTA } from "../components/ui"

function ConsultationCatalogueCard({
  title,
  subtitle,
  icon,
  tags,
  to,
  actionLabel,
  isLocked,
  ctaLabel,
}: {
  title: string
  subtitle: string
  icon: string
  tags?: string[]
  to: string
  actionLabel: string
  isLocked: boolean
  ctaLabel: string
}) {
  const cardContent = (
    <>
      <div className="activity-card-premium-icon" aria-hidden="true">
        {icon}
      </div>
      <div className="activity-card-premium-main">
        <h3 className="activity-card-premium-title">{title}</h3>
        <p className="activity-card-premium-subtitle">{subtitle}</p>
        {tags && tags.length > 0 ? (
          <div className="activity-card-premium-tags cluster">
            {tags.map((tag) => (
              <span key={tag} className="activity-premium-tag">
                {tag}
              </span>
            ))}
          </div>
        ) : null}
      </div>
      <div className="activity-card-premium-action">
        {isLocked ? (
          <UpgradeCTA
            featureCode="thematic_consultation"
            variant="button"
            to="/settings/subscription"
            label={ctaLabel}
          />
        ) : (
          <span className="premium-cta-inline">{actionLabel}</span>
        )}
      </div>
    </>
  )

  if (isLocked) {
    return (
      <div className="activity-card-premium activity-card-premium--locked select-card">
        {cardContent}
      </div>
    )
  }

  return (
    <Link to={to} className="activity-card-premium select-card">
      {cardContent}
    </Link>
  )
}

export function ConsultationsPage() {
  const { history, isLoading: isHistoryLoading } = useConsultations()
  const { data: catalogue, isLoading: isCatalogueLoading } = useConsultationCatalogue()
  const featureAccess = useFeatureAccess("thematic_consultation")
  const lang = detectLang()
  const isThematicConsultationLocked = featureAccess?.granted === false
  const upgradeToBasicLabel =
    lang === "fr"
      ? "Passer à Basic pour accéder aux consultations thématiques"
      : "Upgrade to Basic for thematic consultations"

  return (
    <PageLayout className="activities-page premium-page-layout">
      <div className="premium-hero-section">
        <Link to="/dashboard" className="premium-back-link">
          <span className="premium-back-icon">←</span>
          {t("back_to_overview", lang)}
        </Link>
        <h1 className="premium-hero-title">{t("page_title", lang)}</h1>
        <p className="premium-hero-subtitle">{t("page_subtitle", lang)}</p>
      </div>

      <section className="activities-catalogue-section">
        {isCatalogueLoading ? (
          <div className="premium-loading-state">
            <div className="premium-spinner"></div>
            <span>{t("loading_catalogue", lang)}</span>
          </div>
        ) : (
          <div className="activity-cards-container">
            {catalogue?.items.map((item) => (
              <ConsultationCatalogueCard
                key={item.key}
                title={item.title}
                subtitle={item.subtitle}
                icon={item.icon_ref}
                tags={item.metadata_config.tags}
                to={`/consultations/new?type=${item.key}`}
                actionLabel={t("choose_consultation", lang)}
                isLocked={isThematicConsultationLocked}
                ctaLabel={upgradeToBasicLabel}
              />
            ))}

            <ConsultationCatalogueCard
              title={t("no_preference_title", lang)}
              subtitle={t("no_preference_subtitle", lang)}
              icon="✨"
              to="/consultations/new"
              actionLabel={t("start_now", lang)}
              isLocked={isThematicConsultationLocked}
              ctaLabel={upgradeToBasicLabel}
            />
          </div>
        )}
      </section>

      <section className="activities-history-section-premium" aria-live="polite">
        <h2 className="premium-section-title">{t("history_title", lang)}</h2>
        {isHistoryLoading ? (
          <div className="premium-loading-state-inline">{t("loading", lang)}</div>
        ) : history.length === 0 ? (
          <div className="premium-empty-state-inline">{t("no_history", lang)}</div>
        ) : (
          <div className="activities-history-list-premium">
            {history.map((session) => {
              const typeConfig = getConsultationTypeConfig(session.type)
              return (
                <Link
                  key={session.id}
                  to={`/consultations/result?id=${session.id}`}
                  className="activity-history-card-premium"
                >
                  <div className="activity-history-card-header">
                    <span className="activity-history-card-icon" aria-hidden="true">
                      {typeConfig?.icon}
                    </span>
                    <div className="activity-history-card-meta">
                      <span className="activity-history-card-type">
                        {t(typeConfig?.labelKey ?? "", lang)}
                      </span>
                      <span className="activity-history-card-date">
                        {formatDate(session.createdAt, lang)}
                      </span>
                    </div>
                  </div>
                  <p className="activity-history-card-context">
                    {session.context.length > CONTEXT_TRUNCATE_LENGTH
                      ? `${session.context.slice(0, CONTEXT_TRUNCATE_LENGTH)}...`
                      : session.context}
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

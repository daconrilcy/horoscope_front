import { useNavigate, useParams } from "react-router-dom"

import { useAstrologer } from "../api/astrologers"
import { AstrologerProfileHeader } from "../features/astrologers"
import { detectLang } from "../i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import { PageLayout } from "../layouts"

export function AstrologerProfilePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: profile, isPending, error } = useAstrologer(id)
  const lang = detectLang()

  const handleBack = () => {
    navigate("/astrologers")
  }

  if (isPending) {
    return (
      <PageLayout className="panel">
        <div className="astrologer-profile-page-loading">
          {t("loading", lang)}
        </div>
      </PageLayout>
    )
  }

  if (error) {
    return (
      <PageLayout className="panel">
        <div className="astrologer-profile-page-error">
          <span className="astrologer-profile-page-error-icon" role="img" aria-label={t("aria_error", lang)}>
            ⚠️
          </span>
          <h2>{t("error_loading", lang)}</h2>
          <button onClick={handleBack} type="button">
            {t("back_to_catalogue", lang)}
          </button>
        </div>
      </PageLayout>
    )
  }

  if (!profile) {
    return (
      <PageLayout className="panel">
        <div className="astrologer-profile-page-not-found">
          <span className="astrologer-profile-page-not-found-icon" role="img" aria-label={t("aria_not_found", lang)}>
            🔍
          </span>
          <h2>{t("profile_not_found", lang)}</h2>
          <p>{t("profile_not_found_description", lang)}</p>
          <button onClick={handleBack} type="button">
            {t("back_to_catalogue", lang)}
          </button>
        </div>
      </PageLayout>
    )
  }

  return (
    <PageLayout className="panel">
      <button
        className="astrologer-profile-page-back"
        onClick={handleBack}
        type="button"
      >
        <span aria-hidden="true">←</span> {t("back_to_catalogue", lang)}
      </button>
      <AstrologerProfileHeader
        profile={profile}
        onStartConversation={() => navigate(`/chat?astrologerId=${encodeURIComponent(profile.id)}`)}
      />
    </PageLayout>
  )
}


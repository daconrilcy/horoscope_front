import { useState } from "react"
import type { AstrologerProfile } from "../../../api/astrologers"
import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/astrologers"

type AstrologerProfileHeaderProps = {
  profile: AstrologerProfile
  onStartConversation: () => void
}

export function AstrologerProfileHeader({
  profile,
  onStartConversation,
}: AstrologerProfileHeaderProps) {
  const [imgError, setImgError] = useState(false)
  const lang = detectLang()
  const showImage = profile.avatar_url && !imgError

  return (
    <header className="astrologer-profile-header">
      <div className="astrologer-profile-header-top">
        <div className="astrologer-profile-avatar">
          {showImage ? (
            <img
              src={profile.avatar_url}
              alt={`${t("avatar_alt", lang)} ${profile.name}`}
              className="astrologer-profile-avatar-img"
              onError={() => setImgError(true)}
            />
          ) : (
            <span className="astrologer-profile-avatar-icon" aria-hidden="true">
              ✨
            </span>
          )}
        </div>
        <div className="astrologer-profile-info">
          <h1 className="astrologer-profile-name">{profile.name}</h1>
          <p className="astrologer-profile-style">{profile.style}</p>
          <p className="astrologer-profile-experience">
            {profile.experience_years} {t("years_experience", lang)}
          </p>
        </div>
      </div>

      <div className="astrologer-profile-meta">
        <div className="astrologer-profile-specialties">
          <h3>{t("specialties", lang)}</h3>
          <div className="astrologer-profile-tags">
            {profile.specialties.map((specialty) => (
              <span key={specialty} className="astrologer-profile-tag">
                {specialty}
              </span>
            ))}
          </div>
        </div>

        <div className="astrologer-profile-languages">
          <h3>{t("languages", lang)}</h3>
          <p>{profile.languages.join(", ")}</p>
        </div>
      </div>

      <div className="astrologer-profile-bio">
        <h3>{t("about", lang)}</h3>
        <p>{profile.bio_full}</p>
      </div>

      <div className="astrologer-profile-actions">
        <button
          className="astrologer-profile-cta"
          onClick={onStartConversation}
          type="button"
        >
          {t("start_conversation", lang)}
        </button>
      </div>
    </header>
  )
}

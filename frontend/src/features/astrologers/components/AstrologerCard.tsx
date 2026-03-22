import { useState } from "react"
import type { Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"

type AstrologerCardProps = {
  astrologer: Astrologer
  onClick: () => void
}

export function AstrologerCard({ astrologer, onClick }: AstrologerCardProps) {
  const [imgError, setImgError] = useState(false)
  const lang = detectLang()
  const showImage = astrologer.avatar_url && !imgError
  const fullName = [astrologer.first_name, astrologer.last_name].filter(Boolean).join(" ") || astrologer.name

  return (
    <button
      className="astrologer-card"
      onClick={onClick}
      type="button"
      aria-label={`${t("view_profile_aria", lang)} ${fullName}`}
    >
      <div className="astrologer-card-avatar">
        {showImage ? (
          <img
            src={astrologer.avatar_url || ""}
            alt={`${t("avatar_alt", lang)} ${fullName}`}
            className="astrologer-card-avatar-img"
            onError={() => setImgError(true)}
          />
        ) : (
          <span className="astrologer-card-avatar-icon" aria-hidden="true">
            ✨
          </span>
        )}
      </div>
      <span className="astrologer-card-name">{fullName}</span>
      <p className="astrologer-card-style">{astrologer.style}</p>
      <div className="astrologer-card-specialties">
        {astrologer.specialties.slice(0, 3).map((specialty) => (
          <span key={specialty} className="astrologer-card-tag">
            {specialty}
          </span>
        ))}
      </div>
      <p className="astrologer-card-bio">{astrologer.bio_short}</p>
    </button>
  )
}




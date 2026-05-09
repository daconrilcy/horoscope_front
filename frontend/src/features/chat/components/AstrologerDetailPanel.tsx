import { useState } from "react"
import type { AstrologerProfile } from "@api/astrologers"
import type { AstrologyLang } from "@i18n/astrology"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"

type AstrologerDetailPanelProps = {
  conversationId: number | null
  selectedAstrologer?: AstrologerProfile | null
}

const DEFAULT_SPECIALTIES_FR = [
  "Thèmes nataux",
  "Transits planétaires",
  "Guidance quotidienne",
  "Compatibilité",
]

const DEFAULT_SPECIALTIES_EN = [
  "Birth charts",
  "Planetary transits",
  "Daily guidance",
  "Compatibility",
]

const DEFAULT_SPECIALTIES_ES = [
  "Cartas natales",
  "Tránsitos planetarios",
  "Guía diaria",
  "Compatibilidad",
]

function getDefaultSpecialties(lang: AstrologyLang): string[] {
  switch (lang) {
    case "en":
      return DEFAULT_SPECIALTIES_EN
    case "es":
      return DEFAULT_SPECIALTIES_ES
    default:
      return DEFAULT_SPECIALTIES_FR
  }
}

export function AstrologerDetailPanel({
  conversationId,
  selectedAstrologer,
}: AstrologerDetailPanelProps) {
  const [imgError, setImgError] = useState(false)
  const lang = detectLang()

  const name = selectedAstrologer?.name ?? t("your_astrologer", lang)
  const bio = selectedAstrologer?.bio_full ?? selectedAstrologer?.bio_short ?? t("default_bio", lang)
  const specialties = selectedAstrologer?.specialties ?? getDefaultSpecialties(lang)
  const avatarUrl = selectedAstrologer?.avatar_url
  const showImage = avatarUrl && !imgError

  return (
    <aside className="person-panel">
      <div className="person-panel-header">
        <div className="person-panel-avatar">
          {showImage ? (
            <img
              src={avatarUrl}
              alt={`${t("avatar_alt", lang)} ${name}`}
              className="person-panel-avatar-img"
              onError={() => setImgError(true)}
            />
          ) : (
            <span
              className="person-panel-avatar-icon"
              aria-hidden="true"
            >
              ✨
            </span>
          )}
        </div>
        <h3 className="person-panel-name">{name}</h3>
        <p className="person-panel-status">{t("online", lang)}</p>
      </div>

      <div className="person-panel-info">
        <h4>{t("about", lang)}</h4>
        <p>{bio}</p>
      </div>

      <div className="person-panel-specialties">
        <h4>{t("specialties", lang)}</h4>
        <ul>
          {specialties.map((specialty) => (
            <li key={specialty}>{specialty}</li>
          ))}
        </ul>
      </div>

      {conversationId && (
        <div className="person-panel-conversation">
          <h4>{t("this_conversation", lang)}</h4>
          <p className="person-panel-conversation-id">
            #{conversationId}
          </p>
        </div>
      )}
    </aside>
  )
}




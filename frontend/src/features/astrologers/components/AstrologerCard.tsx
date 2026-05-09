import { useState } from "react"
import type { Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"

type AstrologerCardProps = {
  expert: Astrologer
  featured?: boolean
  isDefault?: boolean
  onClick: () => void
}

function getAstrologerTheme(expert: Astrologer): string {
  const firstName = expert.first_name.toLowerCase()
  if (firstName === "étienne" || firstName === "etienne") return "etienne"
  if (firstName === "luna") return "luna"
  if (firstName === "nox") return "nox"
  if (firstName === "orion") return "orion"
  if (firstName === "atlas") return "atlas"
  if (firstName === "sélène" || firstName === "selene") return "selene"
  return "default"
}

function getAstrologerIcon(theme: string): string {
  switch (theme) {
    case "etienne":
      return "✦"
    case "luna":
      return "❤"
    case "nox":
      return "☽"
    case "orion":
      return "✺"
    case "atlas":
      return "⚡"
    case "selene":
      return "☼"
    default:
      return "✦"
  }
}

function getFeaturedBadge(expert: Astrologer): string {
  const firstName = expert.first_name.toLowerCase()
  if (firstName === "orion") return "Analyse precise"
  if (firstName === "étienne" || firstName === "etienne") return "Debutants"
  if (firstName === "atlas") return "Decisions"
  if (firstName === "luna") return "Relationnel"
  if (firstName === "nox") return "Profondeur"
  if (firstName === "sélène" || firstName === "selene") return "Cycles"
  return expert.style
}

function getProviderBadgeLabel(providerType: Astrologer["provider_type"], lang: ReturnType<typeof detectLang>) {
  return providerType === "real" ? t("provider_type_real", lang) : t("provider_type_ai", lang)
}

export function AstrologerCard({ expert, featured = false, isDefault, onClick }: AstrologerCardProps) {
  const [imgError, setImgError] = useState(false)
  const lang = detectLang()
  const showImage = expert.avatar_url && !imgError
  const fullName = [expert.first_name, expert.last_name].filter(Boolean).join(" ") || expert.name
  const theme = getAstrologerTheme(expert)
  const icon = getAstrologerIcon(theme)
  const featuredBadge = getFeaturedBadge(expert)
  const providerBadgeLabel = getProviderBadgeLabel(expert.provider_type, lang)
  const providerBadgeClassName =
    expert.provider_type === "real"
      ? "person-card-provider-badge person-card-provider-badge--real"
      : "person-card-provider-badge person-card-provider-badge--ia"

  return (
    <button
      className={`person-card ${featured ? "person-card--featured" : ""}`}
      onClick={onClick}
      type="button"
      aria-label={`${t("view_profile_aria", lang)} ${fullName}`}
      data-theme={theme}
    >
      <div className="person-card-orbit person-card-orbit--one" aria-hidden="true" />
      <div className="person-card-orbit person-card-orbit--two" aria-hidden="true" />
      <div className="person-card-topline">
        <span className="person-card-icon" aria-hidden="true">{icon}</span>
        <div className="person-card-badge-stack">
          {isDefault && (
            <span className="person-default-badge">
              {t("your_default", lang)}
            </span>
          )}
          <span className={providerBadgeClassName}>{providerBadgeLabel}</span>
          {featured && <span className="person-card-featured-badge">{featuredBadge}</span>}
        </div>
      </div>
      <div className="person-card-avatar">
        {showImage ? (
          <img
            src={expert.avatar_url || ""}
            alt={`${t("avatar_alt", lang)} ${fullName}`}
            className="person-card-avatar-img"
            onError={() => setImgError(true)}
          />
        ) : (
          <span className="person-card-avatar-icon" aria-hidden="true">
            ✨
          </span>
        )}
      </div>
      <span className="person-card-name">{fullName}</span>
      <span className="person-card-display-name">{expert.name}</span>
      <p className="person-card-style">{expert.style}</p>
      <div className="person-card-divider" aria-hidden="true" />
      <div className="person-card-specialties">
        {expert.specialties.slice(0, 3).map((specialty) => (
          <span key={specialty} className="person-card-tag">
            {specialty}
          </span>
        ))}
      </div>
      <p className="person-card-bio">{expert.bio_short}</p>
    </button>
  )
}




import { useState } from "react"
import type { Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"

type AstrologerCardProps = {
  astrologer: Astrologer
  featured?: boolean
  onClick: () => void
}

function getAstrologerTheme(astrologer: Astrologer): string {
  const firstName = astrologer.first_name.toLowerCase()
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

function getFeaturedBadge(astrologer: Astrologer): string {
  const firstName = astrologer.first_name.toLowerCase()
  if (firstName === "orion") return "Analyse precise"
  if (firstName === "étienne" || firstName === "etienne") return "Debutants"
  if (firstName === "atlas") return "Decisions"
  if (firstName === "luna") return "Relationnel"
  if (firstName === "nox") return "Profondeur"
  if (firstName === "sélène" || firstName === "selene") return "Cycles"
  return astrologer.style
}

export function AstrologerCard({ astrologer, featured = false, onClick }: AstrologerCardProps) {
  const [imgError, setImgError] = useState(false)
  const lang = detectLang()
  const showImage = astrologer.avatar_url && !imgError
  const fullName = [astrologer.first_name, astrologer.last_name].filter(Boolean).join(" ") || astrologer.name
  const theme = getAstrologerTheme(astrologer)
  const icon = getAstrologerIcon(theme)
  const featuredBadge = getFeaturedBadge(astrologer)

  return (
    <button
      className={`astrologer-card ${featured ? "astrologer-card--featured" : ""}`}
      onClick={onClick}
      type="button"
      aria-label={`${t("view_profile_aria", lang)} ${fullName}`}
      data-theme={theme}
    >
      <div className="astrologer-card-orbit astrologer-card-orbit--one" aria-hidden="true" />
      <div className="astrologer-card-orbit astrologer-card-orbit--two" aria-hidden="true" />
      <div className="astrologer-card-topline">
        <span className="astrologer-card-icon" aria-hidden="true">{icon}</span>
        {featured && <span className="astrologer-card-featured-badge">{featuredBadge}</span>}
      </div>
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
      <span className="astrologer-card-alias">{astrologer.name}</span>
      <p className="astrologer-card-style">{astrologer.style}</p>
      <div className="astrologer-card-divider" aria-hidden="true" />
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




// Rend une carte catalogue actionnable avec une hierarchie de choix identity-first.
import { useState } from "react"
import type { Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import {
  getAstrologerBenefitKey,
  getAstrologerFeaturedBadgeKey,
  getAstrologerIcon,
  getAstrologerTheme,
} from "../astrologerPositioning"

type AstrologerCardProps = {
  expert: Astrologer
  isDefault?: boolean
  isIntentMatch?: boolean
  onClick: () => void
  onStart?: () => void
  showProfileCta?: boolean
}

/** Localise le libelle du type de fournisseur affiche comme metadata secondaire. */
function getProviderBadgeLabel(providerType: Astrologer["provider_type"], lang: ReturnType<typeof detectLang>) {
  return providerType === "real" ? t("provider_type_real", lang) : t("provider_type_ai", lang)
}

/** Rend une carte catalogue avec decision claire, action primaire et profil secondaire. */
export function AstrologerCard({
  expert,
  isDefault,
  isIntentMatch = false,
  onClick,
  onStart,
  showProfileCta = false,
}: AstrologerCardProps) {
  const [imgError, setImgError] = useState(false)
  const lang = detectLang()
  const showImage = expert.avatar_url && !imgError
  const fullName = [expert.first_name, expert.last_name].filter(Boolean).join(" ") || expert.name
  const showDisplayName = expert.name.trim().toLowerCase() !== fullName.trim().toLowerCase()
  const theme = getAstrologerTheme(expert)
  const icon = getAstrologerIcon(theme)
  const featuredBadge = t(getAstrologerFeaturedBadgeKey(expert), lang)
  const benefitCopy = t(getAstrologerBenefitKey(expert), lang)
  const providerBadgeLabel = getProviderBadgeLabel(expert.provider_type, lang)
  const cardClassName = [
    "person-card",
    isDefault ? "person-card--recommended" : "",
    isIntentMatch ? "person-card--matched" : "",
  ].filter(Boolean).join(" ")
  const providerBadgeClassName =
    expert.provider_type === "real"
      ? "person-card-provider-badge person-card-provider-badge--real"
      : "person-card-provider-badge person-card-provider-badge--ia"
  const startLabel = t("start_with_guide", lang).replace("{name}", expert.first_name)

  return (
    <article
      className={cardClassName}
      data-theme={theme}
    >
      <div className="person-card-orbit person-card-orbit--one" aria-hidden="true" />
      <div className="person-card-orbit person-card-orbit--two" aria-hidden="true" />
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
      {isDefault && (
        <span className="person-default-badge person-default-badge--recommended">
          {t("your_default", lang)}
        </span>
      )}
      <span className="person-card-name">{fullName}</span>
      {showDisplayName && <span className="person-card-display-name">{expert.name}</span>}
      <p className="person-card-style">{expert.style}</p>
      <p className="person-card-benefit">{benefitCopy}</p>
      <div className="person-card-topline">
        <span className="person-card-icon" aria-hidden="true">{icon}</span>
        <div className="person-card-badge-stack">
          <span className="person-card-featured-badge">{featuredBadge}</span>
          <span className={providerBadgeClassName}>{providerBadgeLabel}</span>
          {isIntentMatch && (
            <span className="person-card-match-badge">
              {t("intent_match_badge", lang)}
            </span>
          )}
        </div>
      </div>
      <div className="person-card-divider" aria-hidden="true" />
      <div className="person-card-specialties">
        {expert.specialties.slice(0, 3).map((specialty) => (
          <span key={specialty} className="person-card-tag">
            {specialty}
          </span>
        ))}
      </div>
      <p className="person-card-bio">{expert.bio_short}</p>
      {showProfileCta && (
        <div className="person-card-actions">
          {onStart && (
            <button
              type="button"
              className="person-card-primary-cta"
              onClick={onStart}
            >
              {startLabel}
            </button>
          )}
          <button
            type="button"
            className="person-card-secondary-cta"
            aria-label={`${t("view_profile_aria", lang)} ${fullName}`}
            onClick={onClick}
          >
            {t("view_profile_cta", lang)}
          </button>
        </div>
      )}
    </article>
  )
}




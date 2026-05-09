import type { Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import { AstrologerCard } from "./AstrologerCard"

type AstrologerGridProps = {
  experts: Astrologer[]
  onSelectAstrologer: (expert: Astrologer) => void
  defaultAstrologerId?: string | null
}

export function AstrologerGrid({ experts, onSelectAstrologer, defaultAstrologerId }: AstrologerGridProps) {
  const lang = detectLang()

  if (experts.length === 0) {
    return (
      <div className="person-grid-empty">
        <span className="person-grid-empty-icon" role="img" aria-label={t("aria_star", lang)}>
          ⭐
        </span>
        <p>{t("empty_state", lang)}</p>
      </div>
    )
  }

  return (
    <div className="person-grid">
      {experts.map((expert, index) => (
        <AstrologerCard
          key={expert.id}
          expert={expert}
          featured={index === 0}
          isDefault={expert.id === defaultAstrologerId}
          onClick={() => onSelectAstrologer(expert)}
        />
      ))}
    </div>
  )
}




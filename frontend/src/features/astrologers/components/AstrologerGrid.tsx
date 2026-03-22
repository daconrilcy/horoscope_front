import type { Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import { AstrologerCard } from "./AstrologerCard"

type AstrologerGridProps = {
  astrologers: Astrologer[]
  onSelectAstrologer: (astrologer: Astrologer) => void
}

export function AstrologerGrid({ astrologers, onSelectAstrologer }: AstrologerGridProps) {
  const lang = detectLang()

  if (astrologers.length === 0) {
    return (
      <div className="astrologer-grid-empty">
        <span className="astrologer-grid-empty-icon" role="img" aria-label={t("aria_star", lang)}>
          ⭐
        </span>
        <p>{t("empty_state", lang)}</p>
      </div>
    )
  }

  return (
    <div className="astrologer-grid">
      {astrologers.map((astrologer, index) => (
        <AstrologerCard
          key={astrologer.id}
          astrologer={astrologer}
          featured={index === 0}
          onClick={() => onSelectAstrologer(astrologer)}
        />
      ))}
    </div>
  )
}




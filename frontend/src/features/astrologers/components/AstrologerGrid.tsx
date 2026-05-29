// Rend la grille catalogue des astrologues sans hierarchie artificielle de carte.
import type { Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import {
  type AstrologerIntentKey,
  isAstrologerMatchingIntent,
  isAstrologerRecommendedStarter,
} from "../astrologerPositioning"
import { AstrologerCard } from "./AstrologerCard"

type AstrologerGridProps = {
  experts: Astrologer[]
  onSelectAstrologer: (expert: Astrologer) => void
  onStartAstrologer?: (expert: Astrologer) => void
  defaultAstrologerId?: string | null
  selectedIntent?: AstrologerIntentKey | null
  showProfileCta?: boolean
  selectionMode?: boolean
  selectionLabel?: string
}

/** Rend la liste catalogue ou son etat vide actionnable selon les donnees disponibles. */
export function AstrologerGrid({
  experts,
  onSelectAstrologer,
  onStartAstrologer,
  defaultAstrologerId,
  selectedIntent = null,
  showProfileCta = false,
  selectionMode = false,
  selectionLabel,
}: AstrologerGridProps) {
  const lang = detectLang()

  if (experts.length === 0) {
    return (
      <div className="person-grid-empty">
        <span className="person-grid-empty-icon" role="img" aria-label={t("aria_star", lang)}>
          ⭐
        </span>
        <strong>{t("empty_state_title", lang)}</strong>
        <p>{t("empty_state", lang)}</p>
        <span>{t("empty_state_next_action", lang)}</span>
      </div>
    )
  }

  return (
    <div className="person-grid">
      {experts.map((expert) => (
        <AstrologerCard
          key={expert.id}
          expert={expert}
          isDefault={expert.id === defaultAstrologerId || isAstrologerRecommendedStarter(expert)}
          isIntentMatch={selectedIntent !== null && isAstrologerMatchingIntent(expert, selectedIntent)}
          showProfileCta={showProfileCta}
          selectionMode={selectionMode}
          selectionLabel={selectionLabel}
          onClick={() => onSelectAstrologer(expert)}
          onStart={onStartAstrologer === undefined ? undefined : () => onStartAstrologer(expert)}
        />
      ))}
    </div>
  )
}




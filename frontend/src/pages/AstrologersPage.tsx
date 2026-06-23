// Compose la route catalogue des astrologues et ses etats de chargement.
import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"

import { useAstrologers } from "@hooks/useAstrologers"
import { useUserSettings } from "@api/userSettings"
import { AstrologerGrid } from "../features/astrologers"
import {
  ASTROLOGER_INTENT_OPTIONS,
  type AstrologerIntentKey,
  isAstrologerMatchingIntent,
} from "../features/astrologers/astrologerPositioning"
import { detectLang } from "../i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import type { Astrologer } from "@api"
import { PageLayout } from "../layouts"

const ASTROLOGERS_ROTATION_STORAGE_KEY = "experts_rotation_index_v1"

/** Alterne l'ordre d'affichage pour repartir l'exposition des guides. */
function rotateAstrologers(experts: Astrologer[], rotationIndex: number): Astrologer[] {
  if (experts.length <= 1) {
    return experts
  }

  const safeIndex = ((rotationIndex % experts.length) + experts.length) % experts.length
  if (safeIndex === 0) {
    return experts
  }

  return [...experts.slice(safeIndex), ...experts.slice(0, safeIndex)]
}

/** Remonte les guides alignes avec l'intention sans masquer les autres choix. */
function orientAstrologersByIntent(
  experts: Astrologer[],
  selectedIntent: AstrologerIntentKey | null,
): Astrologer[] {
  if (selectedIntent === null) {
    return experts
  }

  return [...experts].sort((current, next) => {
    const currentMatch = isAstrologerMatchingIntent(current, selectedIntent)
    const nextMatch = isAstrologerMatchingIntent(next, selectedIntent)

    return Number(nextMatch) - Number(currentMatch)
  })
}

/** Compose la page catalogue protegee et sa navigation vers les profils astrologues. */
export function AstrologersPage() {
  const navigate = useNavigate()
  const { astrologers, isLoading, error } = useAstrologers()
  const { data: preferences } = useUserSettings()
  const lang = detectLang()
  const [selectedIntent, setSelectedIntent] = useState<AstrologerIntentKey | null>(null)
  const [rotationIndex] = useState(() => {
    if (typeof window === "undefined") {
      return 0
    }

    const storedValue = window.localStorage.getItem(ASTROLOGERS_ROTATION_STORAGE_KEY)
    const parsedValue = storedValue ? Number.parseInt(storedValue, 10) : 0
    return Number.isFinite(parsedValue) ? parsedValue : 0
  })

  useEffect(() => {
    if (typeof window === "undefined" || astrologers.length <= 1) {
      return
    }

    const nextIndex = (rotationIndex + 1) % astrologers.length
    window.localStorage.setItem(ASTROLOGERS_ROTATION_STORAGE_KEY, String(nextIndex))
  }, [astrologers.length, rotationIndex])

  const displayedAstrologers = useMemo(
    () => orientAstrologersByIntent(rotateAstrologers(astrologers, rotationIndex), selectedIntent),
    [astrologers, rotationIndex, selectedIntent]
  )

  const handleSelectAstrologer = (expert: Astrologer) => {
    navigate(`/astrologers/${encodeURIComponent(expert.id)}`)
  }

  const handleStartAstrologer = (expert: Astrologer) => {
    navigate(`/natal?personaId=${encodeURIComponent(expert.id)}`)
  }

  const handleIntentClick = (intentKey: AstrologerIntentKey) => {
    setSelectedIntent((currentIntent) => (currentIntent === intentKey ? null : intentKey))
  }

  const pageHeader = (
    <header className="people-page-header">
      <h1>{t("page_title", lang)}</h1>
      <p>{t("page_subtitle", lang)}</p>
    </header>
  )

  return (
    <PageLayout className="app-panel people-page" header={pageHeader}>
      {isLoading && (
        <div className="people-page-loading state-centered">{t("loading", lang)}</div>
      )}

      {error && (
        <div className="people-page-error notice">
          {t("error_loading", lang)}
        </div>
      )}

      {!isLoading && !error && (
        <>
          <section className="people-page-guide" aria-labelledby="people-page-guide-title">
            <div className="people-page-guide-copy">
              <h2 id="people-page-guide-title">{t("choice_guide_title", lang)}</h2>
              <p>{t("choice_guide_subtitle", lang)}</p>
            </div>
            <div className="people-page-intents" role="group" aria-label={t("intent_group_label", lang)}>
              {ASTROLOGER_INTENT_OPTIONS.map((intent) => {
                const isActive = selectedIntent === intent.key

                return (
                  <button
                    key={intent.key}
                    type="button"
                    className={`people-page-intent${isActive ? " people-page-intent--active" : ""}`}
                    aria-pressed={isActive}
                    onClick={() => handleIntentClick(intent.key)}
                  >
                    {t(intent.labelKey, lang)}
                  </button>
                )
              })}
            </div>
          </section>
          <AstrologerGrid
            experts={displayedAstrologers}
            onSelectAstrologer={handleSelectAstrologer}
            onStartAstrologer={handleStartAstrologer}
            defaultAstrologerId={preferences?.default_astrologer_id}
            selectedIntent={selectedIntent}
            showProfileCta
          />
        </>
      )}
    </PageLayout>
  )
}


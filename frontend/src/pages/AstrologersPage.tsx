// Compose la route catalogue des astrologues et ses etats de chargement.
import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"

import { useAstrologers } from "@hooks/useAstrologers"
import { useUserSettings } from "@api/userSettings"
import { AstrologerGrid } from "../features/astrologers"
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

/** Compose la page catalogue protegee et sa navigation vers les profils astrologues. */
export function AstrologersPage() {
  const navigate = useNavigate()
  const { astrologers, isLoading, error } = useAstrologers()
  const { data: preferences } = useUserSettings()
  const lang = detectLang()
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
    () => rotateAstrologers(astrologers, rotationIndex),
    [astrologers, rotationIndex]
  )

  const handleSelectAstrologer = (expert: Astrologer) => {
    navigate(`/astrologers/${encodeURIComponent(expert.id)}`)
  }

  const pageHeader = (
    <header className="people-page-header">
      <h1>{t("page_title", lang)}</h1>
      <p>{t("page_subtitle", lang)}</p>
      <ul className="people-page-choice-list" aria-label={t("choice_criteria_label", lang)}>
        <li>{t("choice_criterion_identity", lang)}</li>
        <li>{t("choice_criterion_method", lang)}</li>
        <li>{t("choice_criterion_action", lang)}</li>
      </ul>
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
        <AstrologerGrid
          experts={displayedAstrologers}
          onSelectAstrologer={handleSelectAstrologer}
          defaultAstrologerId={preferences?.default_astrologer_id}
          showProfileCta
        />
      )}
    </PageLayout>
  )
}


import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"

import { useAstrologers } from "@hooks/useAstrologers"
import { useUserSettings } from "@api/userSettings"
import { AstrologerGrid } from "../features/astrologers"
import { detectLang } from "../i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import type { Astrologer } from "@api"
import { PageLayout } from "../layouts"

const ASTROLOGERS_ROTATION_STORAGE_KEY = "astrologers_rotation_index_v1"

function rotateAstrologers(astrologers: Astrologer[], rotationIndex: number): Astrologer[] {
  if (astrologers.length <= 1) {
    return astrologers
  }

  const safeIndex = ((rotationIndex % astrologers.length) + astrologers.length) % astrologers.length
  if (safeIndex === 0) {
    return astrologers
  }

  return [...astrologers.slice(safeIndex), ...astrologers.slice(0, safeIndex)]
}

export function AstrologersPage() {
  const navigate = useNavigate()
  const { astrologers, isLoading, error } = useAstrologers()
  const { data: settings } = useUserSettings()
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

  const handleSelectAstrologer = (astrologer: Astrologer) => {
    navigate(`/astrologers/${encodeURIComponent(astrologer.id)}`)
  }

  return (
    <PageLayout className="panel astrologers-page">
      <div className="astrologers-page-shell">
        <header className="astrologers-page-header">
          <h1>{t("page_title", lang)}</h1>
          <p>{t("page_subtitle", lang)}</p>
        </header>

        {isLoading && (
          <div className="astrologers-page-loading">{t("loading", lang)}</div>
        )}

        {error && (
          <div className="astrologers-page-error">
            {t("error_loading", lang)}
          </div>
        )}

        {!isLoading && !error && (
          <AstrologerGrid
            astrologers={displayedAstrologers}
            onSelectAstrologer={handleSelectAstrologer}
            defaultAstrologerId={settings?.default_astrologer_id}
          />
        )}
      </div>
    </PageLayout>
  )
}


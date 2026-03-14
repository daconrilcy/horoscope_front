import { useNavigate } from "react-router-dom"

import { useAstrologers } from "@hooks/useAstrologers"
import { AstrologerGrid } from "../features/astrologers"
import { detectLang } from "../i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import type { Astrologer } from "@api"

export function AstrologersPage() {
  const navigate = useNavigate()
  const { astrologers, isLoading, error } = useAstrologers()
  const lang = detectLang()

  const handleSelectAstrologer = (astrologer: Astrologer) => {
    navigate(`/astrologers/${encodeURIComponent(astrologer.id)}`)
  }

  return (
    <div className="panel">
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
          astrologers={astrologers}
          onSelectAstrologer={handleSelectAstrologer}
        />
      )}
    </div>
  )
}


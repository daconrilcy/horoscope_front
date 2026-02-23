import { useNavigate } from "react-router-dom"

import { useAstrologers, type Astrologer } from "../api/astrologers"
import { AstrologerGrid } from "../features/astrologers"
import { detectLang } from "../i18n/astrology"
import { t } from "../i18n/astrologers"

export function AstrologersPage() {
  const navigate = useNavigate()
  const { data: astrologers, isPending, error } = useAstrologers()
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

      {isPending && (
        <div className="astrologers-page-loading">{t("loading", lang)}</div>
      )}

      {error && (
        <div className="astrologers-page-error">
          {t("error_loading", lang)}
        </div>
      )}

      {!isPending && !error && (
        <AstrologerGrid
          astrologers={astrologers ?? []}
          onSelectAstrologer={handleSelectAstrologer}
        />
      )}
    </div>
  )
}

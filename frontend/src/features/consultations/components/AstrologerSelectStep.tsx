import { useAstrologers, type Astrologer } from "../../../api/astrologers"
import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/consultations"
import { AUTO_ASTROLOGER_ID } from "../../../types/consultation"
import { classNames } from "../../../utils/classNames"

type AstrologerSelectStepProps = {
  selectedId: string | null
  onSelect: (id: string) => void
}

export function AstrologerSelectStep({
  selectedId,
  onSelect,
}: AstrologerSelectStepProps) {
  const lang = detectLang()
  const { data: astrologers, isPending, error } = useAstrologers()

  return (
    <div className="wizard-step">
      <h2 className="wizard-step-title">{t("select_astrologer", lang)}</h2>

      <button
        type="button"
        className={classNames(
          "astrologer-option",
          "astrologer-option--auto",
          selectedId === AUTO_ASTROLOGER_ID && "astrologer-option--selected"
        )}
        onClick={() => onSelect(AUTO_ASTROLOGER_ID)}
        aria-pressed={selectedId === AUTO_ASTROLOGER_ID}
      >
        <span className="astrologer-option-icon" aria-hidden="true">
          ✨
        </span>
        <span className="astrologer-option-label">{t("auto_astrologer", lang)}</span>
      </button>

      {isPending && (
        <div className="wizard-loading" aria-live="polite">{t("loading", lang)}</div>
      )}

      {error && (
        <div className="wizard-error" role="alert" aria-live="assertive">
          {t("error_loading_astrologers", lang)}
        </div>
      )}

      {!isPending && !error && astrologers && (
        <div className="astrologer-select-grid">
          {astrologers.map((astrologer: Astrologer) => {
            const isSelected = selectedId === astrologer.id

            return (
              <button
                key={astrologer.id}
                type="button"
                className={classNames(
                  "astrologer-option",
                  isSelected && "astrologer-option--selected"
                )}
                onClick={() => onSelect(astrologer.id)}
                aria-pressed={isSelected}
              >
                <div className="astrologer-option-avatar">
                  {astrologer.avatar_url ? (
                    <img
                      src={astrologer.avatar_url}
                      alt=""
                      className="astrologer-option-avatar-img"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement
                        target.style.display = "none"
                      }}
                    />
                  ) : (
                    <span className="astrologer-option-avatar-fallback">✨</span>
                  )}
                </div>
                <div className="astrologer-option-info">
                  <span className="astrologer-option-name">{astrologer.name}</span>
                  <span className="astrologer-option-style">{astrologer.style}</span>
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

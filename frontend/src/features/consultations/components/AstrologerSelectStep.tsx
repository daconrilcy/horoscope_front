import { useAstrologers, type Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import { AUTO_ASTROLOGER_ID } from "@app-types/consultation"
import { classNames } from "@utils/classNames"

type AstrologerSelectStepProps = {
  selectedId: string | null
  onSelect: (id: string) => void
}

export function AstrologerSelectStep({
  selectedId,
  onSelect,
}: AstrologerSelectStepProps) {
  const lang = detectLang()
  const { data: astrologers, isPending, error, refetch, isFetching } = useAstrologers()
  const hasSelectableAstrologers = Boolean(astrologers && astrologers.length > 0)

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

      {error && !hasSelectableAstrologers && (
        <div className="wizard-error" role="alert" aria-live="assertive">
          <p>{t("error_loading_astrologers", lang)}</p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => void refetch()}
            disabled={isFetching}
          >
            {t("retry_loading_astrologers", lang)}
          </button>
        </div>
      )}

      {!isPending && hasSelectableAstrologers && astrologers && (
        <div className="astrologer-select-grid">
          {astrologers.map((astrologer: Astrologer) => {
            const isSelected = selectedId === astrologer.id
            const fullName =
              [astrologer.first_name, astrologer.last_name].filter(Boolean).join(" ") ||
              astrologer.name

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
                  <span className="astrologer-option-name">{fullName}</span>
                  <span className="astrologer-option-style">{astrologer.style}</span>
                </div>
              </button>
            )
          })}
        </div>
      )}

      {!isPending && !error && !hasSelectableAstrologers && (
        <div className="wizard-error" role="status" aria-live="polite">
          <p>{t("no_astrologers_available", lang)}</p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => void refetch()}
            disabled={isFetching}
          >
            {t("retry_loading_astrologers", lang)}
          </button>
        </div>
      )}
    </div>
  )
}







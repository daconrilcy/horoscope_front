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
  const { data: experts, isPending, error, refetch, isFetching } = useAstrologers()
  const hasSelectableAstrologers = Boolean(experts && experts.length > 0)

  return (
    <div className="flow-step">
      <h2 className="flow-step-title">{t("select_astrologer_step_title", lang)}</h2>

      <button
        type="button"
        className={classNames(
          "person-option",
          "person-option--auto",
          selectedId === AUTO_ASTROLOGER_ID && "person-option--selected"
        )}
        onClick={() => onSelect(AUTO_ASTROLOGER_ID)}
        aria-pressed={selectedId === AUTO_ASTROLOGER_ID}
      >
        <span className="person-option-icon" aria-hidden="true">
          ✨
        </span>
        <span className="person-option-label">{t("auto_astrologer", lang)}</span>
      </button>

      {isPending && (
        <div className="flow-loading" aria-live="polite">{t("loading", lang)}</div>
      )}

      {error && !hasSelectableAstrologers && (
        <div className="flow-error" role="alert" aria-live="assertive">
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

      {!isPending && hasSelectableAstrologers && experts && (
        <div className="person-select-grid">
          {experts.map((expert: Astrologer) => {
            const isSelected = selectedId === expert.id
            const fullName =
              [expert.first_name, expert.last_name].filter(Boolean).join(" ") ||
              expert.name

            return (
              <button
                key={expert.id}
                type="button"
                className={classNames(
                  "person-option",
                  isSelected && "person-option--selected"
                )}
                onClick={() => onSelect(expert.id)}
                aria-pressed={isSelected}
              >
                <div className="person-option-avatar">
                  {expert.avatar_url ? (
                    <img
                      src={expert.avatar_url}
                      alt=""
                      className="person-option-avatar-img"
                      onError={(e) => {
                        e.currentTarget.hidden = true
                      }}
                    />
                  ) : (
                    <span className="person-option-avatar-fallback">✨</span>
                  )}
                </div>
                <div className="person-option-info">
                  <span className="person-option-name">{fullName}</span>
                  <span className="person-option-style">{expert.style}</span>
                </div>
              </button>
            )
          })}
        </div>
      )}

      {!isPending && !error && !hasSelectableAstrologers && (
        <div className="flow-error" role="status" aria-live="polite">
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







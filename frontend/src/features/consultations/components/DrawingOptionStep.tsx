import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/consultations"
import { DRAWING_OPTIONS, type DrawingOption } from "../../../types/consultation"
import { classNames } from "../../../utils/classNames"

type DrawingOptionStepProps = {
  selectedOption: DrawingOption
  onSelect: (option: DrawingOption) => void
}

export function DrawingOptionStep({
  selectedOption,
  onSelect,
}: DrawingOptionStepProps) {
  const lang = detectLang()
  return (
    <div className="wizard-step">
      <h2 className="wizard-step-title">{t("select_drawing", lang)}</h2>
      <div className="drawing-option-grid">
        {DRAWING_OPTIONS.map((option) => {
          const isSelected = selectedOption === option.id

          return (
            <button
              key={option.id}
              type="button"
              className={classNames(
                "drawing-option-card",
                isSelected && "drawing-option-card--selected"
              )}
              onClick={() => onSelect(option.id)}
              aria-pressed={isSelected}
            >
              <span className="drawing-option-icon" aria-hidden="true">
                {option.icon}
              </span>
              <span className="drawing-option-label">{t(option.labelKey, lang)}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

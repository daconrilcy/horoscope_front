import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/consultations"
import { CONSULTATION_TYPES, type ConsultationType } from "../../../types/consultation"
import { classNames } from "../../../utils/classNames"

type ConsultationTypeStepProps = {
  selectedType: ConsultationType | null
  onSelect: (type: ConsultationType) => void
}

export function ConsultationTypeStep({
  selectedType,
  onSelect,
}: ConsultationTypeStepProps) {
  const lang = detectLang()
  return (
    <div className="wizard-step">
      <h2 className="wizard-step-title">{t("select_type", lang)}</h2>
      <div className="consultation-type-grid">
        {CONSULTATION_TYPES.map((typeConfig) => {
          const isSelected = selectedType === typeConfig.id

          return (
            <button
              key={typeConfig.id}
              type="button"
              className={classNames(
                "consultation-type-card",
                isSelected && "consultation-type-card--selected"
              )}
              onClick={() => onSelect(typeConfig.id)}
              aria-pressed={isSelected}
            >
              <span className="consultation-type-icon" aria-hidden="true">
                {typeConfig.icon}
              </span>
              <span className="consultation-type-label">
                {t(typeConfig.labelKey, lang)}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

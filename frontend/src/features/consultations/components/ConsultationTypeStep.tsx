import { detectLang } from "@i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import { type ConsultationType } from "@app-types/consultation"
import { classNames } from "@utils/classNames"
import { useConsultationCatalogue } from "@api/consultations"

type ConsultationTypeStepProps = {
  selectedType: ConsultationType | null
  onSelect: (type: ConsultationType) => void
}

export function ConsultationTypeStep({
  selectedType,
  onSelect,
}: ConsultationTypeStepProps) {
  const lang = detectLang()
  const { data: catalogue, isLoading } = useConsultationCatalogue()

  if (isLoading) {
    return (
      <div className="wizard-step">
        <h2 className="wizard-step-title">{t("select_type", lang)}</h2>
        <div className="state-line state-loading">{t("loading", lang)}</div>
      </div>
    )
  }

  return (
    <div className="wizard-step">
      <h2 className="wizard-step-title">{t("select_type", lang)}</h2>
      <div className="consultation-type-grid">
        {catalogue?.items.map((item) => {
          const isSelected = selectedType === item.key

          return (
            <button
              key={item.key}
              type="button"
              className={classNames(
                "consultation-type-card",
                isSelected && "consultation-type-card--selected"
              )}
              onClick={() => onSelect(item.key as ConsultationType)}
              aria-pressed={isSelected}
            >
              <span className="consultation-type-icon" aria-hidden="true">
                {item.icon_ref}
              </span>
              <span className="consultation-type-label">
                {item.title}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

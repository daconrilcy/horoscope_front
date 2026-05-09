import { detectLang } from "@i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import { CONSULTATION_TYPES, type ConsultationType } from "@app-types/consultation"
import { classNames } from "@utils/classNames"
import { useConsultationCatalogue } from "@api/consultations"

type ConsultationTypeStepProps = {
  selectedType: ConsultationType | null
  onSelect: (type: ConsultationType) => void
}

const FALLBACK_ITEMS = CONSULTATION_TYPES.map((c) => ({
  key: c.id,
  icon_ref: c.icon,
  title: c.labelKey,
}))

export function ConsultationTypeStep({
  selectedType,
  onSelect,
}: ConsultationTypeStepProps) {
  const lang = detectLang()
  const { data: catalogue, isLoading, isError } = useConsultationCatalogue()

  if (isLoading) {
    return (
      <div className="activity-type-step">
        <h2 className="flow-step-title">{t("select_type", lang)}</h2>
        <div className="app-state app-state--loading">{t("loading", lang)}</div>
      </div>
    )
  }

  const items = catalogue?.items?.length
    ? catalogue.items
    : FALLBACK_ITEMS.map((f) => ({
        key: f.key,
        icon_ref: f.icon_ref,
        title: t(f.title, lang) || f.title,
        subtitle: "",
        description: "",
        metadata_config: {},
        sort_order: 0,
      }))

  return (
    <div className="activity-type-step">
      <h2 className="flow-step-title">{t("select_type", lang)}</h2>
      {isError && !catalogue && (
        <p className="app-state app-state--error">{t("catalogue_error", lang)}</p>
      )}
      <div className="activity-type-grid">
        {items.map((item) => {
          const isSelected = selectedType === item.key

          return (
            <button
              key={item.key}
              type="button"
              className={classNames(
                "activity-type-card",
                isSelected && "activity-type-card--selected"
              )}
              onClick={() => onSelect(item.key as ConsultationType)}
              aria-pressed={isSelected}
            >
              <span className="activity-type-icon" aria-hidden="true">
                {item.icon_ref}
              </span>
              <span className="activity-type-label">
                {item.title}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

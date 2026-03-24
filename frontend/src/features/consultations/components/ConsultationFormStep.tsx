import { detectLang } from "@i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import {
  CONSULTATION_TYPES,
  CONTEXT_MAX_LENGTH,
  type ConsultationDraft,
  type ConsultationType,
  type OtherPersonDraft,
  getObjectiveForType,
} from "@app-types/consultation"
import { useConsultationCatalogue } from "@api/consultations"
import { OtherPersonForm } from "./OtherPersonForm"

type ConsultationFormStepProps = {
  draft: ConsultationDraft
  showTypeSelector?: boolean
  onTypeChange: (type: ConsultationType, objective: string) => void
  onContextChange: (context: string) => void
  onObjectiveChange: (objective: string) => void
  onTimeHorizonChange: (horizon: string | null) => void
  onToggleThirdParty: (active: boolean) => void
  onOtherPersonChange: (data: OtherPersonDraft | null) => void
  saveOptIn?: boolean
  onSaveOptInChange?: (checked: boolean) => void
  nickname?: string
  onNicknameChange?: (nickname: string) => void
  onSelectedExistingChange?: (externalId: string | null) => void
}

const FALLBACK_ITEMS = CONSULTATION_TYPES.filter((c) => !c.isLegacy).map((c) => ({
  key: c.id as ConsultationType,
  icon: c.icon,
  labelKey: c.labelKey,
  objectiveKey: c.objectiveKey,
}))

export function ConsultationFormStep({
  draft,
  showTypeSelector = true,
  onTypeChange,
  onContextChange,
  onObjectiveChange,
  onTimeHorizonChange,
  onToggleThirdParty,
  onOtherPersonChange,
  saveOptIn,
  onSaveOptInChange,
  nickname,
  onNicknameChange,
  onSelectedExistingChange,
}: ConsultationFormStepProps) {
  const lang = detectLang()
  const { data: catalogue } = useConsultationCatalogue()

  const typeItems = catalogue?.items?.length
    ? catalogue.items.map((i) => ({
        key: i.key as ConsultationType,
        icon: i.icon_ref,
        label: i.title,
        objectiveKey: null as string | null,
      }))
    : FALLBACK_ITEMS.map((i) => ({
        key: i.key,
        icon: i.icon,
        label: t(i.labelKey, lang),
        objectiveKey: i.objectiveKey,
      }))

  const handleTypeSelect = (item: (typeof typeItems)[number]) => {
    const catalogueItem = catalogue?.items.find((i) => i.key === item.key)
    const objective = catalogueItem?.title ?? t(getObjectiveForType(item.key), lang)
    onTypeChange(item.key, objective)
  }

  return (
    <div className="consultation-form-step">
      <h2 className="wizard-step-title">
        {!showTypeSelector && draft.type
          ? typeItems.find((i) => i.key === draft.type)?.label ?? t("form_step_title", lang)
          : t("form_step_title", lang)}
      </h2>

      {/* Type selection — uniquement si non pré-sélectionné depuis le catalogue */}
      {showTypeSelector && (
        <div className="form-group">
          <label className="form-label">{t("select_type", lang)}</label>
          <div className="consultation-type-pills">
            {typeItems.map((item) => (
              <button
                key={item.key}
                type="button"
                className={`type-pill${draft.type === item.key ? " type-pill--selected" : ""}`}
                onClick={() => handleTypeSelect(item)}
                aria-pressed={draft.type === item.key}
              >
                <span className="type-pill-icon" aria-hidden="true">
                  {item.icon}
                </span>
                <span className="type-pill-label">{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Context */}
      <div className="form-group">
        <label htmlFor="form-context" className="form-label">
          {t("enter_context", lang)}
        </label>
        <textarea
          id="form-context"
          className="validation-context-input"
          value={draft.context}
          onChange={(e) => onContextChange(e.target.value)}
          placeholder={t("context_placeholder", lang)}
          rows={5}
          maxLength={CONTEXT_MAX_LENGTH}
          aria-describedby="form-context-counter"
        />
        <div id="form-context-counter" className="validation-context-counter">
          {CONTEXT_MAX_LENGTH - draft.context.length} {t("context_max_length_hint", lang)}
        </div>
      </div>

      {/* Time horizon */}
      <div className="form-group">
        <label htmlFor="form-horizon" className="form-label">
          {t("time_horizon_label", lang)}
        </label>
        <input
          id="form-horizon"
          className="validation-context-input"
          type="text"
          value={draft.timeHorizon ?? ""}
          onChange={(e) => onTimeHorizonChange(e.target.value || null)}
          placeholder={t("time_horizon_placeholder", lang)}
        />
        <p className="validation-context-hint">{t("time_horizon_hint", lang)}</p>
      </div>

      {/* Third party toggle */}
      <div className="form-group form-group--third-party-toggle">
        <div className="checkbox-label">
          <input
            id="form-third-party"
            type="checkbox"
            checked={!!draft.isInteraction}
            onChange={(e) => {
              onToggleThirdParty(e.target.checked)
              if (!e.target.checked) {
                onOtherPersonChange(null)
              }
            }}
          />
          <label htmlFor="form-third-party">{t("add_third_party_label", lang)}</label>
        </div>
        <p className="validation-context-hint">{t("add_third_party_hint", lang)}</p>
      </div>

      {/* Third party form */}
      {draft.isInteraction && (
        <div className="form-group">
          <OtherPersonForm
            value={draft.otherPerson ?? null}
            onChange={onOtherPersonChange}
            saveOptIn={saveOptIn}
            onSaveOptInChange={onSaveOptInChange}
            nickname={nickname}
            onNicknameChange={onNicknameChange}
            onSelectedExistingChange={onSelectedExistingChange}
          />
        </div>
      )}
    </div>
  )
}

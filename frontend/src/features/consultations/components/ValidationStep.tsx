import { useMemo } from "react"
import { useAstrologer } from "../../../api/astrologers"
import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/consultations"
import {
  AUTO_ASTROLOGER_ID,
  CONTEXT_MAX_LENGTH,
  WIZARD_STEP_LABELS,
  getConsultationTypeConfig,
  getDrawingOptionConfig,
  type ConsultationDraft,
} from "../../../types/consultation"

type ValidationStepProps = {
  draft: ConsultationDraft
  context: string
  onContextChange: (context: string) => void
}

export function ValidationStep({
  draft,
  context,
  onContextChange,
}: ValidationStepProps) {
  const lang = detectLang()
  const astrologerId = draft.astrologerId === AUTO_ASTROLOGER_ID ? undefined : draft.astrologerId ?? undefined
  const { data: astrologer } = useAstrologer(astrologerId)
  const astrologerName = draft.astrologerId === AUTO_ASTROLOGER_ID 
    ? t("auto_astrologer", lang) 
    : astrologer?.name ?? t("loading_name", lang)

  const typeConfig = useMemo(
    () => (draft.type ? getConsultationTypeConfig(draft.type) : undefined),
    [draft.type]
  )

  const drawingConfig = useMemo(
    () => getDrawingOptionConfig(draft.drawingOption),
    [draft.drawingOption]
  )

  return (
    <div className="wizard-step">
      <h2 className="wizard-step-title">{t("summary_title", lang)}</h2>

      <div className="validation-summary">
        <div className="validation-item">
          <span className="validation-label">{t(WIZARD_STEP_LABELS.type, lang)}:</span>
          <span className="validation-value">
            {typeConfig && t(typeConfig.labelKey, lang)}
          </span>
        </div>
        <div className="validation-item">
          <span className="validation-label">{t(WIZARD_STEP_LABELS.astrologer, lang)}:</span>
          <span className="validation-value">{astrologerName}</span>
        </div>
        <div className="validation-item">
          <span className="validation-label">{t(WIZARD_STEP_LABELS.drawing, lang)}:</span>
          <span className="validation-value">
            {t(drawingConfig?.labelKey ?? "", lang)}
          </span>
        </div>
      </div>

      <div className="validation-context">
        <label htmlFor="consultation-context" className="validation-context-label">
          {t("enter_context", lang)}
        </label>
        <textarea
          id="consultation-context"
          className="validation-context-input"
          value={context}
          onChange={(e) => onContextChange(e.target.value)}
          placeholder={t("context_placeholder", lang)}
          rows={4}
          maxLength={CONTEXT_MAX_LENGTH}
          aria-describedby="consultation-context-counter"
        />
        <div id="consultation-context-counter" className="validation-context-counter">
          {CONTEXT_MAX_LENGTH - context.length} {t("context_max_length_hint", lang)}
        </div>
      </div>
    </div>
  )
}

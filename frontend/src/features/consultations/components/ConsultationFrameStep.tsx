import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/consultations"
import { CONTEXT_MAX_LENGTH, type ConsultationDraft } from "../../../types/consultation"

type ConsultationFrameStepProps = {
  draft: ConsultationDraft
  onContextChange: (context: string) => void
  onObjectiveChange: (objective: string) => void
  onTimeHorizonChange: (timeHorizon: string) => void
}

export function ConsultationFrameStep({
  draft,
  onContextChange,
  onObjectiveChange,
  onTimeHorizonChange,
}: ConsultationFrameStepProps) {
  const lang = detectLang()

  return (
    <div className="wizard-step">
      <h2 className="wizard-step-title">{t("frame_step_title", lang)}</h2>

      <div className="validation-context">
        <label htmlFor="consultation-objective" className="validation-context-label">
          {t("objective_label", lang)}
        </label>
        <input
          id="consultation-objective"
          className="validation-context-input"
          type="text"
          value={draft.objective ?? ""}
          onChange={(e) => onObjectiveChange(e.target.value)}
          placeholder={t("objective_placeholder", lang)}
        />

        <label htmlFor="consultation-context" className="validation-context-label">
          {t("enter_context", lang)}
        </label>
        <textarea
          id="consultation-context"
          className="validation-context-input"
          value={draft.context}
          onChange={(e) => onContextChange(e.target.value)}
          placeholder={t("context_placeholder", lang)}
          rows={4}
          maxLength={CONTEXT_MAX_LENGTH}
          aria-describedby="consultation-context-counter"
        />
        <div id="consultation-context-counter" className="validation-context-counter">
          {CONTEXT_MAX_LENGTH - draft.context.length} {t("context_max_length_hint", lang)}
        </div>

        <label htmlFor="consultation-time-horizon" className="validation-context-label">
          {t("time_horizon_label", lang)}
        </label>
        <input
          id="consultation-time-horizon"
          className="validation-context-input"
          type="text"
          value={draft.timeHorizon ?? ""}
          onChange={(e) => onTimeHorizonChange(e.target.value)}
          placeholder={t("time_horizon_placeholder", lang)}
        />
        <p className="validation-context-hint">{t("time_horizon_hint", lang)}</p>
      </div>
    </div>
  )
}

import { detectLang } from "@i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import { CONTEXT_MAX_LENGTH, INTERACTION_ELIGIBLE_TYPES, type ConsultationDraft } from "@app-types/consultation"

type ConsultationFrameStepProps = {
  draft: ConsultationDraft
  onContextChange: (context: string) => void
  onObjectiveChange: (objective: string) => void
  onTimeHorizonChange: (timeHorizon: string) => void
  onInteractionToggle?: (isInteraction: boolean) => void
}

export function ConsultationFrameStep({
  draft,
  onContextChange,
  onObjectiveChange,
  onTimeHorizonChange,
  onInteractionToggle,
}: ConsultationFrameStepProps) {
  const lang = detectLang()
  const isInteractionEligible = draft.type && INTERACTION_ELIGIBLE_TYPES.includes(draft.type)
  const isRelationshipType = draft.type === "relationship"

  return (
    <div className="flow-step">
      <h2 className="flow-step-title">{t("frame_step_title", lang)}</h2>

      <div className="validation-context">
        <label htmlFor="activity-objective" className="validation-context-label">
          {t("objective_label", lang)}
        </label>
        <input
          id="activity-objective"
          className="validation-context-input"
          type="text"
          value={draft.objective ?? ""}
          onChange={(e) => onObjectiveChange(e.target.value)}
          placeholder={t("objective_placeholder", lang)}
        />

        <label htmlFor="activity-context" className="validation-context-label">
          {t("enter_context", lang)}
        </label>
        <textarea
          id="activity-context"
          className="validation-context-input"
          value={draft.context}
          onChange={(e) => onContextChange(e.target.value)}
          placeholder={t("context_placeholder", lang)}
          rows={4}
          maxLength={CONTEXT_MAX_LENGTH}
          aria-describedby="activity-context-counter"
        />
        <div id="activity-context-counter" className="validation-context-counter">
          {CONTEXT_MAX_LENGTH - draft.context.length} {t("context_max_length_hint", lang)}
        </div>

        <label htmlFor="activity-time-horizon" className="validation-context-label">
          {t("time_horizon_label", lang)}
        </label>
        <input
          id="activity-time-horizon"
          className="validation-context-input"
          type="text"
          value={draft.timeHorizon ?? ""}
          onChange={(e) => onTimeHorizonChange(e.target.value)}
          placeholder={t("time_horizon_placeholder", lang)}
        />
        <p className="validation-context-hint">{t("time_horizon_hint", lang)}</p>

        {isInteractionEligible && !isRelationshipType && onInteractionToggle && (
          <div className="interaction-toggle-section">
            <div className="checkbox-label">
              <input
                id="activity-is-interaction"
                type="checkbox"
                checked={!!draft.isInteraction}
                onChange={(e) => onInteractionToggle(e.target.checked)}
              />
              <label htmlFor="activity-is-interaction">
                {t("is_interaction_label", lang)}
              </label>
            </div>
            <p className="interaction-toggle-hint">{t("is_interaction_hint", lang)}</p>
          </div>
        )}
      </div>
    </div>
  )
}





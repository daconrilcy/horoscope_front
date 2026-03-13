import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/consultations"
import { type ConsultationDraft, getConsultationTypeConfig } from "../../../types/consultation"
import { type ConsultationPrecheckData } from "../../../api/consultations"
import { AstrologerSelectStep } from "./AstrologerSelectStep"

type ConsultationSummaryStepProps = {
  draft: ConsultationDraft
  precheck: ConsultationPrecheckData | null
  onAstrologerSelect: (id: string) => void
}

export function ConsultationSummaryStep({
  draft,
  precheck,
  onAstrologerSelect,
}: ConsultationSummaryStepProps) {
  const lang = detectLang()
  const typeConfig = draft.type ? getConsultationTypeConfig(draft.type) : null

  return (
    <div className="wizard-step">
      <h2 className="wizard-step-title">{t("summary_step_title", lang)}</h2>

      <div className="summary-details">
        <div className="summary-item">
          <span className="summary-label">{t("type_label", lang)}:</span>
          <span className="summary-value">
            {typeConfig ? t(typeConfig.labelKey, lang) : draft.type}
          </span>
        </div>
        <div className="summary-item">
          <span className="summary-label">{t("objective_label", lang)}:</span>
          <span className="summary-value">{draft.objective}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">{t("horizon_label", lang)}:</span>
          <span className="summary-value">{draft.timeHorizon || t("not_specified", lang)}</span>
        </div>
        {draft.otherPerson && (
          <div className="summary-item">
            <span className="summary-label">{t("other_person_label", lang)}:</span>
            <span className="summary-value">
              {draft.otherPerson.birthPlace} ({draft.otherPerson.birthDate})
            </span>
          </div>
        )}
      </div>

      <div className="summary-precheck">
        <h3 className="summary-subtitle">{t("expected_quality_title", lang)}</h3>
        {precheck ? (
          <div className="precheck-status">
            <p className={`precision-badge precision-badge--${precheck.precision_level}`}>
              {t(`precision_${precheck.precision_level}`, lang)}
            </p>
            {precheck.status === "blocked" && (
              <p className="error-message">{t("blocked_reason_generic", lang)}</p>
            )}
          </div>
        ) : (
          <p>{t("precheck_not_available", lang)}</p>
        )}
      </div>

      <div className="summary-astrologer">
        <h3 className="summary-subtitle">{t("choose_astrologer_optional", lang)}</h3>
        <AstrologerSelectStep
          selectedId={draft.astrologerId}
          onSelect={onAstrologerSelect}
        />
      </div>
    </div>
  )
}

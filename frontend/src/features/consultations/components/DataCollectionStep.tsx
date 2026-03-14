import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/consultations"
import { type ConsultationDraft, type OtherPersonDraft } from "../../../types/consultation"
import { type ConsultationPrecheckData } from "../../../api/consultations"
import { OtherPersonForm } from "./OtherPersonForm"
import { Link } from "react-router-dom"

type DataCollectionStepProps = {
  draft: ConsultationDraft
  precheck: ConsultationPrecheckData | null
  onOtherPersonChange: (data: OtherPersonDraft | null) => void
  saveOptIn?: boolean
  onSaveOptInChange?: (checked: boolean) => void
  nickname?: string
  onNicknameChange?: (nickname: string) => void
}

export function DataCollectionStep({
  draft,
  precheck,
  onOtherPersonChange,
  saveOptIn,
  onSaveOptInChange,
  nickname,
  onNicknameChange,
}: DataCollectionStepProps) {
  const lang = detectLang()

  const isUserMissingData = precheck?.user_profile_quality === "missing" || precheck?.user_profile_quality === "incomplete"
  const isInteractionPath = draft.type === "relation" || draft.isInteraction

  return (
    <div className="wizard-step">
      <h2 className="wizard-step-title">{t("collection_step_title", lang)}</h2>

      {precheck && (
        <div className="precheck-summary">
          <p className={`precision-badge precision-badge--${precheck.precision_level}`}>
            {t(`precision_${precheck.precision_level}`, lang)}
          </p>
          {precheck.status === "degraded" && (
            <p className="degraded-warning">
              {t("degraded_mode_info", lang)}: {t(precheck.fallback_mode ?? "", lang)}
            </p>
          )}
        </div>
      )}

      {isUserMissingData && (
        <div className="user-data-missing-notice">
          <p>{t("user_data_missing_hint", lang)}</p>
          <Link to="/profile" className="btn btn-secondary">
            {t("complete_my_profile", lang)}
          </Link>
        </div>
      )}

      {isInteractionPath && (
        <div className="relation-data-collection">
          <OtherPersonForm
            value={draft.otherPerson ?? null}
            onChange={onOtherPersonChange}
            saveOptIn={saveOptIn}
            onSaveOptInChange={onSaveOptInChange}
            nickname={nickname}
            onNicknameChange={onNicknameChange}
          />
        </div>
      )}

      {!isUserMissingData && !isInteractionPath && (
        <div className="nothing-to-collect">
          <p>{t("no_extra_data_needed", lang)}</p>
        </div>
      )}
    </div>
  )
}

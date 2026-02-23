import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/consultations"
import { WIZARD_STEPS, WIZARD_STEP_LABELS, type WizardStep } from "../../../types/consultation"
import { classNames } from "../../../utils/classNames"

type WizardProgressProps = {
  currentStepName: WizardStep
}

export function WizardProgress({ currentStepName }: WizardProgressProps) {
  const lang = detectLang()
  const currentStepIndex = WIZARD_STEPS.indexOf(currentStepName)

  return (
    <nav className="wizard-progress" aria-label={t("wizard_progress_aria", lang)}>
      <ol className="wizard-progress-list">
        {WIZARD_STEPS.map((step, index) => {
          const isCompleted = index < currentStepIndex
          const isCurrent = step === currentStepName

          return (
            <li
              key={step}
              className={classNames(
                "wizard-progress-step",
                isCompleted && "wizard-progress-step--completed",
                isCurrent && "wizard-progress-step--current"
              )}
              aria-current={isCurrent ? "step" : undefined}
            >
              <span className="wizard-progress-number" aria-hidden="true">
                {isCompleted ? "✓" : index + 1}
              </span>
              <span className="wizard-progress-label">{t(WIZARD_STEP_LABELS[step], lang)}</span>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

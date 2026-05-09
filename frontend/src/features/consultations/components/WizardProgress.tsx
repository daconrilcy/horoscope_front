import { detectLang } from "@i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import { WIZARD_STEPS, WIZARD_STEP_LABELS, type WizardStep } from "@app-types/consultation"
import { classNames } from "@utils/classNames"

type WizardProgressProps = {
  currentStepName: WizardStep
}

export function WizardProgress({ currentStepName }: WizardProgressProps) {
  const lang = detectLang()
  const currentStepIndex = WIZARD_STEPS.indexOf(currentStepName)

  return (
    <nav className="flow-progress" aria-label={t("flow_progress_aria", lang)}>
      <ol className="flow-progress-list">
        {WIZARD_STEPS.map((step, index) => {
          const isCompleted = index < currentStepIndex
          const isCurrent = step === currentStepName

          return (
            <li
              key={step}
              className={classNames(
                "flow-progress-step",
                isCompleted && "flow-progress-step--completed",
                isCurrent && "flow-progress-step--current"
              )}
              aria-current={isCurrent ? "step" : undefined}
            >
              <span className="flow-progress-number" aria-hidden="true">
                {isCompleted ? "✓" : index + 1}
              </span>
              <span className="flow-progress-label">{t(WIZARD_STEP_LABELS[step], lang)}</span>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}






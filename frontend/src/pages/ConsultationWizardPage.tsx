import { useEffect, useCallback } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"

import { useConsultation } from "../state/consultationStore"
import {
  ConsultationTypeStep,
  AstrologerSelectStep,
  DrawingOptionStep,
  ValidationStep,
  WizardProgress,
} from "../features/consultations"
import { detectLang } from "../i18n/astrology"
import { t } from "../i18n/consultations"
import { VALID_CONSULTATION_TYPES, type ConsultationType, type DrawingOption } from "../types/consultation"

export function ConsultationWizardPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const lang = detectLang()

  const {
    state,
    setType,
    setAstrologer,
    setDrawingOption,
    setContext,
    nextStep,
    prevStep,
    reset,
    canProceed,
    currentStepName,
  } = useConsultation()

  useEffect(() => {
    const typeParam = searchParams.get("type")
    if (typeParam && currentStepName === "type" && state.draft.type === null) {
      if (VALID_CONSULTATION_TYPES.includes(typeParam as ConsultationType)) {
        setType(typeParam as ConsultationType)
      }
    }
  }, [searchParams, currentStepName, state.draft.type, setType])

  const handleCancel = useCallback(() => {
    reset()
    navigate("/consultations")
  }, [reset, navigate])

  const handleNext = useCallback(() => {
    if (canProceed) {
      nextStep()
    }
  }, [canProceed, nextStep])

  const handleGenerate = useCallback(() => {
    if (canProceed) {
      navigate("/consultations/result")
    }
  }, [canProceed, navigate])

  const handleTypeSelect = useCallback((type: ConsultationType) => {
    setType(type)
    nextStep()
  }, [setType, nextStep])

  const handleAstrologerSelect = useCallback((id: string) => {
    setAstrologer(id)
    nextStep()
  }, [setAstrologer, nextStep])

  const handleDrawingSelect = useCallback((option: DrawingOption) => {
    setDrawingOption(option)
    nextStep()
  }, [setDrawingOption, nextStep])

  const renderStep = () => {
    switch (currentStepName) {
      case "type":
        return (
          <ConsultationTypeStep
            selectedType={state.draft.type}
            onSelect={handleTypeSelect}
          />
        )
      case "astrologer":
        return (
          <AstrologerSelectStep
            selectedId={state.draft.astrologerId}
            onSelect={handleAstrologerSelect}
          />
        )
      case "drawing":
        return (
          <DrawingOptionStep
            selectedOption={state.draft.drawingOption}
            onSelect={handleDrawingSelect}
          />
        )
      case "validation":
        return (
          <ValidationStep
            draft={state.draft}
            context={state.draft.context}
            onContextChange={setContext}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="panel consultation-wizard-page">
      <WizardProgress currentStepName={currentStepName} />

      <div className="wizard-content">{renderStep()}</div>

      <div className="wizard-actions">
        <button type="button" className="btn btn-secondary" onClick={handleCancel}>
          {t("cancel", lang)}
        </button>

        <div className="wizard-actions-nav">
          {currentStepName !== "type" && (
            <button type="button" className="btn btn-secondary" onClick={prevStep}>
              {t("previous", lang)}
            </button>
          )}

          {currentStepName !== "validation" && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleNext}
              disabled={!canProceed}
            >
              {t("next", lang)}
            </button>
          )}

          {currentStepName === "validation" && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={!canProceed}
            >
              {t("generate", lang)}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

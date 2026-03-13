import { useEffect, useCallback } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"

import { useConsultation } from "../state/consultationStore"
import {
  ConsultationTypeStep,
  AstrologerSelectStep,
  ValidationStep,
  WizardProgress,
} from "../features/consultations"
import { detectLang } from "../i18n/astrology"
import { t } from "../i18n/consultations"
import {
  VALID_CREATABLE_TYPES,
  getObjectiveForType,
  type ConsultationType,
} from "../types/consultation"
import { useConsultationPrecheck } from "../api/consultations"

export function ConsultationWizardPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const lang = detectLang()
  const { mutate: runPrecheck, isPending: isPrechecking } = useConsultationPrecheck()

  const {
    state,
    setType,
    setAstrologer,
    setContext,
    setObjective,
    setTimeHorizon,
    setPrecheck,
    nextStep,
    prevStep,
    reset,
    canProceed,
    currentStepName,
  } = useConsultation()

  useEffect(() => {
    const typeParam = searchParams.get("type")
    if (typeParam && currentStepName === "type" && state.draft.type === null) {
      if (VALID_CREATABLE_TYPES.includes(typeParam as ConsultationType)) {
        const selectedType = typeParam as ConsultationType
        setType(selectedType)
        setObjective(t(getObjectiveForType(selectedType), lang))
        
        runPrecheck({ consultation_type: selectedType }, {
          onSuccess: (response) => {
            setPrecheck(response.data)
          }
        })
      }
    }
  }, [searchParams, currentStepName, state.draft.type, setType, setObjective, lang, runPrecheck, setPrecheck])

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
    setObjective(t(getObjectiveForType(type), lang))
    setTimeHorizon(null)
    setPrecheck(null) // Reset precheck for new type
    
    runPrecheck({ consultation_type: type }, {
      onSuccess: (response) => {
        setPrecheck(response.data)
      }
    })
    
    nextStep()
  }, [setType, setObjective, setTimeHorizon, setPrecheck, runPrecheck, nextStep, lang])

  const handleAstrologerSelect = useCallback((id: string) => {
    setAstrologer(id)
    nextStep()
  }, [setAstrologer, nextStep])

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
      case "validation":
        return (
          <ValidationStep
            draft={state.draft}
            context={state.draft.context}
            objective={state.draft.objective ?? ""}
            timeHorizon={state.draft.timeHorizon ?? ""}
            onContextChange={setContext}
            onObjectiveChange={setObjective}
            onTimeHorizonChange={(value) => setTimeHorizon(value)}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="panel consultation-wizard-page">
      <WizardProgress currentStepName={currentStepName} />

      <div className="wizard-content">
        {isPrechecking && (
          <div className="wizard-loading-overlay">
            <span className="spinner" aria-hidden="true">⌛</span>
            <p>{t("precheck_loading", lang)}</p>
          </div>
        )}
        {renderStep()}
      </div>

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
              disabled={!canProceed || isPrechecking}
            >
              {t("next", lang)}
            </button>
          )}

          {currentStepName === "validation" && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={!canProceed || isPrechecking || state.precheck?.status === "blocked"}
            >
              {t("generate", lang)}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

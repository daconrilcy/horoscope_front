import { useEffect, useCallback } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"

import { useConsultation } from "../state/consultationStore"
import {
  ConsultationTypeStep,
  ConsultationFrameStep,
  DataCollectionStep,
  ConsultationSummaryStep,
  WizardProgress,
  ConsultationFallbackBanner,
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
    setOtherPerson,
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
      if (currentStepName === "frame") {
        runPrecheck({ 
          consultation_type: state.draft.type!, 
          question: state.draft.context,
          horizon: state.draft.timeHorizon ?? undefined
        }, {
          onSuccess: (response) => {
            setPrecheck(response.data)
          }
        })
      }
      if (currentStepName === "collection" && state.draft.otherPerson) {
        runPrecheck({
          consultation_type: state.draft.type!,
          question: state.draft.context,
          horizon: state.draft.timeHorizon ?? undefined,
          other_person: {
            birth_date: state.draft.otherPerson.birthDate,
            birth_time: state.draft.otherPerson.birthTime ?? undefined,
            birth_time_known: state.draft.otherPerson.birthTimeKnown,
            birth_place: state.draft.otherPerson.birthPlace
          }
        }, {
          onSuccess: (response) => {
            setPrecheck(response.data)
          }
        })
      }
      nextStep()
    }
  }, [canProceed, currentStepName, nextStep, runPrecheck, state.draft, setPrecheck])

  const handleGenerate = useCallback(() => {
    if (canProceed) {
      navigate("/consultations/result")
    }
  }, [canProceed, navigate])

  const handleTypeSelect = useCallback((type: ConsultationType) => {
    setType(type)
    setObjective(t(getObjectiveForType(type), lang))
    setTimeHorizon(null)
    setOtherPerson(null)
    setPrecheck(null)
    
    runPrecheck({ consultation_type: type }, {
      onSuccess: (response) => {
        setPrecheck(response.data)
      }
    })
    
    nextStep()
  }, [setType, setObjective, setTimeHorizon, setOtherPerson, setPrecheck, runPrecheck, nextStep, lang])

  const renderStep = () => {
    switch (currentStepName) {
      case "type":
        return (
          <ConsultationTypeStep
            selectedType={state.draft.type}
            onSelect={handleTypeSelect}
          />
        )
      case "frame":
        return (
          <ConsultationFrameStep
            draft={state.draft}
            onContextChange={setContext}
            onObjectiveChange={setObjective}
            onTimeHorizonChange={setTimeHorizon}
          />
        )
      case "collection":
        return (
          <DataCollectionStep
            draft={state.draft}
            precheck={state.precheck}
            onOtherPersonChange={setOtherPerson}
          />
        )
      case "summary":
        return (
          <ConsultationSummaryStep
            draft={state.draft}
            precheck={state.precheck}
            onAstrologerSelect={setAstrologer}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="panel consultation-wizard-page">
      <WizardProgress currentStepName={currentStepName} />

      {state.precheck && currentStepName === "summary" && (
        <ConsultationFallbackBanner precheck={state.precheck} />
      )}

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

          {currentStepName !== "summary" && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleNext}
              disabled={!canProceed || isPrechecking}
            >
              {t("next", lang)}
            </button>
          )}

          {currentStepName === "summary" && (
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

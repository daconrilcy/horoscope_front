import { WizardLayout } from "../layouts"
import { useEffect, useCallback, useRef } from "react"
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
import { tConsultations as t } from "@i18n/consultations"
import {
  VALID_CREATABLE_TYPES,
  getObjectiveForType,
  mapLegacyConsultationKey,
  type ConsultationType,
} from "../types/consultation"
import { useConsultationPrecheck, useConsultationCatalogue } from "../api/consultations"
import { trackEvent, EVENTS } from "../utils/analytics"

export function ConsultationWizardPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const lang = detectLang()
  const { mutate: runPrecheck, isPending: isPrechecking } = useConsultationPrecheck()
  const { data: catalogue } = useConsultationCatalogue()
  const initializedTypeParamRef = useRef<string | null>(null)

  const {
    state,
    setType,
    setAstrologer,
    setContext,
    setObjective,
    setTimeHorizon,
    setOtherPerson,
    setIsInteraction,
    setSaveThirdParty,
    setThirdPartyNickname,
    setSelectedThirdPartyExternalId,
    setPrecheck,
    nextStep,
    prevStep,
    goToStep,
    reset,
    canProceed,
    currentStepName,
  } = useConsultation()

  const startConsultationForType = useCallback(
    (type: ConsultationType, advanceToNextStep: boolean) => {
      const astrologerIdFromQuery = searchParams.get("astrologerId")
      
      // AC2: Normalisation des clés legacy (work -> career, etc.)
      const canonicalType = mapLegacyConsultationKey(type)
      
      reset()
      setType(canonicalType)
      setAstrologer(astrologerIdFromQuery || "auto")
      setContext("")
      
      // AC1.7: Utilisation des micro-textes pilotés par la base si disponibles
      const template = catalogue?.items.find(i => i.key === canonicalType)
      setObjective(template?.title ?? t(getObjectiveForType(canonicalType), lang))
      
      setTimeHorizon(null)
      setOtherPerson(null)
      setPrecheck(null)

      trackEvent(EVENTS.CONSULTATION_STARTED, { type: canonicalType })

      runPrecheck(
        { consultation_type: canonicalType },
        {
          onSuccess: (response) => {
            setPrecheck(response.data)
            trackEvent(EVENTS.CONSULTATION_PRECHECK, {
              type: canonicalType,
              status: response.data.status,
              precision: response.data.precision_level,
            })
          },
        }
      )

      if (advanceToNextStep) {
        goToStep(1)
      }
    },
    [
      catalogue,
      reset,
      setType,
      setAstrologer,
      setContext,
      setObjective,
      setTimeHorizon,
      setOtherPerson,
      setPrecheck,
      lang,
      runPrecheck,
      goToStep,
      searchParams,
    ]
  )

  useEffect(() => {
    const typeParam = searchParams.get("type")
    if (!typeParam) {
      initializedTypeParamRef.current = null
      return
    }

    if (
      VALID_CREATABLE_TYPES.includes(typeParam as ConsultationType) &&
      initializedTypeParamRef.current !== typeParam
    ) {
      initializedTypeParamRef.current = typeParam
      startConsultationForType(typeParam as ConsultationType, true)
    }
  }, [searchParams, startConsultationForType])

  const handleCancel = useCallback(() => {
    reset()
    navigate("/consultations")
  }, [reset, navigate])

  const handlePrev = useCallback(() => {
    if (currentStepName === "frame" && searchParams.get("type")) {
      // L'utilisateur est arrivé via ?type=xxxx depuis /consultations
      // Retour à la page catalogue plutôt qu'à l'étape de sélection interne
      reset()
      navigate("/consultations")
    } else {
      prevStep()
    }
  }, [currentStepName, searchParams, reset, navigate, prevStep])

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
            birth_place: state.draft.otherPerson.birthPlace,
            birth_city: state.draft.otherPerson.birthCity,
            birth_country: state.draft.otherPerson.birthCountry,
            ...(state.draft.otherPerson.placeResolvedId
              ? { place_resolved_id: state.draft.otherPerson.placeResolvedId }
              : {}),
            ...(state.draft.otherPerson.birthLat !== null &&
            state.draft.otherPerson.birthLat !== undefined
              ? { birth_lat: state.draft.otherPerson.birthLat }
              : {}),
            ...(state.draft.otherPerson.birthLon !== null &&
            state.draft.otherPerson.birthLon !== undefined
              ? { birth_lon: state.draft.otherPerson.birthLon }
              : {}),
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
    startConsultationForType(type, true)
  }, [startConsultationForType])

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
            onInteractionToggle={setIsInteraction}
          />
        )
      case "collection":
        return (
          <DataCollectionStep
            draft={state.draft}
            precheck={state.precheck}
            onOtherPersonChange={setOtherPerson}
            saveOptIn={state.draft.saveThirdParty}
            onSaveOptInChange={setSaveThirdParty}
            nickname={state.draft.thirdPartyNickname}
            onNicknameChange={setThirdPartyNickname}
            onSelectedExistingChange={setSelectedThirdPartyExternalId}
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
      <WizardLayout
        customProgress={<WizardProgress currentStepName={currentStepName} />}
        onBack={currentStepName !== "type" ? handlePrev : undefined}
      >
        {state.precheck && currentStepName === "summary" && (
          <ConsultationFallbackBanner precheck={state.precheck} />
        )}

        <div className="wizard-content">
          {isPrechecking && (currentStepName === "collection" || currentStepName === "summary") && (
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
              <button type="button" className="btn btn-secondary" onClick={handlePrev}>
                {t("previous", lang)}
              </button>
            )}

            {currentStepName !== "summary" && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleNext}
                disabled={!canProceed}
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
      </WizardLayout>
    </div>
  )
}

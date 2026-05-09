import { WizardLayout } from "../layouts"
import { useEffect, useCallback, useRef } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"

import { useConsultation } from "../state/consultationStore"
import {
  AstrologerSelectStep,
  ConsultationFormStep,
  WizardProgress,
} from "../features/consultations"
import { detectLang } from "../i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import {
  VALID_CREATABLE_TYPES,
  AUTO_ASTROLOGER_ID,
  getObjectiveForType,
  type ConsultationType,
} from "../types/consultation"
import { useConsultationCatalogue } from "../api/consultations"
import { useAstrologer } from "../api/astrologers"
import { trackEvent, EVENTS } from "../utils/analytics"

function SelectedAstrologerCard({
  astrologerId,
  lang,
}: {
  astrologerId: string
  lang: ReturnType<typeof detectLang>
}) {
  const isAuto = astrologerId === AUTO_ASTROLOGER_ID
  const { data: expert } = useAstrologer(isAuto ? undefined : astrologerId)

  const name = isAuto
    ? t("auto_astrologer", lang)
    : expert
      ? [expert.first_name, expert.last_name].filter(Boolean).join(" ") || expert.name
      : t("loading_name", lang)

  return (
    <div className="flow-person-card">
      <div className="flow-person-card__avatar">
        {!isAuto && expert?.avatar_url ? (
          <img src={expert.avatar_url} alt="" className="flow-person-card__avatar-img" />
        ) : (
          <span className="flow-person-card__avatar-icon" aria-hidden="true">✨</span>
        )}
      </div>
      <div className="flow-person-card__info">
        <span className="flow-person-card__name">{name}</span>
        {!isAuto && expert?.style && (
          <span className="flow-person-card__style">{expert.style}</span>
        )}
      </div>
    </div>
  )
}

export function ConsultationWizardPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const lang = detectLang()
  const { data: catalogue } = useConsultationCatalogue()
  const initializedRef = useRef(false)
  const typePreselectedRef = useRef(false)
  const expertChosenRef = useRef(false)

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
    goToStep,
    reset,
    canProceed,
    currentStepName,
  } = useConsultation()

  // Initialize from URL params on first load
  useEffect(() => {
    if (initializedRef.current) return

    const astrologerIdFromQuery = searchParams.get("astrologerId")
    const typeParam = searchParams.get("type")

    if (!astrologerIdFromQuery && !typeParam) return

    initializedRef.current = true
    reset()

    if (typeParam && VALID_CREATABLE_TYPES.includes(typeParam as ConsultationType)) {
      const canonicalType = typeParam as ConsultationType
      setType(canonicalType)
      const template = catalogue?.items.find((i) => i.key === canonicalType)
      setObjective(template?.title ?? t(getObjectiveForType(canonicalType), lang))
      typePreselectedRef.current = true
    }

    if (astrologerIdFromQuery) {
      setAstrologer(astrologerIdFromQuery)
      expertChosenRef.current = true
      // Venant d'une page astrologue : l'astrologue est déjà choisi, on saute à la page 2
      goToStep(1)
    }
  }, [searchParams, catalogue, reset, setAstrologer, setType, setObjective, goToStep, lang])

  const handleBackToConsultations = useCallback(() => {
    reset()
    navigate("/consultations")
  }, [reset, navigate])

  // Sélection d'astrologue : enregistre + avance automatiquement à l'étape suivante
  const handleAstrologerSelect = useCallback(
    (id: string) => {
      setAstrologer(id)
      expertChosenRef.current = true
      goToStep(1)
    },
    [setAstrologer, goToStep]
  )

  const handlePrevFromForm = useCallback(() => {
    goToStep(0)
  }, [goToStep])

  const handleGenerate = useCallback(() => {
    if (!canProceed) return
    trackEvent(EVENTS.CONSULTATION_STARTED, { type: state.draft.type })
    navigate("/consultations/result")
  }, [canProceed, state.draft.type, navigate])

  const handleCancel = useCallback(() => {
    reset()
    navigate("/consultations")
  }, [reset, navigate])

  const handleTypeChange = useCallback(
    (type: ConsultationType, objective: string) => {
      setType(type)
      setObjective(objective)
    },
    [setType, setObjective]
  )

  const showAstrologerCard = expertChosenRef.current

  const renderStep = () => {
    switch (currentStepName) {
      case "astrologer":
        return (
          <AstrologerSelectStep
            selectedId={state.draft.astrologerId}
            onSelect={handleAstrologerSelect}
          />
        )
      case "form":
        return (
          <ConsultationFormStep
            draft={state.draft}
            showTypeSelector={!typePreselectedRef.current}
            onTypeChange={handleTypeChange}
            onContextChange={setContext}
            onObjectiveChange={setObjective}
            onTimeHorizonChange={setTimeHorizon}
            onToggleThirdParty={setIsInteraction}
            onOtherPersonChange={setOtherPerson}
            saveOptIn={state.draft.saveThirdParty}
            onSaveOptInChange={setSaveThirdParty}
            nickname={state.draft.thirdPartyNickname ?? undefined}
            onNicknameChange={setThirdPartyNickname}
            onSelectedExistingChange={setSelectedThirdPartyExternalId}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="app-panel activity-flow-page">
      <WizardLayout
        customProgress={<WizardProgress currentStepName={currentStepName} />}
        onBack={handleBackToConsultations}
      >
        {showAstrologerCard && (
          <SelectedAstrologerCard astrologerId={state.draft.astrologerId} lang={lang} />
        )}

        <div className="flow-content">
          {renderStep()}
        </div>

        <div className="flow-actions">
          <button type="button" className="btn btn-secondary" onClick={handleCancel}>
            {t("cancel", lang)}
          </button>

          <div className="flow-actions-nav">
            {currentStepName === "form" && (
              <button type="button" className="btn btn-secondary" onClick={handlePrevFromForm}>
                {t("previous", lang)}
              </button>
            )}

            {currentStepName === "form" && (
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
      </WizardLayout>
    </div>
  )
}

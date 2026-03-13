import { useEffect, useState, useCallback, useRef, useMemo } from "react"
import { useNavigate, useSearchParams, Link } from "react-router-dom"

import { useConsultation, CHAT_PREFILL_KEY } from "../state/consultationStore"
import { useConsultationGenerate, type ConsultationPrecheckData } from "../api/consultations"
import { useAstrologer } from "../api/astrologers"
import { detectLang } from "../i18n/astrology"
import { t } from "../i18n/consultations"
import { 
  AUTO_ASTROLOGER_ID, 
  WIZARD_STEP_LABELS, 
  getConsultationTypeConfig, 
  getObjectiveForType, 
  type ConsultationResult 
} from "../types/consultation"
import { ConsultationFallbackBanner } from "../features/consultations"
import { classNames } from "../utils/classNames"

function resolveObjectiveText(
  objective: string | undefined,
  type: ConsultationResult["type"],
  lang: ReturnType<typeof detectLang>
): string {
  if (objective && !objective.startsWith("objective_")) {
    return objective
  }
  return t(getObjectiveForType(type), lang)
}

export function ConsultationResultPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const lang = detectLang()

  const { state, setResult, saveToHistory, reset } = useConsultation()
  const consultationGenerate = useConsultationGenerate()

  const [error, setError] = useState<string | null>(null)

  const historyId = searchParams.get("id")
  const currentResult: ConsultationResult | undefined = historyId
    ? state.history.find((h) => h.id === historyId)
    : state.result ?? undefined

  const isAlreadyInHistory = historyId !== null && currentResult !== undefined
  const [isSaved, setIsSaved] = useState(isAlreadyInHistory)

  const astrologerId =
    currentResult?.astrologerId === AUTO_ASTROLOGER_ID
      ? undefined
      : currentResult?.astrologerId
  const { data: astrologer } = useAstrologer(astrologerId)
  const astrologerName =
    currentResult?.astrologerId === AUTO_ASTROLOGER_ID
      ? t("auto_astrologer", lang)
      : astrologer?.name ?? t("loading_name", lang)

  const draftType = state.draft.type
  const draftAstrologerId = state.draft.astrologerId
  const draftContext = state.draft.context
  const draftObjective = state.draft.objective
  const draftTimeHorizon = state.draft.timeHorizon
  const draftOtherPerson = state.draft.otherPerson
  const generationStarted = useRef(false)

  const typeConfig = useMemo(
    () => (currentResult ? getConsultationTypeConfig(currentResult.type) : undefined),
    [currentResult]
  )
  const currentObjective = useMemo(
    () =>
      currentResult
        ? resolveObjectiveText(currentResult.objective, currentResult.type, lang)
        : "",
    [currentResult, lang]
  )

  const resultPrecheck = useMemo<ConsultationPrecheckData | null>(() => {
    if (!currentResult?.fallbackMode && !currentResult?.precisionLevel) return null
    return {
      consultation_type: currentResult.type,
      status: currentResult.fallbackMode ? "degraded" : "nominal",
      precision_level: (currentResult.precisionLevel as any) || "high",
      fallback_mode: currentResult.fallbackMode as any,
      user_profile_quality: "complete",
      missing_fields: [],
      available_modes: [],
      blocking_reasons: []
    }
  }, [currentResult])

  const generateInterpretation = useCallback(async () => {
    if (draftType === null || draftAstrologerId === null) {
      navigate("/consultations/new")
      return
    }

    setError(null)

    try {
      const objective = resolveObjectiveText(draftObjective, draftType, lang)
      const timeHorizon = draftTimeHorizon?.trim() ? draftTimeHorizon.trim() : null
      
      const payload = {
        consultation_type: draftType,
        question: draftContext,
        horizon: timeHorizon ?? undefined,
        astrologer_id: draftAstrologerId,
        other_person: draftOtherPerson ? {
          birth_date: draftOtherPerson.birthDate,
          birth_time: draftOtherPerson.birthTime ?? undefined,
          birth_time_known: draftOtherPerson.birthTimeKnown,
          birth_place: draftOtherPerson.birthPlace
        } : undefined
      }

      const response = await consultationGenerate.mutateAsync(payload)
      const data = response.data

      const result: ConsultationResult = {
        id: data.consultation_id,
        type: data.consultation_type as any,
        astrologerId: draftAstrologerId,
        context: draftContext,
        objective,
        timeHorizon,
        summary: data.summary,
        keyPoints: data.sections.find(s => s.id === "key_points")?.content.split("\n") || [],
        actionableAdvice: data.sections.find(s => s.id === "advice")?.content.split("\n") || [],
        createdAt: new Date().toISOString(),
        fallbackMode: data.fallback_mode,
        precisionLevel: data.precision_level,
        sections: data.sections,
        routeKey: data.route_key
      }

      setResult(result)
    } catch (err: any) {
      setError(err.message || t("error_generation", lang))
    }
  }, [
    draftType,
    draftAstrologerId,
    draftContext,
    draftObjective,
    draftTimeHorizon,
    draftOtherPerson,
    consultationGenerate,
    setResult,
    navigate,
    lang,
  ])

  useEffect(() => {
    if (!historyId && !state.result && draftType !== null && !generationStarted.current) {
      generationStarted.current = true
      void generateInterpretation()
    }
  }, [historyId, state.result, draftType, generateInterpretation])

  const handleSave = useCallback(() => {
    if (currentResult) {
      saveToHistory(currentResult)
      setIsSaved(true)
    }
  }, [currentResult, saveToHistory])

  const handleOpenInChat = useCallback(() => {
    if (currentResult) {
      const interpretation = currentResult.summary || ""
      const timeHorizonBlock = currentResult.timeHorizon
        ? `\n${t("time_horizon_summary_label", lang)}: ${currentResult.timeHorizon}`
        : ""
      const message =
        `[Consultation ${t(typeConfig?.labelKey ?? "", lang)}]\n\n` +
        `${t("objective_summary_label", lang)}: ${resolveObjectiveText(currentResult.objective, currentResult.type, lang)}${timeHorizonBlock}\n\n` +
        `${currentResult.context}\n\n${t("interpretation_label", lang)}:\n${interpretation}`
      sessionStorage.setItem(CHAT_PREFILL_KEY, message)
      reset()
      const astrologerParam = currentResult.astrologerId !== AUTO_ASTROLOGER_ID
        ? `?astrologerId=${currentResult.astrologerId}`
        : ""
      navigate(`/chat${astrologerParam}`)
    }
  }, [currentResult, typeConfig, reset, navigate, lang])

  if (consultationGenerate.isPending) {
    return (
      <div className="panel consultation-result-page">
        <div className="consultation-result-loading" aria-live="polite" aria-busy="true">
          <span className="loading-spinner" />
          <p>{t("generating", lang)}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="panel consultation-result-page">
        <div className="consultation-result-error" role="alert">
          <p>{error}</p>
          <Link to="/consultations/new" className="btn">
            {t("back_to_consultations", lang)}
          </Link>
        </div>
      </div>
    )
  }

  if (!currentResult) {
    return (
      <div className="panel consultation-result-page">
        <div className="consultation-result-empty" aria-live="polite">
          <p>{t("no_history", lang)}</p>
          <Link to="/consultations" className="btn">
            {t("back_to_consultations", lang)}
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="panel consultation-result-page">
      <header className="consultation-result-header">
        <h1>{t("result_title", lang)}</h1>
      </header>

      {resultPrecheck && (
        <ConsultationFallbackBanner precheck={resultPrecheck} />
      )}

      <div className="consultation-result-summary-section">
        <div className="consultation-result-type">
          <span className="consultation-result-type-icon" aria-hidden="true">
            {typeConfig?.icon}
          </span>
          <span className="consultation-result-type-label">
            {t(typeConfig?.labelKey ?? "", lang)}
          </span>
        </div>

        <div className="consultation-result-meta">
          <span className="consultation-result-astrologer">
            {t("step_astrologer", lang)}: {astrologerName}
          </span>
        </div>

        <div className="consultation-result-context">
          <strong>{t("objective_label", lang)}:</strong>
          <p>{currentObjective}</p>
        </div>

        {currentResult.timeHorizon && (
          <div className="consultation-result-context">
            <strong>{t("time_horizon_label", lang)}:</strong>
            <p>{currentResult.timeHorizon}</p>
          </div>
        )}

        <div className="consultation-result-context">
          <strong>{t("enter_context", lang)}:</strong>
          <p>{currentResult.context}</p>
        </div>
      </div>

      <section className="consultation-result-guidance">
        <div className="consultation-result-interpretation">
          <h2>{t("summary_label", lang)}</h2>
          <p className="consultation-result-interpretation-text">
            {currentResult.summary}
          </p>
        </div>

        {currentResult.sections && currentResult.sections.length > 0 ? (
          currentResult.sections.map((section) => (
            <div key={section.id} className={`consultation-result-section consultation-result-section--${section.id}`}>
              <h3>{section.title}</h3>
              <div className="section-content">
                {section.content.split("\n").map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>
          ))
        ) : (
          <>
            {currentResult.keyPoints && currentResult.keyPoints.length > 0 && (
              <div className="consultation-result-key-points">
                <h3>{t("key_points_label", lang)}</h3>
                <ul>
                  {currentResult.keyPoints.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
            )}

            {currentResult.actionableAdvice && currentResult.actionableAdvice.length > 0 && (
              <div className="consultation-result-advice">
                <h3>{t("actionable_advice_label", lang)}</h3>
                <ul>
                  {currentResult.actionableAdvice.map((advice, idx) => (
                    <li key={idx}>{advice}</li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}

        {currentResult.disclaimer && (
          <p className="consultation-result-disclaimer">
            <em>{currentResult.disclaimer}</em>
          </p>
        )}
      </section>

      <div className="consultation-result-actions">
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleOpenInChat}
        >
          {t("open_in_chat", lang)}
        </button>
        <button
          type="button"
          className={classNames("btn", "btn-secondary", isSaved && "btn-success")}
          onClick={handleSave}
          disabled={isSaved}
        >
          {isSaved ? t("saved", lang) : t("save", lang)}
        </button>
        <Link to="/consultations" className="btn btn-secondary">
          {t("back_to_consultations", lang)}
        </Link>
      </div>
    </div>
  )
}

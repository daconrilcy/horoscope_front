import { useEffect, useState, useCallback, useRef, useMemo } from "react"
import { useNavigate, useSearchParams, Link } from "react-router-dom"

import { useConsultation, CHAT_PREFILL_KEY } from "../state/consultationStore"
import { useExecuteModule } from "../api/chat"
import { useAstrologer } from "../api/astrologers"
import { detectLang } from "../i18n/astrology"
import { t } from "../i18n/consultations"
import { AUTO_ASTROLOGER_ID, WIZARD_STEP_LABELS, getConsultationTypeConfig, getDrawingOptionConfig, type ConsultationResult } from "../types/consultation"
import { generateUniqueId } from "../utils/generateUniqueId"
import { generateSimpleInterpretation } from "../utils/generateSimpleInterpretation"
import { classNames } from "../utils/classNames"

export function ConsultationResultPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const lang = detectLang()

  const { state, setResult, saveToHistory, reset } = useConsultation()
  const executeModule = useExecuteModule()

  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const historyId = searchParams.get("id")
  const currentResult = historyId
    ? state.history.find((h) => h.id === historyId)
    : state.result

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
  const draftDrawingOption = state.draft.drawingOption
  const draftContext = state.draft.context
  const generationStarted = useRef(false)

  const typeConfig = useMemo(
    () => (currentResult ? getConsultationTypeConfig(currentResult.type) : undefined),
    [currentResult]
  )

  const drawingOptionConfig = useMemo(
    () => (currentResult ? getDrawingOptionConfig(currentResult.drawingOption) : undefined),
    [currentResult]
  )

  const generateInterpretation = useCallback(async () => {
    if (draftType === null || draftAstrologerId === null) {
      navigate("/consultations/new")
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      let interpretation = ""
      let drawingResult: ConsultationResult["drawing"]

      if (draftDrawingOption !== "none") {
        const moduleResult = await executeModule.mutateAsync({
          module: draftDrawingOption as "tarot" | "runes",
          payload: { question: draftContext },
        })
        interpretation = moduleResult.interpretation
        const drawingLabel = t("drawing_completed", lang)
        drawingResult =
          draftDrawingOption === "tarot"
            ? { cards: [drawingLabel] }
            : { runes: [drawingLabel] }
      } else {
        interpretation = generateSimpleInterpretation(draftContext, lang)
      }

      const result: ConsultationResult = {
        id: generateUniqueId(),
        type: draftType,
        astrologerId: draftAstrologerId,
        drawingOption: draftDrawingOption,
        context: draftContext,
        drawing: drawingResult,
        interpretation,
        createdAt: new Date().toISOString(),
      }

      setResult(result)
    } catch {
      setError(t("error_generation", lang))
    } finally {
      setIsGenerating(false)
    }
  }, [draftType, draftAstrologerId, draftDrawingOption, draftContext, executeModule, setResult, navigate, lang])

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
      const message = `[Consultation ${t(typeConfig?.labelKey ?? "", lang)}]\n\n${currentResult.context}\n\n${t("interpretation_label", lang)}:\n${currentResult.interpretation}`
      sessionStorage.setItem(CHAT_PREFILL_KEY, message)
      reset()
      navigate("/chat")
    }
  }, [currentResult, typeConfig, reset, navigate, lang])

  if (isGenerating) {
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

      <div className="consultation-result-summary">
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
            {t(WIZARD_STEP_LABELS.astrologer, lang)}: {astrologerName}
          </span>
          {currentResult.drawingOption !== "none" && (
            <span className="consultation-result-drawing">
              {t(drawingOptionConfig?.labelKey ?? "", lang)}
            </span>
          )}
        </div>

        <div className="consultation-result-context">
          <strong>{t("enter_context", lang)}:</strong>
          <p>{currentResult.context}</p>
        </div>
      </div>

      {currentResult.drawing && (
        <div className="consultation-result-drawing-section">
          {currentResult.drawing.cards && (
            <div className="consultation-result-cards">
              {currentResult.drawing.cards.map((card, index) => (
                <span key={`card-${index}-${card}`} className="consultation-result-card">
                  🃏 {card}
                </span>
              ))}
            </div>
          )}
          {currentResult.drawing.runes && (
            <div className="consultation-result-runes">
              {currentResult.drawing.runes.map((rune, index) => (
                <span key={`rune-${index}-${rune}`} className="consultation-result-rune">
                  ᚱ {rune}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      <section className="consultation-result-interpretation">
        <h2>{t("interpretation", lang)}</h2>
        <p className="consultation-result-interpretation-text">
          {currentResult.interpretation}
        </p>
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
